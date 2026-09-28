"""Export a Blender primitive blockout as compact Pyglet scene data.

Run this file inside Blender's Scripting workspace, or pass it to Blender's
own Python interpreter with ``blender --background --python``.

The default output is ``<blend-file>.scene.json`` next to the .blend file.
An explicit output path may be placed after ``--``.

Hierarchy convention
--------------------
An EMPTY named ``Body`` with a direct MESH child named ``BodyMesh`` is exported
as one visible node named ``Body``. The EMPTY supplies the animation pivot and
local transform; the MESH supplies its geometry and shape transform. The
generated scene therefore contains no meshless nodes. An EMPTY without a
matching ``<EmptyName>Mesh`` child is omitted and its descendants are attached
to the nearest exported node.

Unpaired meshes are also exported. A trailing ``Mesh`` is removed from their
node name when this does not create a duplicate.

Mesh geometry is inferred from object/data names containing Cube, Box, Sphere,
or Icosphere. It can instead be set with the custom property
``pyglet_geometry`` (normally ``cube`` or ``sphere``). Set ``pyglet_export``
to false to exclude an object.

Transforms are exported as translation, axis-angle rotation (radians), and
scale rather than opaque 4x4 matrices. Blender's Z-up coordinates are
converted to the project's Y-up coordinates.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    import bpy
    from mathutils import Matrix, Vector
except ImportError as exc:  # pragma: no cover - only Blender provides bpy
    raise RuntimeError(
        "Run export_blender_scene.py with Blender's Python interpreter."
    ) from exc


FORMAT_VERSION = 2


def _clean_number(value: float) -> float:
    value = float(value)
    if abs(value) < 5e-7:
        return 0.0
    return round(value, 6)


def _vector_values(vector: Any) -> list[float]:
    return [_clean_number(component) for component in vector]


def _convert_translation(vector: Any) -> Vector:
    """Convert Blender (x, y, z) to project coordinates (x, z, -y)."""

    return Vector((vector.x, vector.z, -vector.y))


def _without_scale(matrix: Matrix) -> Matrix:
    """Keep only translation and rotation from a world transform."""

    location, rotation, _scale = matrix.decompose()
    return Matrix.Translation(location) @ rotation.to_matrix().to_4x4()


def _bounding_box_transform(obj: Any) -> Matrix:
    """Map the unit [-.5, .5] primitive onto a Blender mesh bounding box."""

    corners = [Vector(corner) for corner in obj.bound_box]
    minimum = Vector(
        tuple(min(corner[axis] for corner in corners) for axis in range(3))
    )
    maximum = Vector(
        tuple(max(corner[axis] for corner in corners) for axis in range(3))
    )
    center = (minimum + maximum) * 0.5
    size = maximum - minimum
    return Matrix.Translation(center) @ Matrix.Diagonal(
        (size.x, size.y, size.z, 1.0)
    )


def _transform_components(
    matrix: Matrix,
    description: str,
    warnings: list[str],
) -> dict[str, Any]:
    """Decompose a matrix into values used by Mat4.from_* constructors."""

    translation, rotation, scale = matrix.decompose()
    euler = rotation.to_euler("XYZ")

    reconstructed = (
        Matrix.Translation(translation)
        @ rotation.to_matrix().to_4x4()
        @ Matrix.Diagonal((scale.x, scale.y, scale.z, 1.0))
    )
    maximum_error = max(
        abs(matrix[row][column] - reconstructed[row][column])
        for row in range(4)
        for column in range(4)
    )
    if maximum_error > 1e-5:
        warnings.append(
            f"{description} contains shear; its TRS decomposition is an "
            f"approximation (maximum matrix error {maximum_error:.3g})."
        )

    return {
        "translation": _vector_values(_convert_translation(translation)),
        # Blender XYZ Euler matrices are Rz @ Ry @ Rx. Under the basis
        # conversion, Blender Z becomes project Y and Blender Y becomes
        # project -Z. Negating the Y angle lets us use the positive Z axis.
        "rotations": [
            {"angle": _clean_number(euler.z), "axis": [0.0, 1.0, 0.0]},
            {"angle": _clean_number(-euler.y), "axis": [0.0, 0.0, 1.0]},
            {"angle": _clean_number(euler.x), "axis": [1.0, 0.0, 0.0]},
        ],
        "scale": _vector_values(Vector((scale.x, scale.z, scale.y))),
    }


def _geometry_key(obj: Any) -> str:
    explicit = obj.get("pyglet_geometry")
    if explicit is not None:
        key = str(explicit).strip().lower()
        aliases = {
            "box": "cube",
            "uv_sphere": "sphere",
            "uvsphere": "sphere",
            "ico_sphere": "sphere",
            "icosphere": "sphere",
        }
        return aliases.get(key, key)

    data_name = getattr(obj.data, "name", "")
    searchable_name = f"{obj.name} {data_name}".lower()
    if "cube" in searchable_name or "box" in searchable_name:
        return "cube"
    if "sphere" in searchable_name:
        return "sphere"
    return "unknown"


def _exportable_objects() -> list[Any]:
    return [
        obj
        for obj in bpy.context.scene.objects
        if obj.type in {"EMPTY", "MESH"}
        and bool(obj.get("pyglet_export", True))
    ]


def _paired_mesh(empty: Any, exported_names: set[str]) -> Any | None:
    explicit_name = empty.get("pyglet_mesh")
    expected_name = (
        str(explicit_name).strip()
        if explicit_name is not None
        else f"{empty.name}Mesh"
    )
    matches = [
        child
        for child in empty.children
        if child.name in exported_names
        and child.type == "MESH"
        and child.name.casefold() == expected_name.casefold()
    ]
    if len(matches) > 1:
        raise ValueError(
            f"Empty {empty.name!r} has multiple matching mesh children"
        )
    return matches[0] if matches else None


def _unpaired_mesh_name(mesh: Any) -> str:
    explicit_name = mesh.get("pyglet_node_name")
    if explicit_name is not None:
        name = str(explicit_name).strip()
        if not name:
            raise ValueError(
                f"Mesh {mesh.name!r} has an empty pyglet_node_name property"
            )
        return name

    name = mesh.name
    if name.casefold().endswith("mesh"):
        stripped = name[:-4].rstrip(" _.-")
        if stripped:
            return stripped
    return name


def _logical_records(objects: list[Any]) -> list[dict[str, Any]]:
    exported_names = {obj.name for obj in objects}
    claimed_meshes: set[str] = set()
    records: list[dict[str, Any]] = []

    for obj in objects:
        if obj.type != "EMPTY":
            continue
        mesh = _paired_mesh(obj, exported_names)
        if mesh is None:
            continue
        claimed_meshes.add(mesh.name)
        records.append(
            {
                "name": obj.name,
                "anchor": obj,
                "mesh": mesh,
            }
        )

    for obj in objects:
        if obj.type != "MESH" or obj.name in claimed_meshes:
            continue
        records.append(
            {
                "name": _unpaired_mesh_name(obj),
                "anchor": obj,
                "mesh": obj,
            }
        )

    names = [record["name"] for record in records]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError(
            "Logical node names overlap after removing 'Mesh': "
            f"{duplicates}. Rename the objects or set pyglet_node_name."
        )
    if "root" in names:
        raise ValueError("'root' is reserved by RenderWindow")
    return records


def _logical_parent_names(records: list[dict[str, Any]]) -> dict[str, str | None]:
    owner_by_object: dict[str, str] = {}
    for record in records:
        owner_by_object[record["anchor"].name] = record["name"]
        owner_by_object[record["mesh"].name] = record["name"]

    parent_names: dict[str, str | None] = {}
    for record in records:
        own_name = record["name"]
        ancestor = record["anchor"].parent
        parent_name = None
        while ancestor is not None:
            owner = owner_by_object.get(ancestor.name)
            if owner is not None and owner != own_name:
                parent_name = owner
                break
            ancestor = ancestor.parent
        parent_names[own_name] = parent_name
    return parent_names


def _relative_local_matrix(anchor: Any, parent_anchor: Any | None) -> Matrix:
    """Compose Blender local transforms up to a logical parent.

    EMPTY scale is preserved because Blender propagates it to the entire child
    subtree. A mesh object's own scale is separated later into shape_transform.
    """

    parts: list[Matrix] = []
    current = anchor
    while current is not None and current != parent_anchor:
        local = current.matrix_local.copy()
        parts.append(local)
        current = current.parent

    if parent_anchor is not None and current is None:
        raise ValueError(
            f"{parent_anchor.name!r} is not an ancestor of {anchor.name!r}"
        )

    result = Matrix.Identity(4)
    for local in reversed(parts):
        result = result @ local
    return result


def _order_records(
    records: list[dict[str, Any]],
    parent_names: dict[str, str | None],
) -> list[dict[str, Any]]:
    pending = list(records)
    ordered: list[dict[str, Any]] = []
    available: set[str] = set()

    while pending:
        made_progress = False
        for record in pending[:]:
            parent = parent_names[record["name"]]
            if parent is not None and parent not in available:
                continue
            ordered.append(record)
            available.add(record["name"])
            pending.remove(record)
            made_progress = True

        if not made_progress:
            unresolved = {
                record["name"]: parent_names[record["name"]]
                for record in pending
            }
            raise ValueError(f"Logical scene hierarchy contains a cycle: {unresolved}")

    return ordered


def _output_path_from_arguments() -> Path:
    arguments: list[str] = []
    if "--" in sys.argv:
        arguments = sys.argv[sys.argv.index("--") + 1 :]

    if arguments:
        return Path(bpy.path.abspath(arguments[0])).resolve()
    if bpy.data.filepath:
        return Path(bpy.data.filepath).resolve().with_suffix(".scene.json")
    return Path(bpy.path.abspath("//pigeon_scene.json")).resolve()


def export_scene(output_path: str | Path | None = None) -> Path:
    """Export the active Blender scene and return the written JSON path."""

    path = Path(output_path).resolve() if output_path else _output_path_from_arguments()
    objects = _exportable_objects()
    records = _logical_records(objects)
    parent_names = _logical_parent_names(records)
    ordered_records = _order_records(records, parent_names)
    record_by_name = {record["name"]: record for record in records}

    warnings: list[str] = []
    nodes: list[dict[str, Any]] = []

    for record in ordered_records:
        name = record["name"]
        anchor = record["anchor"]
        mesh = record["mesh"]
        parent_name = parent_names[name]
        parent_anchor = (
            record_by_name[parent_name]["anchor"]
            if parent_name is not None
            else None
        )

        relative_blender = _relative_local_matrix(anchor, parent_anchor)

        if anchor != mesh:
            # The EMPTY's scale is a group transform in Blender, so it belongs
            # in local_transform and must propagate to every descendant.
            local_blender = relative_blender
            # The paired mesh is a direct child of its EMPTY pivot. Its entire
            # local T/R/S therefore belongs to the visible shape.
            shape_blender = mesh.matrix_local @ _bounding_box_transform(mesh)
        else:
            # This scale belongs only to the visible standalone mesh.
            local_blender = _without_scale(relative_blender)
            # An unpaired mesh acts as both joint and shape. Keep its T/R in
            # local_transform and move only its residual size into the shape.
            shape_blender = (
                local_blender.inverted_safe()
                @ relative_blender
                @ _bounding_box_transform(mesh)
            )
        geometry = _geometry_key(mesh)
        if geometry == "unknown":
            warnings.append(
                f"Could not infer geometry for mesh {mesh.name!r}. Set its "
                "custom property 'pyglet_geometry' to 'cube' or 'sphere'."
            )

        nodes.append(
            {
                "name": name,
                "parent": parent_name,
                "geometry": geometry,
                "local_transform": _transform_components(
                    local_blender,
                    f"Node {name!r} local transform",
                    warnings,
                ),
                "shape_transform": _transform_components(
                    shape_blender,
                    f"Node {name!r} shape transform",
                    warnings,
                ),
                "source": {
                    "blender_joint": record["anchor"].name,
                    "blender_mesh": mesh.name,
                    "blender_data": getattr(mesh.data, "name", None),
                },
            }
        )

    document = {
        "format_version": FORMAT_VERSION,
        "coordinate_system": {
            "source": "Blender right-handed Z-up",
            "target": "Pyglet/OpenGL right-handed Y-up",
            "vector_mapping": "(x, y, z) -> (x, z, -y)",
            "rotation": "ordered axis-angle steps in radians",
            "transform_order": "translation @ rotation @ scale",
        },
        "source_blend": bpy.data.filepath or None,
        "warnings": warnings,
        "nodes": nodes,
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Exported {len(nodes)} visible nodes to: {path}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    return path


if __name__ == "__main__":
    export_scene()
