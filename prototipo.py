import pyglet
from OpenGL.GL import *
import numpy as np
import ctypes
from OpenGL.GL.shaders import compileProgram, compileShader

vertex_shader = """
#version 330 core

layout (location=0) in vec3 vertexPos;
layout (location=1) in vec3 vertexColor;

out vec3 fragmentColor;

void main()
{
    gl_Position = vec4(vertexPos, 1.0);
    fragmentColor = vertexColor;
}"""

fragment_shader = """
#version 330 core

in vec3 fragmentColor;

out vec4 color;

void main()
{
    color = vec4(fragmentColor, 1.0);
}
"""

win = pyglet.window.Window(800, 600)
glClearColor(0.15, 0.15, 0.17, 1.0)
program = compileProgram(compileShader(vertex_shader, GL_VERTEX_SHADER),
                        compileShader(fragment_shader, GL_FRAGMENT_SHADER))
glUseProgram(program)

vertices = np.array((
    -0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
     0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
     0.0,  0.5, 0.0, 0.0, 0.0, 1.0
), dtype=np.float32)

vao = glGenVertexArrays(1)
glBindVertexArray(vao)
vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

@win.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT)
    glDrawArrays(GL_TRIANGLES, 0, 3)

@win.event
def on_close():
    glDeleteVertexArrays(1,(vao,))
    glDeleteBuffers(1,(vbo,))
    glDeleteProgram(program)
    print("mememoria liberada")

pyglet.app.run()