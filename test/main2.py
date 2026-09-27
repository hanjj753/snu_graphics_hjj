import pyglet
import math
from math import pi

from pyglet.gl import glClearColor, glEnable, glViewport, GL_TRIANGLES, GL_DEPTH_TEST, GL_CULL_FACE
from pyglet.math import Mat4, Vec3
from pyglet.graphics.shader import Shader, ShaderProgram

from primitives import CubeGeometry, SphereGeometry

def create_vertex_list(program:ShaderProgram, geometry) :
    return program.vertex_list_indexed(
        len(geometry.vertices) // 3,
        GL_TRIANGLES,
        geometry.indices,
        vertices=(
            "f",
            geometry.vertices
        ),
        colors=(
            "Bn",
            geometry.colors
        )
    )

VERTEX_SHADER_SOURCE = """
#version 330 core

layout(location = 0) in vec3 vertices;
layout(location = 1) in vec4 colors;

out vec4 vertex_color;

uniform mat4 model;
uniform mat4 view_proj;

void main() {
    
    gl_Position =  view_proj * model * vec4(vertices, 1.0);
    vertex_color = colors;

}
"""

FRAGMENT_SHADER_SOURCE = """
#version 330 core

in vec4 vertex_color;
out vec4 final_color;

void main() {

    final_color = vertex_color;

}
"""

class SceneNode :
    
    def __init__(self, mesh=None) :
        self.mesh = mesh
        self.children = []

        self.local_transform = Mat4()
        self.shape_transform = Mat4()
        self.world_transform = Mat4()

    def add_child(self, child) :
        self.children.append(child)
        return child

    def update_world(self, parent_world=None) :
        if parent_world is None :
            parent_world = Mat4()

        self.world_transform = parent_world @ self.local_transform

        for child in self.children : 
            child.update_world(self.world_transform)

    def draw(self, program) :
        if self.mesh is not None :
            model_matrix = self.world_transform @ self.shape_transform

            program["model"] = model_matrix
            self.mesh.draw(GL_TRIANGLES)

        for child in self.children :
            child.draw(program)

class PigeonWindow(pyglet.window.Window) :

    def __init__(self) :
        super().__init__(
            width = 960,
            height = 540,
            resizable = True,
            caption = "Pigeon",
        )

        glClearColor(0.15, 0.18, 0.25, 1.0)
        glEnable(GL_DEPTH_TEST) # 겹쳤을 떄 앞에 있는 면을 남김
        glEnable(GL_CULL_FACE)  # 큐브 뒷면 그리지 않음
        
        self.elapsed_time = 0.0

        self.parent_length = 0.55
        self.child_length = 0.40

        vertex_shader = Shader(VERTEX_SHADER_SOURCE, "vertex")
        fragment_shader = Shader(FRAGMENT_SHADER_SOURCE, "fragment")
        self.program = ShaderProgram(
            vertex_shader, 
            fragment_shader,
        )

        cube_geometry = CubeGeometry()
        sphere_geometry = SphereGeometry()
        self.cube = create_vertex_list(self.program, cube_geometry)
        self.sphere = create_vertex_list(self.program, sphere_geometry)

        self.root = SceneNode()
        self.body_node = SceneNode(self.sphere)
        self.head_node = SceneNode(self.sphere)
        self.root.add_child(self.body_node)
        self.body_node.add_child(self.head_node)

        self.body_node.shape_transform = Mat4.from_scale(Vec3(1.2, 0.75, 0.7))
        self.head_node.shape_transform = Mat4.from_scale(Vec3(0.42, 0.42, 0.42))
        self.head_node.local_transform = Mat4.from_translation(Vec3(0.62, 0.25, 0.0))

        self.root.update_world()

        # Camera 셋업
        self.camera_position = Vec3(0, 0, 3)
        self.camera_target = Vec3(0, 0, 0)
        self.camera_up = Vec3(0, 1, 0)
        self.view_matrix = Mat4.look_at(
            position=self.camera_position,
            target=self.camera_target,
            up=self.camera_up,
        )
        self.projection_matrix = Mat4.perspective_projection(
            aspect=self.width/self.height,
            z_near=0.1,
            z_far=100,
            fov=60
        )

    def on_draw(self) :
        self.clear()

        view_proj = self.projection_matrix @ self.view_matrix

        self.program.use() # Shader 활성화
        self.program["view_proj"] = view_proj
        self.root.draw(self.program)
        self.program.stop() # Shader 비활성화

    def update(self, dt) :
        self.elapsed_time += dt

        body_angle = (
            0.15
            * math.sin(0.7 * self.elapsed_time)
        )

        self.body_node.local_transform = (
            Mat4.from_rotation(
                body_angle,
                Vec3(0.0, 1.0, 0.0),
            )
        )

        head_bob = (
            0.04
            * math.sin(2.0 * self.elapsed_time)
        )

        head_angle = (
            0.12
            * math.sin(2.0 * self.elapsed_time)
        )

        self.head_node.local_transform = (
            Mat4.from_translation(
                Vec3(
                    0.62,
                    0.25 + head_bob,
                    0.0,
                )
            )
            @ Mat4.from_rotation(
                head_angle,
                Vec3(0.0, 0.0, 1.0),
            )
        )

        self.root.update_world()

    def on_resize(self, width, height) :
        glViewport(
            0, 0,
            *self.get_framebuffer_size(),
        )

        self.projection_matrix = Mat4.perspective_projection(
            aspect= width/max(height, 1),
            z_near=0.1,
            z_far=100,
            fov=60
        )

        return pyglet.event.EVENT_HANDLED

    def run(self) :
        pyglet.clock.schedule_interval(self.update, 1/60)
        pyglet.app.run()

if __name__ == "__main__" :

    window = PigeonWindow()
    window.run()