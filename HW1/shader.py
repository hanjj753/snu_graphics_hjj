from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.gl import GL_TRIANGLES

from primitives import Geometry

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

def create_program(vs_source=VERTEX_SHADER_SOURCE, fs_source=FRAGMENT_SHADER_SOURCE):
    vert_shader = Shader(vs_source, 'vertex')
    frag_shader = Shader(fs_source, 'fragment')
    return ShaderProgram(vert_shader, frag_shader)

def create_vertex_list(program:ShaderProgram, geometry:Geometry) :
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
