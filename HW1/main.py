from pyglet.math import Mat4, Vec3
from math import pi, sin, cos, hypot, atan2

from render import RenderWindow
from primitives import Geometry, CubeGeometry, SphereGeometry

class PigeonWindow(RenderWindow) :

    def __init__(self, width=1280, height=720, caption="Pigeon", resizable=True, camera_position=Vec3(3, 3, 3), background_color=(1.0, 1.0, 1.0, 1.0)):

        geo_list = [
            CubeGeometry(), 
            SphereGeometry(),
            SphereGeometry(color=(100, 100, 100, 200)), #회색
            SphereGeometry(color=(50, 50, 50, 255)), # 짙은 회색,
            CubeGeometry(color=(100, 100, 100, 255)),
        ]
        super().__init__(geometry_list=geo_list, width=width, height=height, caption=caption, resizable=resizable, camera_position=camera_position, background_color=background_color)

        self.create_pigeon()
        self.save_default_pose()

        self.node_dict["root"].update_world()

    def create_pigeon(self) :
        """
        Blender에서 작업한 뒤에 숫자 보고 노가다 뛰면 될 듯
        """

        self.add_node(
            geo_index=3,
            name='Body',
            parent='root',
            local_transform=Mat4(),
            shape_transform=(
                Mat4.from_translation(Vec3(-0.2, 0.0, 0.0))
                @ Mat4.from_rotation(0.1 * pi, Vec3(0.0, 0.0, 1.0))
                @ Mat4.from_scale(Vec3(2.4, 1.35, 1.2))
            ),
        )

        self.add_node(
            geo_index=1,
            name='Neck',
            parent='Body',
            local_transform=Mat4.from_translation(Vec3(0.75, 0.65, 0.0)),
            shape_transform=(
                Mat4.from_rotation(-0.15 * pi, Vec3(0.0, 0.0, 1.0))
                @ Mat4.from_scale(Vec3(0.65, 1.1, 0.55))
            ),
        )

        self.add_node(
            geo_index=1,
            name='Head',
            parent='Neck',
            local_transform=Mat4.from_translation(Vec3(0.4, 0.5, 0.0)),
            shape_transform=Mat4.from_scale(Vec3(0.6, 0.6, 0.6)),
        )

        self.add_node(
            geo_index=0,
            name='Beak',
            parent='Head',
            local_transform=(
                Mat4.from_translation(Vec3(0.25, -0.05, 0.0))
                @ Mat4.from_rotation(-0.05 * pi, Vec3(0.0, 0.0, 1.0))
            ),
            shape_transform=(
                Mat4.from_translation(Vec3(0.1, 0.0, 0.0))
                @ Mat4.from_scale(Vec3(0.2, 0.075, 0.1))
            ),
        )

        self.add_node(
            geo_index=3,
            name='LeftEye',
            parent='Head',
            local_transform=Mat4.from_translation(Vec3(0.1, 0.08, 0.27)),
            shape_transform=Mat4.from_scale(Vec3(0.1, 0.1, 0.08)),
        )

        self.add_node(
            geo_index=3,
            name='RightEye',
            parent='Head',
            local_transform=Mat4.from_translation(Vec3(0.1, 0.08, -0.27)),
            shape_transform=Mat4.from_scale(Vec3(0.1, 0.1, 0.08)),
        )

        self.add_node(
            geo_index=0,
            name='LeftUpperWing',
            parent='Body',
            local_transform=(
                Mat4.from_translation(Vec3(0.2, 0.3, 0.4))
                @ Mat4.from_rotation(-0.05 * pi, Vec3(0.0, 1.0, 0.0))
                @ Mat4.from_rotation(-0.1 * pi, Vec3(0.0, 0.0, 1.0))
                @ Mat4.from_rotation(0.4 * pi, Vec3(1.0, 0.0, 0.0))
                @ Mat4.from_scale(Vec3(1.0, 1.0, 0.97))
            ),
            shape_transform=(
                Mat4.from_translation(Vec3(0.0, 0.0, 0.4))
                @ Mat4.from_scale(Vec3(0.75, 0.2, 0.8))
            ),
        )

        self.add_node(
            geo_index=0,
            name='LeftLowerWing',
            parent='LeftUpperWing',
            local_transform=(
                Mat4.from_translation(Vec3(0.0, 0.0, 0.7))
                @ Mat4.from_rotation(-0.1 * pi, Vec3(0.0, 1.0, 0.0))
            ),
            shape_transform=(
                Mat4.from_translation(Vec3(0.0, 0.0, 0.4))
                @ Mat4.from_scale(Vec3(0.6, 0.12, 0.8))
            ),
        )

        self.add_node(
            geo_index=0,
            name='LeftWingTip',
            parent='LeftLowerWing',
            local_transform=(
                Mat4.from_translation(Vec3(0.0, 0.0, 0.7))
                @ Mat4.from_rotation(-0.05 * pi, Vec3(0.0, 1.0, 0.0))
            ),
            shape_transform=(
                Mat4.from_translation(Vec3(0.0, 0.0, 0.3))
                @ Mat4.from_scale(Vec3(0.38, 0.1, 0.6))
            ),
        )

        self.add_node(
            geo_index=0,
            name='RightUpperWing',
            parent='Body',
            local_transform=(
                Mat4.from_translation(Vec3(0.2, 0.3, -0.4))
                @ Mat4.from_rotation(0.05 * pi, Vec3(0.0, 1.0, 0.0))
                @ Mat4.from_rotation(-0.1 * pi, Vec3(0.0, 0.0, 1.0))
                @ Mat4.from_rotation(-0.4 * pi, Vec3(1.0, 0.0, 0.0))
                @ Mat4.from_scale(Vec3(1.0, 1.0, 0.97))
            ),
            shape_transform=(
                Mat4.from_translation(Vec3(0.0, 0.0, -0.4))
                @ Mat4.from_scale(Vec3(0.75, 0.2, 0.8))
            ),
        )

        self.add_node(
            geo_index=0,
            name='RightLowerWing',
            parent='RightUpperWing',
            local_transform=(
                Mat4.from_translation(Vec3(0.0, 0.0, -0.7))
                @ Mat4.from_rotation(0.1 * pi, Vec3(0.0, 1.0, 0.0))
            ),
            shape_transform=(
                Mat4.from_translation(Vec3(0.0, 0.0, -0.4))
                @ Mat4.from_scale(Vec3(0.6, 0.12, 0.8))
            ),
        )

        self.add_node(
            geo_index=0,
            name='RightWingTip',
            parent='RightLowerWing',
            local_transform=(
                Mat4.from_translation(Vec3(0.0, 0.0, -0.7))
                @ Mat4.from_rotation(0.05 * pi, Vec3(0.0, 1.0, 0.0))
            ),
            shape_transform=(
                Mat4.from_translation(Vec3(0.0, 0.0, -0.3))
                @ Mat4.from_scale(Vec3(0.38, 0.1, 0.6))
            ),
        )

        self.add_node(
            geo_index=4,
            name='LeftUpperLeg',
            parent='root',
            local_transform=Mat4.from_translation(Vec3(-0.15, -0.55, 0.3)),
            shape_transform=(
                Mat4.from_translation(Vec3(0.0, -0.18, 0.0))
                @ Mat4.from_scale(Vec3(0.16, 0.36, 0.16))
            ),
        )

        self.add_node(
            geo_index=4,
            name='LeftLowerLeg',
            parent='LeftUpperLeg',
            local_transform=Mat4.from_translation(Vec3(0.0, -0.36, 0.0)),
            shape_transform=(
                Mat4.from_translation(Vec3(0.0, -0.2, 0.0))
                @ Mat4.from_scale(Vec3(0.14, 0.4, 0.14))
            ),
        )

        self.add_node(
            geo_index=0,
            name='LeftFoot',
            parent='LeftLowerLeg',
            local_transform=Mat4.from_translation(Vec3(0.0, -0.4, 0.0)),
            shape_transform=(
                Mat4.from_translation(Vec3(0.22, -0.04, 0.0))
                @ Mat4.from_scale(Vec3(0.44, 0.1, 0.2))
            ),
        )

        self.add_node(
            geo_index=4,
            name='RightUpperLeg',
            parent='root',
            local_transform=Mat4.from_translation(Vec3(-0.15, -0.55, -0.3)),
            shape_transform=(
                Mat4.from_translation(Vec3(0.0, -0.18, 0.0))
                @ Mat4.from_scale(Vec3(0.16, 0.36, 0.16))
            ),
        )

        self.add_node(
            geo_index=4,
            name='RightLowerLeg',
            parent='RightUpperLeg',
            local_transform=Mat4.from_translation(Vec3(0.0, -0.36, 0.0)),
            shape_transform=(
                Mat4.from_translation(Vec3(0.0, -0.2, 0.0))
                @ Mat4.from_scale(Vec3(0.14, 0.4, 0.14))
            ),
        )

        self.add_node(
            geo_index=0,
            name='RightFoot',
            parent='RightLowerLeg',
            local_transform=Mat4.from_translation(Vec3(0.0, -0.4, 0.0)),
            shape_transform=(
                Mat4.from_translation(Vec3(0.22, -0.04, 0.0))
                @ Mat4.from_scale(Vec3(0.44, 0.1, 0.2))
            ),
        )

        self.add_node(
            geo_index=0,
            name='LeftPrimaryFeather1',
            parent='LeftWingTip',
            local_transform=(
                Mat4.from_translation(Vec3(-0.2, -0.03, 0.38))
                @ Mat4.from_rotation(0.1 * pi, Vec3(0.0, 1.0, 0.0))
            ),
            shape_transform=Mat4.from_scale(Vec3(0.7, 0.06, 0.16)),
        )

        self.add_node(
            geo_index=0,
            name='LeftPrimaryFeather2',
            parent='LeftWingTip',
            local_transform=(
                Mat4.from_translation(Vec3(-0.3, -0.05, 0.35))
                @ Mat4.from_rotation(0.2 * pi, Vec3(0.0, 1.0, 0.0))
            ),
            shape_transform=Mat4.from_scale(Vec3(0.76, 0.05, 0.15)),
        )

        self.add_node(
            geo_index=0,
            name='LeftPrimaryFeather3',
            parent='LeftWingTip',
            local_transform=(
                Mat4.from_translation(Vec3(-0.4, -0.07, 0.28))
                @ Mat4.from_rotation(0.3 * pi, Vec3(0.0, 1.0, 0.0))
            ),
            shape_transform=Mat4.from_scale(Vec3(0.82, 0.05, 0.14)),
        )

        self.add_node(
            geo_index=0,
            name='RightPrimaryFeather1',
            parent='RightWingTip',
            local_transform=(
                Mat4.from_translation(Vec3(-0.2, -0.03, -0.38))
                @ Mat4.from_rotation(-0.1 * pi, Vec3(0.0, 1.0, 0.0))
            ),
            shape_transform=Mat4.from_scale(Vec3(0.7, 0.06, 0.16)),
        )

        self.add_node(
            geo_index=0,
            name='RightPrimaryFeather2',
            parent='RightWingTip',
            local_transform=(
                Mat4.from_translation(Vec3(-0.3, -0.05, -0.35))
                @ Mat4.from_rotation(-0.2 * pi, Vec3(0.0, 1.0, 0.0))
            ),
            shape_transform=Mat4.from_scale(Vec3(0.76, 0.05, 0.15)),
        )

        self.add_node(
            geo_index=0,
            name='RightPrimaryFeather3',
            parent='RightWingTip',
            local_transform=(
                Mat4.from_translation(Vec3(-0.4, -0.07, -0.28))
                @ Mat4.from_rotation(-0.3 * pi, Vec3(0.0, 1.0, 0.0))
            ),
            shape_transform=Mat4.from_scale(Vec3(0.82, 0.05, 0.14)),
        )
        
    def save_default_pose(self) :
        self.default_pose = { name: node.local_transform for name, node in self.node_dict.items() }
        self.default_shape = { name: node.shape_transform for name, node in self.node_dict.items() }

    def animate(self, dt) :
        """
        애니메이션 구현 계획

        0~2초 : (제자리에서) 걷기
        - RightUpperLeg, LeftUpperLeg z축 기준 회전시키면 됨
        - 움직이게 할 거면 body 자체를 translation을 주면 될 듯
        2~4초 : 바닥 쪼기
        4~6초 : 날개 퍼덕이기
        - 날개 필 때 x축 기준으로도 돌려야 하는데 z축 기준으로도 조금 돌려야 자연스러울 듯
        """
        x_axis = Vec3(1, 0, 0)
        y_axis = Vec3(0, 1, 0)
        z_axis = Vec3(0, 0, 1)

        if self.elapsed_time < 2 : # 걷기

            body_move = 0.5 * self.elapsed_time
            body_bob = 0.01 * abs(sin(pi * self.elapsed_time))
            self.node_dict["Body"].local_transform = self.default_pose["Body"] @ Mat4.from_translation(Vec3(body_move, body_bob, 0))

            leg_angle = 0.4 * sin(2*pi * self.elapsed_time) # 주기 1초
            self.node_dict["RightUpperLeg"].local_transform = self.default_pose["RightUpperLeg"] @ Mat4.from_translation(Vec3(body_move, 0, 0)) @ Mat4.from_rotation(leg_angle, z_axis)
            self.node_dict["LeftUpperLeg"].local_transform = self.default_pose["LeftUpperLeg"] @ Mat4.from_translation(Vec3(body_move, 0, 0)) @ Mat4.from_rotation(-leg_angle, z_axis)

        elif self.elapsed_time < 3 :

            body_angle = 0.3*pi * sin(0.5*pi * self.elapsed_time) # pi/2까지 도달하는데 1초
            self.node_dict["Body"].local_transform = self.default_pose["Body"] @ Mat4.from_translation(Vec3(1, 0, 0)) @ Mat4.from_rotation(body_angle, z_axis)

            neck_angle = 0.1*pi * sin(0.5*pi * self.elapsed_time)
            self.node_dict["Neck"].local_transform = Mat4.from_rotation(neck_angle, Vec3(0, 0, 1)) @ self.default_pose["Neck"]

        elif self.elapsed_time < 4 :

            head_bob = 0.1 * abs(sin(4*pi * self.elapsed_time))
            self.node_dict["Head"].local_transform = self.default_pose["Head"] @ Mat4.from_translation(Vec3(head_bob, 0, 0))

        elif self.elapsed_time < 5 :

            body_angle = -0.3*pi * cos(0.5*pi * self.elapsed_time) # pi/2까지 도달하는데 1초
            self.node_dict["Body"].local_transform = self.default_pose["Body"] @ Mat4.from_translation(Vec3(1, 0, 0)) @ Mat4.from_rotation(body_angle, z_axis)

            neck_angle = -0.1*pi * cos(0.5*pi * self.elapsed_time)
            self.node_dict["Neck"].local_transform = Mat4.from_rotation(neck_angle, Vec3(0, 0, 1)) @ self.default_pose["Neck"]

        elif self.elapsed_time < 6 :
            pass
        

if __name__ == "__main__" :

    window = PigeonWindow(camera_position=Vec3(0, 0, -8), background_color=(0.15, 0.18, 0.25, 1))
    window.run()