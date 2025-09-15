import pyglet
from OpenGL.GL import *
import numpy as np
import libs.transformations as tr
from libs.easy_shaders import SimpleModelViewProjectionShaderProgram
import libs.gpu_shape as gp
from libs.basic_shapes import Shape

from OpenGL.GL.framebufferobjects import *
from PIL import Image

# GL SETUP
win = pyglet.window.Window(700,700)
program = SimpleModelViewProjectionShaderProgram()
glUseProgram(program.shaderProgram)
glClearColor(0.6, 0.8, 0.5, 1.0)
glEnable(GL_DEPTH_TEST)
glEnable(GL_CULL_FACE)

# CREATE FLOOR
length = 12
count = 12
box_len = 2 * length / count
floor_vert = ()
color = True
for x in range(count):
    for z in range(count):
        for u in range(2):
            for v in range(2):
                floor_vert += ((x+v)*box_len-length,  (z+u)*box_len-length, 0)
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

# CREATE WALLS
cosines = [np.cos(2*np.pi*i/64) for i in range(64)]
sines = [np.sin(2*np.pi*i/64) for i in range(64)]

wall_verts = tuple()
for i in range(64):
    wall_verts += (-sines[i]*10.5, cosines[i]*10.5, 0.0, 0.55, 0.6, 0.55,
                   -sines[i]*10.5, cosines[i]*10.5, 0.8, 0.71, 0.74, 0.7)

wall_inds = tuple()
for i in range(63):
    wall_inds += (i*2,i*2+1,i*2+2, i*2+1,i*2+3,i*2+2)
wall_inds += (126,127,0, 127,1,0)

wall = gp.createGPUShape(program, Shape(wall_verts, wall_inds))

top_verts = tuple()
for i in range(64):
    top_verts += (-sines[i]*10.5, cosines[i]*10.5, 0.8, 0.8, 0.8, 0.8)
top_verts += (-13, 13, 0.8, 0.4, 0.4, 0.4,
              -13,-13, 0.8, 0.4, 0.4, 0.4,
               13,-13, 0.8, 0.4, 0.4, 0.4,
               13, 13, 0.8, 0.4, 0.4, 0.4)

top_inds = tuple()
for i in range(16):
    top_inds += (i,64,i+1)
for i in range(16,32):
    top_inds += (i,65,i+1)
for i in range(32,48):
    top_inds += (i,66,i+1)
for i in range(48,63):
    top_inds += (i,67,i+1)
top_inds += (63,67,0, 65,16,64, 66,32,65, 67,48,66, 64,0,67)
    
top = gp.createGPUShape(program, Shape(top_verts, top_inds))

# TRANSFORMS
model_loc = glGetUniformLocation(program.shaderProgram, "model")
view_loc = glGetUniformLocation(program.shaderProgram, "view")
proj_loc = glGetUniformLocation(program.shaderProgram, "projection")
PERSPECTIVE = tr.perspective(100, win.aspect_ratio, 1, 11)
VIEW = tr.lookAt(np.array([0,0,10]), np.array([0,0,0]), np.array([0,1,0]))
glUniformMatrix4fv(proj_loc, 1, GL_TRUE, PERSPECTIVE)
glUniformMatrix4fv(view_loc, 1, GL_TRUE, VIEW)
glUniformMatrix4fv(model_loc, 1, GL_TRUE, tr.identity())

framebuffer = glGenFramebuffers(1)
glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)

texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture)

# Set the texture parameters
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

# Set the texture format and size
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, win.width, win.height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)

# Attach the texture to the framebuffer
glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0)

glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)

win.clear()
program.drawCall(floor)
program.drawCall(wall)
program.drawCall(top)

glReadBuffer(GL_COLOR_ATTACHMENT0)
pixels = glReadPixels(0, 0, win.width, win.height, GL_RGB, GL_UNSIGNED_BYTE)

image = Image.frombytes('RGB', (win.width, win.height), pixels)

image.save('output.jpg')

glDeleteFramebuffers(1, [framebuffer])
glDeleteTextures(1, [texture])
floor.clear()
wall.clear()
top.clear()
glDeleteProgram(program.shaderProgram)