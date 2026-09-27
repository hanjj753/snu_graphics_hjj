from pyglet.math import Mat4, Vec3
from render import RenderWindow
from primitives import CubeGeometry, SphereGeometry
from math import pi

class PigeonWindow(RenderWindow) :

    def __init__(self):

        geo_list = [
            CubeGeometry(), 
            SphereGeometry(),
            SphereGeometry(color=(200, 200, 200, 200))
        ]
        super().__init__(geometry_list=geo_list)

        self.create_pigeon()
        self.save_default_pose()

        self.node_dict["root"].update_world()

    def create_pigeon(self) :

        self.add_node(
            geo_index=1,
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
            geo_index=2,
            name='Head',
            parent='Neck',
            local_transform=Mat4.from_translation(Vec3(0.4, 0.5, 0.0)),
            shape_transform=Mat4.from_scale(Vec3(0.95, 0.9, 0.9)),
        )

        self.add_node(
            geo_index=0,
            name='Beak',
            parent='Head',
            local_transform=(
                Mat4.from_translation(Vec3(0.45, -0.05, 0.0))
                @ Mat4.from_rotation(-0.05 * pi, Vec3(0.0, 0.0, 1.0))
            ),
            shape_transform=(
                Mat4.from_translation(Vec3(0.1, 0.0, 0.0))
                @ Mat4.from_scale(Vec3(0.2, 0.15, 0.2))
            ),
        )

        self.add_node(
            geo_index=1,
            name='LeftEye',
            parent='Head',
            local_transform=Mat4.from_translation(Vec3(0.18, 0.12, 0.43)),
            shape_transform=Mat4.from_scale(Vec3(0.16, 0.16, 0.08)),
        )

        self.add_node(
            geo_index=1,
            name='RightEye',
            parent='Head',
            local_transform=Mat4.from_translation(Vec3(0.18, 0.12, -0.43)),
            shape_transform=Mat4.from_scale(Vec3(0.16, 0.16, 0.08)),
        )

        self.add_node(
            geo_index=0,
            name='LeftUpperWing',
            parent='Body',
            local_transform=(
                Mat4.from_translation(Vec3(0.0, 0.1, 0.5))
                @ Mat4.from_rotation(-0.05 * pi, Vec3(0.0, 1.0, 0.0))
                @ Mat4.from_rotation(0.1 * pi, Vec3(0.0, 0.0, 1.0))
                @ Mat4.from_rotation(-0.05 * pi, Vec3(1.0, 0.0, 0.0))
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
                @ Mat4.from_rotation(-0.1 * pi, Vec3(1.0, 0.0, 0.0))
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
                @ Mat4.from_rotation(-0.05 * pi, Vec3(1.0, 0.0, 0.0))
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
                Mat4.from_translation(Vec3(0.0, 0.1, -0.5))
                @ Mat4.from_rotation(0.05 * pi, Vec3(0.0, 1.0, 0.0))
                @ Mat4.from_rotation(0.1 * pi, Vec3(0.0, 0.0, 1.0))
                @ Mat4.from_rotation(0.05 * pi, Vec3(1.0, 0.0, 0.0))
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
                @ Mat4.from_rotation(0.1 * pi, Vec3(1.0, 0.0, 0.0))
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
                @ Mat4.from_rotation(0.05 * pi, Vec3(1.0, 0.0, 0.0))
                @ Mat4.from_scale(Vec3(0.38, 0.1, 0.6))
            ),
        )

        self.add_node(
            geo_index=0,
            name='LeftUpperLeg',
            parent='Body',
            local_transform=Mat4.from_translation(Vec3(-0.15, -0.55, 0.3)),
            shape_transform=(
                Mat4.from_translation(Vec3(0.0, -0.18, 0.0))
                @ Mat4.from_scale(Vec3(0.16, 0.36, 0.16))
            ),
        )

        self.add_node(
            geo_index=0,
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
            geo_index=0,
            name='RightUpperLeg',
            parent='Body',
            local_transform=Mat4.from_translation(Vec3(-0.15, -0.55, -0.3)),
            shape_transform=(
                Mat4.from_translation(Vec3(0.0, -0.18, 0.0))
                @ Mat4.from_scale(Vec3(0.16, 0.36, 0.16))
            ),
        )

        self.add_node(
            geo_index=0,
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

    def animate(self, dt) :
        pass

if __name__ == "__main__" :

    window = PigeonWindow()
    window.run()