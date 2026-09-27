import math

class CubeGeometry : # unit cube, 원점 중심, 길이 1

    def __init__(self, color=(180, 180, 180, 255)) :
        
        self.vertices = (
            -0.5, -0.5, -0.5,
             0.5, -0.5, -0.5,
             0.5,  0.5, -0.5,
            -0.5,  0.5, -0.5,

            -0.5, -0.5,  0.5,
             0.5, -0.5,  0.5,
             0.5,  0.5,  0.5,
            -0.5,  0.5,  0.5,
        )

        self.indices = (
            4, 5, 6,  4, 6, 7,  # 앞
            0, 3, 2,  0, 2, 1,  # 뒤
            0, 4, 7,  0, 7, 3,  # 왼쪽
            1, 2, 6,  1, 6, 5,  # 오른쪽
            3, 7, 6,  3, 6, 2,  # 위
            0, 1, 5,  0, 5, 4,  # 아래
        )

        self.colors = tuple(color) * 8

class SphereGeometry : # unit sphere, 원점 1, 반지름 0.5

    def __init__(self, radius=0.5, stacks=18, sectors=24, color=(150, 160, 175, 255)):
        """
        x = radius × sin(phi) × cos(theta) \n
        y = radius × cos(phi) \n
        z = radius × sin(phi) × sin(theta)

        phi는 stack의 개수에 따라 pi를 나눔 - 위도 생성 \n
        theta 는 sector의 개수에 따라 2pi를 나눔 - 경도 생성
        """

        if stacks < 2:
            raise ValueError("stacks must be at least 2")

        if sectors < 3:
            raise ValueError("sectors must be at least 3")

        vertices = []
        colors = []
        indices = []

        for stack in range(stacks+1) :
            phi = math.pi * stack / stacks

            normal_y = math.cos(phi)
            ring_radius = math.sin(phi)

            for sector in range(sectors+1) :
                theta = 2 * math.pi * sector / sectors

                normal_x = ring_radius * math.cos(theta)
                normal_z = ring_radius * math.sin(theta)

                vertices.extend((radius*normal_x, radius*normal_y, radius*normal_z))
                colors.extend(color)

        ring_size = sectors + 1 # sector = 0일 때와 sector 최대일 때 0, 2pi로 같은 각도 나타냄

        for stack in range(stacks) :
            for sector in range(sectors) :
                current = stack * ring_size + sector #vertices에 들어간 index 구하는 것임
                next_ring = current + ring_size # 같은 vertex의 하나 아래쪽 ring 의 vertex의 index

                a = current
                b = next_ring
                c = next_ring + 1
                d = current + 1

                if stack != 0 :
                    indices.extend((a, d, c)) # z축이 화면 밖으로 나오는 방향이라 a d c가 반시계 방향

                if stack != stacks - 1:
                    indices.extend((a, c, b))

                """
                a ───── d
                │ ╲     │
                │   ╲   │
                │     ╲ │
                b ───── c
                """ 


        self.vertices = tuple(vertices)
        self.colors = tuple(colors)
        self.indices = tuple(indices)