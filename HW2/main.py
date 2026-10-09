import pyglet
from pyglet.math import Vec3
from pyglet.gl import *
from camera import TrackballCamera
from pathlib import Path
from io import StringIO
import re

# 왼쪽 아래를 (0, 0, 0)으로 놓았을 때 Cornell box의 정 중앙의 좌표가 (1.45, 1.5, -1.5) 
center = Vec3(1.45, 1.50, -1.50)
eye = Vec3(1.45, 1.50, 5.00) # camera가 (1.45, 1.5, 5)
fov = 60.8

width = 960
height = 720

mouseRotatePressed = False
mouseMovePressed   = False
mouseDollyPressed   = False

camera = TrackballCamera(eye=eye, center=center, fov=fov)
window = pyglet.window.Window( width, height, resizable=True, caption="Cornell Box" )
batch = pyglet.graphics.Batch()

@window.event
def on_resize(width, height):
    camera.resize( window, width, height )
    return pyglet.event.EVENT_HANDLED

@window.event
def on_draw():
	window.clear()
	camera.apply(window)
	batch.draw()
		
@window.event
def on_mouse_release( x, y, button, mods ):
	global mouseRotatePressed, mouseMovePressed, mouseDollyPressed

	mouseMovePressed   = False
	mouseRotatePressed = False
	mouseDollyPressed   = False

@window.event
def on_mouse_press( x, y, button, mods ):
	global mouseRotatePressed, mouseMovePressed, mouseDollyPressed

	if button & pyglet.window.mouse.LEFT and mods & pyglet.window.key.MOD_SHIFT:
		mouseMovePressed   = True
		mouseRotatePressed = False
		mouseDollyPressed   = False
	elif button & pyglet.window.mouse.LEFT and mods & pyglet.window.key.MOD_CTRL:
		mouseMovePressed   = False
		mouseRotatePressed = False
		mouseDollyPressed   = True
	elif button & pyglet.window.mouse.LEFT:
		camera.begin_rotate(x, y)
		mouseMovePressed   = False
		mouseRotatePressed = True
		mouseDollyPressed   = False

@window.event
def on_mouse_drag( x, y, dx, dy, button, mods ):	
	if mouseRotatePressed:
		camera.rotate(x, y)
	elif mouseMovePressed:
		camera.move(dx/window.width, dy/window.height, 0.0)
	elif mouseDollyPressed:
		camera.zoom(dy/window.height)

@window.event
def on_key_press(key, modifiers):
    if key == pyglet.window.key.R:
        camera.reset()

    elif key == pyglet.window.key.Q:
        pyglet.app.exit()	


glClearColor(0.0, 0.1, 0.3, 1.0)
glEnable(GL_DEPTH_TEST)
glClearDepth(1.0)
glDepthFunc(GL_LESS)


obj_path = Path("models/cornell_scene.obj")
obj_text = obj_path.read_text(encoding="utf-8")
obj_text = re.sub(r"(?m)^g(\s+)", r"o\1", obj_text) # pyglet이 무시하는 Blender의 group 지시문을 object 지시문으로 변환

scene = pyglet.model.load( str(obj_path), file=StringIO(obj_text))
models = scene.create_models(batch=batch)
camera.resize(window, width, height)

pyglet.app.run()