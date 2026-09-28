import pyglet

from pyglet.gl import glClearColor, glEnable, glViewport, GL_DEPTH_TEST, GL_CULL_FACE, GL_TRIANGLES
from pyglet.math import Mat4, Vec3

from shader import create_program, create_vertex_list
from primitives import Geometry

class Node :
    
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

class RenderWindow(pyglet.window.Window) :

    def __init__(self, geometry_list:list[Geometry], width=1280, height=720, caption="Window", resizable=True, camera_position=Vec3(3, 3, 3), background_color=(1.0, 1.0, 1.0, 1.0)) :
        super().__init__(width=width, height=height, caption=caption, resizable=resizable)

        glClearColor(*background_color)
        glEnable(GL_DEPTH_TEST) # 겹쳤을 떄 앞에 있는 면을 남김
        glEnable(GL_CULL_FACE)  # 큐브 뒷면 그리지 않음

        self.camera_position = camera_position
        self.camera_setup()
        self.elapsed_time = 0

        self.program = create_program()

        self.geo_list = []
        for geometry in geometry_list :
            self.geo_list.append(create_vertex_list(self.program, geometry))

        self.node_dict = {"root" : Node()}

    def add_node(self, geo_index:int, name:str, parent:str="root", local_transform:Mat4=Mat4(), shape_transform:Mat4=Mat4()) :

        if name in self.node_dict : raise ValueError("Node name Overlapping.")

        new_node = Node(self.geo_list[geo_index])
        new_node.local_transform = local_transform
        new_node.shape_transform = shape_transform
        self.node_dict[name] = new_node
        self.node_dict[parent].add_child(new_node)

    def camera_setup(self) :

        # Camera 셋업
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
        self.node_dict["root"].draw(self.program)
        self.program.stop() # Shader 비활성화

    def animate(self, dt) :
        pass

    def update(self, dt) :
        self.elapsed_time += dt

        self.animate(dt)

        self.node_dict["root"].update_world()

    def on_resize(self, width, height) :

        glViewport(0, 0, *self.get_framebuffer_size())
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
