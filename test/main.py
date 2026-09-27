import pyglet
import math
from math import pi

from pyglet.gl import glClearColor, glEnable, glViewport, GL_TRIANGLES, GL_DEPTH_TEST, GL_CULL_FACE
from pyglet.math import Mat4, Vec3
from pyglet.graphics.shader import Shader, ShaderProgram

# GLSL 이라고 하는 OpenGL Shading Language를 str로 GPU에 전달해줌
# Python str -> Shader() : OpenGL 드라이버가 GLSL 컴파일
# #version 330 core                         <- GLSL 3.30 버전 사용
# layout(location = 0) in vec3 vertices;    <- vec3로 input 받겠다는 것
# out vec4 vertex_color;                    <- vec4를 다음 단계로 전달하겠다는 것
# gl_Position                               <- homogeneous coordinates
# uniform                                   <- 모든 vertex가 공유하는 shader 입력값 -> 이걸 gl_Position에 곱해주어야 함
# Vertex Shader 은 vertex마다 한 번씩 실행됨.
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

# Fragment shader은 각 픽셀이 어떤 색인지에 대한 정보를 계산
# Fragment Shader은 삼각형 내부의 픽셀마다 한번씩 실행됨.
# vec4인 이유는 RGB + alpha
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
        # self.parent_model = Mat4()
        # self.child_model = Mat4()

        # self.model_matrix = Mat4() # 기본 Mat4 는 Identity Matrix, 4x4 Matrix인 이유는 homogeneous coordinate이기 때문

        vertex_shader = Shader(VERTEX_SHADER_SOURCE, "vertex")
        fragment_shader = Shader(FRAGMENT_SHADER_SOURCE, "fragment")
        self.program = ShaderProgram(
            vertex_shader, 
            fragment_shader,
        )

        self.triangle = self.program.vertex_list( # Pyglet 내장 함수
            3, # vertex 개수
            GL_TRIANGLES, #vertex 3개를 하나의 삼각형으로 보라는 뜻
            vertices = (
                "f", # float
                (
                    -0.6, -0.5, 0.0,
                     0.6, -0.5, 0.0,
                     0.0,  0.6, 0.0,
                )
            ),
            colors = (
                "Bn", # normalized unsigned Byte
                (
                    255,   0,   0, 255,
                      0, 255,   0, 255,
                      0,   0, 255, 255,
                )
            )
        )

        self.rectangle = self.program.vertex_list_indexed(
            4,
            GL_TRIANGLES,
            (
                0, 1, 2,
                0, 2, 3,
            ),
            vertices=(
                "f",
                (
                    -0.6, -0.5, 0.0,  # 0: 왼쪽 아래
                    0.6, -0.5, 0.0,  # 1: 오른쪽 아래
                    0.6,  0.5, 0.0,  # 2: 오른쪽 위
                    -0.6,  0.5, 0.0,  # 3: 왼쪽 위
                ),
            ),
            colors=(
                "Bn",
                (
                    255,   0,   0, 255,  # 0: 빨강
                    0, 255,   0, 255,  # 1: 초록
                    0,   0, 255, 255,  # 2: 파랑
                    255, 255,   0, 255,  # 3: 노랑
                ),
            ),
        )

        self.link = self.program.vertex_list_indexed(
            4,  # vertex 개수
            GL_TRIANGLES,
            ( # index는 반시계 방향으로 그려야 함
                0, 1, 2, 
                0, 2, 3,
            ),
            vertices = (
                "f", # float
                (
                    0.0, -0.08, 0.0,
                    1.0, -0.08, 0.0,
                    1.0,  0.08, 0.0,
                    0.0,  0.08, 0.0,
                )
            ),
            colors = (
                "Bn", # normalized unsigned Byte
                (
                    255, 120,  30, 255,
                    255, 200,  40, 255,
                    255, 200,  40, 255,
                    255, 120,  30, 255, 
                )
            )
        )

        self.cube = self.program.vertex_list_indexed(
            8,
            GL_TRIANGLES,
            (
                # 앞면: +z
                4, 5, 6,
                4, 6, 7,

                # 뒷면: -z
                0, 3, 2,
                0, 2, 1,

                # 왼쪽: -x
                0, 4, 7,
                0, 7, 3,

                # 오른쪽: +x
                1, 2, 6,
                1, 6, 5,

                # 위쪽: +y
                3, 7, 6,
                3, 6, 2,

                # 아래쪽: -y
                0, 1, 5,
                0, 5, 4,
            ),
            vertices=(
                "f",
                (
                    -0.5, -0.5, -0.5,  # 0
                    0.5, -0.5, -0.5,  # 1
                    0.5,  0.5, -0.5,  # 2
                    -0.5,  0.5, -0.5,  # 3

                    -0.5, -0.5,  0.5,  # 4
                    0.5, -0.5,  0.5,  # 5
                    0.5,  0.5,  0.5,  # 6
                    -0.5,  0.5,  0.5,  # 7
                ),
            ),
            colors=(
                "Bn",
                (
                    255,  80,  80, 255,  # 0
                    80, 255,  80, 255,  # 1
                    80,  80, 255, 255,  # 2
                    255, 255,  80, 255,  # 3

                    255,  80, 255, 255,  # 4
                    80, 255, 255, 255,  # 5
                    255, 160,  80, 255,  # 6
                    220, 220, 220, 255,  # 7
                ),
            )
        )

        self.root = SceneNode()

        self.parent_node = SceneNode(self.cube)
        self.child_node = SceneNode(self.cube)

        self.root.add_child(self.parent_node)
        self.parent_node.add_child(self.child_node)

        self.tip_length = 0.3
        self.tip_node = SceneNode(self.cube)
        self.child_node.add_child(self.tip_node)

        self.parent_node.shape_transform = (
            Mat4.from_translation(Vec3(self.parent_length/2, 0, 0)) @
            Mat4.from_scale(Vec3(self.parent_length, 0.18, 0.18))
        ) 

        self.child_node.shape_transform = (
            Mat4.from_translation(Vec3(self.child_length/2, 0, 0)) @
            Mat4.from_scale(Vec3(self.child_length, 0.14, 0.14))
        )

        self.tip_node.shape_transform = (
            Mat4.from_translation(Vec3(self.child_length/2, 0, 0)) @
            Mat4.from_scale(Vec3(self.child_length, 0.1, 0.1))
        )

        self.root.update_world()

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

        self.program.use() # Shader 활성화

        # self.program["model"] = self.model_matrix # Shader의 uniform은 dictionary key 처럼 접근, Shader 활성화 시킨 후 적용해야 함.
        # self.rectangle.draw(GL_TRIANGLES) #삼각형 그리기

        view_proj = self.projection_matrix @ self.view_matrix
        self.program["view_proj"] = view_proj
        self.root.draw(self.program)

        # self.program["model"] = self.parent_model
        # self.cube.draw(GL_TRIANGLES)

        # self.program["model"] = self.child_model
        # self.cube.draw(GL_TRIANGLES)

        self.program.stop() # Shader 비활성화

    def update(self, dt) :
        self.elapsed_time += dt

        # 배경색 바꾸기
        # 0 ~ 1까지 주기 1초로 sin파
        # pulse = 0.5 + 0.5 * math.sin(2 * pi * self.elapsed_time)
        # glClearColor(0.15, 0.18, 0.25 + 0.25*pulse, 1)

        # x = 0.3 * math.sin(self.elapsed_time)
        # translation = Mat4.from_translation( # identity matrix에 가장 오른쪽 col이 (x, 0, 0, 1) 임.
        #     Vec3(x, 0.0, 0.0), 
        # )
        # rotation = Mat4.from_rotation( # 3, 4번쨰 col, row 는 identity, 1, 2번째 row col 은 cos -sin sin cos
        #     self.elapsed_time, #각도
        #     Vec3(0.0, 0.0, 1.0), #축
        # )
        # scale = Mat4.from_scale( # identity에 대각선 값만 vec3의 값으로 교체
        #     Vec3(0.6, 0.6, 1.0) 
        # )
        # self.model_matrix = rotation @ translation @ scale # 오른쪽부터 해석 / 왼쪽 축 해석

        z_axis = Vec3(0, 0, 1)

        scene_angle = 0.5 * pi * math.sin(
            0.7 * self.elapsed_time
        )

        scene_rotation = Mat4.from_rotation(
            scene_angle,
            Vec3(0, 1, 0)
        )

        parent_angle = 0.6 * math.sin(self.elapsed_time)
        child_angle = 0.8 * math.sin(1.7*self.elapsed_time)
        tip_angle = 0.5 * math.sin(2.2*self.elapsed_time)

        base_translation = Mat4.from_translation(
            Vec3(-0.45, 0, 0)
        )

        parent_rotation = Mat4.from_rotation(
            parent_angle,
            z_axis,
        )

        self.parent_node.local_transform = base_translation @ scene_rotation @ parent_rotation

        # parent_frame = base_translation @ scene_rotation @ parent_rotation

        # parent_center = Mat4.from_translation(
        #     Vec3(self.parent_length/2, 0, 0)
        # )

        # parent_shape = Mat4.from_scale(
        #     Vec3(self.parent_length, 0.18, 0.18)
        # )

        # self.parent_model = parent_frame @ parent_center @ parent_shape

        child_joint_translation = Mat4.from_translation(
            Vec3(self.parent_length, 0, 0)
        )

        child_rotation = Mat4.from_rotation(
            child_angle,
            z_axis,
        )

        self.child_node.local_transform = child_joint_translation @ child_rotation

        self.tip_node.local_transform = (
            Mat4.from_translation(Vec3(self.child_length, 0, 0)) @
            Mat4.from_rotation(tip_angle, z_axis)
        )

        self.root.update_world()

        # child_frame = parent_frame @ child_joint_translation @ child_rotation

        # child_shape = Mat4.from_scale(
        #     Vec3(self.child_length, 0.14, 0.14)
        # )

        # child_center = Mat4.from_translation(
        #     Vec3(self.child_length/2, 0, 0)
        # )

        # self.child_model = child_frame @ child_center @ child_shape



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