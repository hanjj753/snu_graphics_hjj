#!/usr/bin/env python

import pyglet
from pyglet.gl import *
from pyglet.math import Mat4, Vec3
import sys, math

import camera
width  = 1000
height = 1000

mouseRotatePressed = False
mouseMovePressed   = False
mouseDollyPressed   = False

window = pyglet.window.Window( width, height, resizable=True, caption="Trackball Viewer" )
batch = pyglet.graphics.Batch()
program = pyglet.graphics.get_default_shader()

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
def on_key_press( key, mods ):	
	if key==pyglet.window.key.Q:
		pyglet.app.exit()
		
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
		camera.beginRotate(x, y)
		mouseMovePressed   = False
		mouseRotatePressed = True
		mouseDollyPressed   = False

@window.event
def on_mouse_drag( x, y, dx, dy, button, mods ):	
	if mouseRotatePressed:
		camera.rotate(x, y)
	elif mouseMovePressed:
		camera.move(dx/width, dy/height, 0.0)
	elif mouseDollyPressed:
		camera.zoom(dy/height)	


glClearColor(0.0, 0.1, 0.3, 1.0)
glEnable(GL_DEPTH_TEST)
glClearDepth(1.0)
glDepthFunc(GL_LESS)

#
# Add your geometry here.
#
scene = pyglet.model.load("logo3d.obj")
models = scene.create_models(batch=batch)
		
camera.resize( window, width, height )
	
pyglet.app.run()
