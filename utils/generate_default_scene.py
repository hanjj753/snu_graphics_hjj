"""Print paste-ready scene construction code from an exported scene JSON.

This script uses only Python's standard library. Run it from the project root:

    python utils/generate_default_scene.py HW1/pigeon_blockout.scene.json

The default output is indented for pasting over ``pass`` inside the existing
scene-building method. Use ``--whole-method`` to print the complete method and
``--method-name`` to choose its name.

The default geometry indexes match::

    [CubeGeometry(), SphereGeometry()]

Override or add a mapping with a repeated option such as
``--geometry cube=2 --geometry sphere=0``.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SUPPORTED_FORMAT_VERSION = 2
DEFAULT_GEOMETRY_MAP = {"cube": 0, "sphere": 1}
EPSILON = 5e-7
ANGLE_STEP_IN_PI = 0.05


def _number(value: Any, description: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{description} must be a number") from exc
    if not math.isfinite(result):
        raise ValueError(f"{description} must be finite")
    return 0.0 if abs(result) < EPSILON else result


def _number_literal(value: float) -> str:
    if value == 0.0:
        return "0.0"
    return repr(round(value, 6))


def _quantized_angle_literal(angle: float) -> str | None:
    """Return the nearest 0.05 * n * pi expression, or None for zero."""

    step_count = angle / (ANGLE_STEP_IN_PI * math.pi)
    if step_count >= 0.0:
        nearest_step = math.floor(step_count + 0.5)
    else:
        nearest_step = math.ceil(step_count - 0.5)

    if nearest_step == 0:
        return None

    coefficient = nearest_step * ANGLE_STEP_IN_PI
    coefficient_text = f"{coefficient:.2f}".rstrip("0").rstrip(".")
    return f"{coefficient_text} * pi"


def _vector3(value: Any, description: str) -> tuple[float, float, float]:
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(f"{description} must contain three numbers")
    return tuple(
        _number(component, f"{description}[{index}]")
        for index, component in enumerate(value)
    )


def _vec3_expression(value: tuple[float, float, float]) -> str:
    components = ", ".join(_number_literal(component) for component in value)
    return f"Vec3({components})"


def _transform_expressions(
    value: Any,
    field_name: str,
    node_name: str,
) -> list[str]:
    if not isinstance(value, dict):
        raise ValueError(f"{node_name}.{field_name} must be an object")

    translation = _vector3(
        value.get("translation"),
        f"{node_name}.{field_name}.translation",
    )
    scale = _vector3(
        value.get("scale"),
        f"{node_name}.{field_name}.scale",
    )

    rotations = value.get("rotations")
    if not isinstance(rotations, list):
        raise ValueError(f"{node_name}.{field_name}.rotations must be a list")

    expressions: list[str] = []
    if any(abs(component) > EPSILON for component in translation):
        expressions.append(
            f"Mat4.from_translation({_vec3_expression(translation)})"
        )

    for index, rotation in enumerate(rotations):
        if not isinstance(rotation, dict):
            raise ValueError(
                f"{node_name}.{field_name}.rotations[{index}] must be an object"
            )
        angle = _number(
            rotation.get("angle"),
            f"{node_name}.{field_name}.rotations[{index}].angle",
        )
        axis = _vector3(
            rotation.get("axis"),
            f"{node_name}.{field_name}.rotations[{index}].axis",
        )
        angle_literal = _quantized_angle_literal(angle)
        if angle_literal is None:
            continue
        axis_length = math.sqrt(sum(component * component for component in axis))
        if axis_length < EPSILON:
            raise ValueError(
                f"{node_name}.{field_name}.rotations[{index}].axis cannot be zero "
                "when its angle is nonzero"
            )
        normalized_axis = tuple(component / axis_length for component in axis)
        expressions.append(
            "Mat4.from_rotation("
            f"{angle_literal}, {_vec3_expression(normalized_axis)})"
        )

    if any(abs(component - 1.0) > EPSILON for component in scale):
        expressions.append(f"Mat4.from_scale({_vec3_expression(scale)})")

    return expressions


def _append_keyword_transform(
    lines: list[str],
    keyword: str,
    value: Any,
    node_name: str,
    indent: str,
) -> None:
    expressions = _transform_expressions(value, keyword, node_name)
    if not expressions:
        lines.append(f"{indent}{keyword}=Mat4(),")
    elif len(expressions) == 1:
        lines.append(f"{indent}{keyword}={expressions[0]},")
    else:
        lines.append(f"{indent}{keyword}=(")
        lines.append(f"{indent}    {expressions[0]}")
        for expression in expressions[1:]:
            lines.append(f"{indent}    @ {expression}")
        lines.append(f"{indent}),")


def _read_nodes(json_path: Path) -> tuple[list[dict[str, Any]], tuple[str, ...]]:
    document = json.loads(json_path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("Scene JSON root must be an object")

    version = document.get("format_version")
    if version != SUPPORTED_FORMAT_VERSION:
        raise ValueError(
            f"Unsupported scene format version {version!r}; expected "
            f"{SUPPORTED_FORMAT_VERSION}. Run export_blender_scene.py again."
        )

    nodes = document.get("nodes")
    if not isinstance(nodes, list):
        raise ValueError("Scene JSON must contain a 'nodes' list")

    names: list[str] = []
    for entry in nodes:
        if not isinstance(entry, dict):
            raise ValueError("Every scene node must be a JSON object")
        name = entry.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError("Every scene node must have a non-empty string name")
        if name == "root":
            raise ValueError("'root' is reserved by RenderWindow")
        if entry.get("geometry") is None:
            raise ValueError(
                f"Node {name!r} has no geometry. Re-export with the compact "
                "version of export_blender_scene.py."
            )
        names.append(name)

    if len(names) != len(set(names)):
        raise ValueError("Scene JSON contains duplicate node names")

    export_warnings = document.get("warnings", [])
    if not isinstance(export_warnings, list):
        raise ValueError("Scene JSON 'warnings' must be a list")

    return nodes, tuple(str(item) for item in export_warnings)


def _order_parents_before_children(
    nodes: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    known_names = {entry["name"] for entry in nodes}
    for entry in nodes:
        parent = entry.get("parent")
        if parent is not None and parent not in known_names:
            raise ValueError(
                f"Node {entry['name']!r} refers to missing parent {parent!r}"
            )

    pending = list(nodes)
    ordered: list[dict[str, Any]] = []
    available = {"root"}

    while pending:
        made_progress = False
        for entry in pending[:]:
            parent = entry.get("parent") or "root"
            if parent not in available:
                continue
            ordered.append(entry)
            available.add(entry["name"])
            pending.remove(entry)
            made_progress = True

        if not made_progress:
            unresolved = {
                entry["name"]: entry.get("parent")
                for entry in pending
            }
            raise ValueError(f"Scene hierarchy contains a cycle: {unresolved}")

    return ordered


def _parse_geometry_map(values: Iterable[str]) -> dict[str, int]:
    result = dict(DEFAULT_GEOMETRY_MAP)
    for value in values:
        key, separator, raw_index = value.partition("=")
        key = key.strip().lower()
        if not separator or not key:
            raise ValueError(
                f"Invalid geometry mapping {value!r}; expected NAME=INDEX"
            )
        try:
            index = int(raw_index)
        except ValueError as exc:
            raise ValueError(
                f"Invalid geometry index in {value!r}; expected an integer"
            ) from exc
        if index < 0:
            raise ValueError(f"Geometry index cannot be negative: {value!r}")
        result[key] = index
    return result


def generate_scene_code(
    nodes: Sequence[dict[str, Any]],
    geometry_map: Mapping[str, int],
    *,
    whole_method: bool = False,
    method_name: str = "create_pigeon",
) -> str:
    """Return Python source ready to paste into a RenderWindow subclass."""

    ordered = _order_parents_before_children(nodes)
    body_indent = "        "
    lines: list[str] = []

    if whole_method:
        if not method_name.isidentifier():
            raise ValueError(f"Invalid Python method name: {method_name!r}")
        lines.append(f"    def {method_name}(self):")

    lines.append(f"{body_indent}# Generated from Blender scene JSON.")
    lines.append(f"{body_indent}from math import pi")
    lines.append(f"{body_indent}from pyglet.math import Mat4, Vec3")

    if not ordered:
        lines.append(f"{body_indent}pass")
        return "\n".join(lines) + "\n"

    for entry in ordered:
        name = entry["name"]
        parent = entry.get("parent") or "root"
        geometry_key = str(entry.get("geometry")).strip().lower()
        if geometry_key not in geometry_map:
            raise ValueError(
                f"No geometry index for {geometry_key!r} (node {name!r}). "
                f"Pass --geometry {geometry_key}=INDEX."
            )

        lines.append("")
        lines.append(f"{body_indent}self.add_node(")
        argument_indent = body_indent + "    "
        lines.append(
            f"{argument_indent}geo_index={int(geometry_map[geometry_key])},"
        )
        lines.append(f"{argument_indent}name={name!r},")
        lines.append(f"{argument_indent}parent={parent!r},")
        _append_keyword_transform(
            lines,
            "local_transform",
            entry.get("local_transform"),
            name,
            argument_indent,
        )
        _append_keyword_transform(
            lines,
            "shape_transform",
            entry.get("shape_transform"),
            name,
            argument_indent,
        )
        lines.append(f"{body_indent})")

    return "\n".join(lines) + "\n"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Print code that recreates an exported Blender scene inside a "
            "RenderWindow subclass. Rotation angles are rounded to 0.05*pi."
        )
    )
    parser.add_argument("json_path", type=Path, help="JSON exported from Blender")
    parser.add_argument(
        "--geometry",
        action="append",
        default=[],
        metavar="NAME=INDEX",
        help=(
            "map an exported geometry name to a geo_list index; may be repeated "
            "(defaults: cube=0, sphere=1)"
        ),
    )
    parser.add_argument(
        "--whole-method",
        action="store_true",
        help="include the indented method definition line",
    )
    parser.add_argument(
        "--method-name",
        default="create_pigeon",
        help="method name used with --whole-method (default: create_pigeon)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    arguments = parser.parse_args(argv)

    try:
        geometry_map = _parse_geometry_map(arguments.geometry)
        nodes, export_warnings = _read_nodes(arguments.json_path.resolve())
        code = generate_scene_code(
            nodes,
            geometry_map,
            whole_method=arguments.whole_method,
            method_name=arguments.method_name,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))

    for warning in export_warnings:
        print(f"Export warning: {warning}", file=sys.stderr)
    print(code, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
