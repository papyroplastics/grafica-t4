import pyglet
from OpenGL.GL import *
import numpy as np
import libs.transformations as tr
from libs.easy_shaders import SimpleModelViewProjectionShaderProgram
import libs.gpu_shape as gp
from libs.basic_shapes import Shape

# GL SETUP
win = pyglet.window.Window()
win.set_exclusive_mouse(True)
win.set_mouse_visible(False)
program = SimpleModelViewProjectionShaderProgram()
glUseProgram(program.shaderProgram)
glClearColor(0.6, 0.8, 0.5, 1.0)
glEnable(GL_DEPTH_TEST)
glEnable(GL_CULL_FACE)

# CREATE TANK
tank_vertices = np.array([-0.5, 0.8, 0.0, 0.6, 0.6, 0.6,
                          -0.5,-0.8, 0.0, 0.6, 0.6, 0.6,
                           0.5,-0.8, 0.0, 0.6, 0.6, 0.6,
                           0.5, 0.8, 0.0, 0.6, 0.6, 0.6], dtype=np.float32)

tank_indices = np.array([0,1,2, 0,2,3], dtype=np.int32)

tank = gp.createGPUShape(program, Shape(tank_vertices, tank_indices))

# TRANSFORMS
model_loc = glGetUniformLocation(program.shaderProgram, "model")
view_loc = glGetUniformLocation(program.shaderProgram, "view")
proj_loc = glGetUniformLocation(program.shaderProgram, "projection")
PERSPECTIVE = tr.perspective(60, win.aspect_ratio, 0.5, 10)
glUniformMatrix4fv(proj_loc, 1, GL_TRUE, PERSPECTIVE)

# CREATE FLOOR
length = 30
count = 20
box_len = 2 * length / count
floor_vert = ()
color = True
for x in range(count):
    for z in range(count):
        for u in range(2):
            for v in range(2):
                floor_vert += ((x+v)*box_len-length,  (z+u)*box_len-length, -0.1)
                if color:
                    floor_vert += (0.43, 0.73, 0.43)
                else:
                    floor_vert += (0.3, 0.6, 0.3)
        color = not color
    color = not color

floor_ind = ()
for i in range(count**2):
    j = i*4
    floor_ind += (j, j+1, j+2, j+1, j+3, j+2)

floor = gp.createGPUShape(program, Shape(floor_vert, floor_ind))

# GLOBAL VARIABLES
theta = 0.0
rotate_left = False
rotate_right = False
forward = False
backward = False
position = np.zeros(3, dtype=np.float32)
direction = np.array([0.0, 1.0, 0.0], dtype=np.float32)

# PROGRAM
def update():
    global theta, position, direction
    if rotate_left:
        theta += 0.08
    if rotate_right:
        theta -= 0.08

    dir_sin = np.sin(theta)
    dir_cos = np.cos(theta)
    direction = np.array([-dir_sin, dir_cos, 0])

    if forward:
        position += direction * 0.08
    if backward:
        position -= direction * 0.08

    glUniformMatrix4fv(model_loc, 1, GL_TRUE, tr.translate(*position) @ tr.trigRotationZ(dir_sin, dir_cos))
    view = tr.lookAt(position + np.array([0,0,4]), position, np.array([0,1,0]))
    glUniformMatrix4fv(view_loc, 1, GL_TRUE, view)

@win.event
def on_draw():
    win.clear()
    program.drawCall(tank)
    glUniformMatrix4fv(model_loc, 1, GL_TRUE, tr.identity())
    program.drawCall(floor)
    update()

@win.event
def on_key_press(symbol, mods):
    global rotate_left, rotate_right, forward, backward
    if symbol == pyglet.window.key.A:
        rotate_left = True
    elif symbol == pyglet.window.key.D:
        rotate_right = True
    elif symbol == pyglet.window.key.W:
        forward = True
    elif symbol == pyglet.window.key.S:
        backward = True

@win.event
def on_key_release(symbol, mods):
    global rotate_left, rotate_right, forward, backward
    if symbol == pyglet.window.key.A:
        rotate_left = False
    elif symbol == pyglet.window.key.D:
        rotate_right = False
    elif symbol == pyglet.window.key.W:
        forward = False
    elif symbol == pyglet.window.key.S:
        backward = False

@win.event
def on_close():
    tank.clear()
    floor.clear()
    glDeleteProgram(program.shaderProgram)

pyglet.app.run()