import pyglet
pyglet.options['debug_gl'] = False
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.gl import *
from pyglet.math import Mat4, Vec3
from math import cos, sin, radians, pi

vertex_shader = """
    #version 330

    in vec3 position;
    in vec3 color;
    uniform mat4 model;
    uniform mat4 view;
    uniform mat4 proj;
    
    out vec3 newColor;
    void main()
    {
        gl_Position = proj * view * model * vec4(position, 1.0f);
        newColor = color;
    }
    """

fragment_shader = """
    #version 330

    in vec3 newColor;
    
    out vec4 outColor;
    void main()
    {
        outColor = vec4(newColor, 1.0f);
    }
    """

win = pyglet.window.Window()
win.set_exclusive_mouse(True)
win.set_mouse_visible(False)
glClearColor(0.3, 0.3, 0.3, 1.0)

vert_shader = Shader(vertex_shader, 'vertex')
frag_shader = Shader(fragment_shader, 'fragment')
program = ShaderProgram(vert_shader, frag_shader)
program.use()

glEnable(GL_DEPTH_TEST)
glEnable(GL_CULL_FACE)

def crearVerticesNave():
    pos_nave = (0.0, -0.2, -0.1,
                0.25, 0.0, -0.1,
                0.0,  0.25,-0.1,
               -0.25, 0.0, -0.1,
                0.0,  0.0, -0.4,
                0.0,  0.0,  1.0,

               -0.22,-0.06,-0.14,
               -0.5,  0.1,  0.5,
               -0.3,  0.42,-0.1,
               -0.23,-0.08,-0.14,

                0.22,-0.06,-0.14,
                0.5,  0.1,  0.5,
                0.3,  0.42,-0.1,
                0.23,-0.08,-0.14,
                
               -0.22,-0.03,-0.17,
               -0.5,  0.07, 0.4,
               -0.8, -0.15,-0.6,
               -0.22,-0.03,-0.17,
               -0.5, -0.0,  0.4,
               -0.8, -0.15,-0.6,
                
                0.22,-0.03,-0.17,
                0.5,  0.07, 0.4,
                0.8, -0.15,-0.6,
                0.22,-0.03,-0.17,
                0.5, -0.0,  0.4,
                0.8, -0.15,-0.6)

    color_nave = (0.6, 0.6, 0.9,
                  0.6, 0.6, 0.9,
                  0.6, 0.6, 0.9,
                  0.6, 0.6, 0.9,
                  0.7, 0.7, 0.9,
                  0.3, 0.3, 0.5,

                  0.4, 0.4, 0.8,
                  0.2, 0.2, 0.8,
                  0.2, 0.2, 0.8,
                  0.4, 0.4, 0.8,

                  0.4, 0.4, 0.8,
                  0.2, 0.2, 0.8,
                  0.2, 0.2, 0.8,
                  0.4, 0.4, 0.8,

                  0.6, 0.6, 0.9,
                  0.6, 0.6, 0.9,
                  0.55,0.55,1.0,
                  0.4, 0.4, 0.7,
                  0.4, 0.4, 0.7,
                  0.4, 0.4, 0.7,

                  0.6, 0.6, 0.9,
                  0.6, 0.6, 0.9,
                  0.55,0.55,1.0,
                  0.4, 0.4, 0.7,
                  0.4, 0.4, 0.7,
                  0.4, 0.4, 0.7)

    ind_nave = (0,4,1, 1,4,2, 2,4,3, 3,4,0, 3,5,2, 2,5,1, 1,5,0, 0,5,3,
                6,8,7, 9,7,8, 6,9,8, 9,6,7,
                10,11,12, 11,13,12, 10,12,13, 10,13,11,
                14,16,15, 17,18,19, 16,18,15, 14,15,18,
                22,20,21, 24,23,25, 24,22,21, 20,24,21)

    ind_lineas = (0,1, 1,2, 2,3, 3,0, 4,0, 4,1, 4,2, 4,3, 5,0,5,1, 5,2, 5,3,
                6,7, 7,8, 8,6, 6,9, 9,7, 9,8,
                10,11, 11,12, 12,10, 10,13, 13,11, 13,12,
                14,15, 15,16, 16,17, 17,18, 18,19, 15,18,
                24,21, 25,24, 24,23, 23,22, 22,21, 21,20)
    
    negro = (0.0,) *26

    return (program.vertex_list_indexed(count=26, mode=GL_TRIANGLES, indices=ind_nave,
                                        position=("fn", pos_nave), color = ("fn", color_nave)),
            program.vertex_list_indexed(count=26, mode=GL_LINES, indices=ind_lineas,
                                        position=("fn", pos_nave), color = ("fn", negro)),
            program.vertex_list_indexed(count=26, mode=GL_TRIANGLES, indices=ind_nave,
                                        position=("fn", pos_nave), color = ("fn", negro)))

def crearVerticesSuelo(n,l):
    pos_suelo = ()
    k = 2 * l / n
    for i in range(n):
        for j in range(n):
            for u in range(2):
                for v in range(2):
                    pos_suelo += ((i+u)*k-l, 0, (j+v)*k-l)

    blanco = (0.43, 0.73, 0.43) * 4
    negro = (0.3, 0.6, 0.3) * 4

    def crear_fila(bool):
        fila = ()
        for i in range(n):
            if bool:
                fila += blanco
                bool = False
            else:
                fila += negro
                bool = True
        return fila
    fila_blanca = crear_fila(True)
    fila_negra = crear_fila(False)

    color_suelo = ()
    for i in range(n):
        if i % 2 == 0:
            color_suelo += fila_blanca
        else:
            color_suelo += fila_negra

    ind_suelo = ()
    for i in range(n**2):
        j = i*4
        ind_suelo += (j, j+1, j+2, j+1, j+3, j+2)

    return program.vertex_list_indexed(count=n**2*4, mode=GL_TRIANGLES, indices=ind_suelo,
                                       position=("fn", pos_suelo), color = ("fn", color_suelo))

def crearCubo():
    pos = (-0.5, -0.5, 0.5, 0.5, -0.5, 0.5, 0.5, 0.5, 0.5, -0.5, 0.5, 0.5,
           -0.5, -0.5, -0.5, 0.5, -0.5, -0.5, 0.5, 0.5, -0.5, -0.5, 0.5, -0.5)
    color = (0.9, 0.1, 0.2, 0.1, 0.3, 0.9, 0.2, 0.5, 0.6, 0.1, 0.9, 0.1,
             0.5, 0.9, 0.1, 0.4, 0.2, 0.9, 0.9, 0.9, 0.1, 0.2, 0.5, 0.6)
    ind = (0,1,2,0,2,3,7,6,4,6,5,4,0,7,4,0,3,7,3,2,6,3,6,7,1,5,6,1,6,2,1,0,4,1,4,5)

    return program.vertex_list_indexed(count= 8, mode=pyglet.gl.GL_TRIANGLES, indices=ind,
                                       position=("fn",pos), color = ("fn",color))

def crearToro():
    senos =  [sin(radians(i)) for i in range(0,360,15)]
    cosenos =  [cos(radians(i)) for i in range(0,360,15)]

    def crearArco(ind):
        vertices = ()
        for i in range(24):
            vertices += ((2+cosenos[i])*cosenos[ind], senos[i], (2+cosenos[i])*senos[ind])
        return vertices

    pos = ()
    for i in range(24):
        pos += crearArco(i)

    color = ()
    for i in range(24):
        c = 0.0
        for j in range(24):
            color += (c,)*3
            if j >=12:
                c -= 0.08
            else:
                c += 0.08

    
    ind = ()
    for i in range(576):
        j = (i+24)%576
        k = (i+1)%576
        ind += (i, k, j, j, k, (i+25)%576)
    
    for i in ind:
        if i >= 576:
            print(i)

    return program.vertex_list_indexed(count=576, mode=GL_TRIANGLES, indices=ind,
                                       position=("fn", pos), color = ("fn", color))

def crearEnemigo(r,g,b):
    pos = (0, 0, 0,
           -0.5, 0, -0.4,
           0, 0, 0.4,
           0.5, 0, -0.4,
           
           0, 0.3, -0.15,
           -0.2, 0, -0.3,
           0, 0, 0.35,
           0.2, 0, -0.3)
    
    color = (0.6, 0.6, 0.9,
             0.6, 0.6, 0.9,
             0.3, 0.3, 0.6,
             0.6, 0.6, 0.9,
             r,g,b,
             r,g,b,
             r-0.2,g-0.2,b-0.2,
             r,g,b)
    
    ind = (0,1,2, 0,2,3, 4,5,6, 4,6,7)

    color2 = (0,) * 24
    ind2 = (0,1, 1,2, 2,3, 3,0, 4,5, 5,6, 6,7, 7,4, 4,6)

    return (program.vertex_list_indexed(count=8, mode=GL_TRIANGLES, indices=ind,
                                       position=("fn", pos), color = ("fn", color)),
            program.vertex_list_indexed(count=8, mode=GL_LINES, indices=ind2,
                                       position=("fn", pos), color = ("fn", color2)))

def rotacion_nave(c,s,c2,s2):
    return Mat4((c, -s2*s, c2*s, 0.0,
                 0.0, c2, s2, 0.0,
                 -s, -c*s2, c*c2, 0.0,
                 0.0, 0.0, 0.0, 1.0)).transpose()

def transformada_sombra(pos):
    x,y,z = pos
    return Mat4((1.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 0.0, 0.0,
                 0.0, 0.0, 1.0, 0.0,
                 0.05*x+0.2, -5, -0.5*y, 1.0))

def ad_infinitum(pos):
    x,y,z = pos
    return Mat4.from_translation((7*(x//7), -10, 7*(z//7)))

def rotacion_bonita(theta, x ,z):
    c = cos(theta)
    s = sin(theta)
    cc = c * c
    ss = s * s
    cs = c * s
    css = cs * s
    ccs = cs * c
    sss = ss * s

    return Mat4((cc,  cs+css, ss-ccs, 0,
                -cs, cc-sss, cs+css, 0,
                s,   -cs,    cc, 0,
                x, 0, z, 1))

def pos_sistema(alpha):
    return Mat4.from_translation(Vec3(4,3,-3)) @ Mat4.from_rotation(alpha, Vec3(0,1,0))

class Node:
    def __init__(self):
        self.transform = Mat4()
        self.children = ()
        self.mode = None

    def draw(self, parent_transform = Mat4()):
        new_transform = parent_transform @ self.transform
        for child in self.children:
            if type(child) == Node:
                child.draw(new_transform)
            else:
                program["model"] = new_transform
                child.draw(self.mode)

vl_nave, vl_lineas_nave, vl_sombra_nave = crearVerticesNave()
vl_suelo = crearVerticesSuelo(16,14)
vl_cubo = crearCubo()
vl_toro = crearToro()
vl_enemigo1, vl_enemigo_lineas = crearEnemigo(0.9, 0.3, 0.3)
vl_enemigo2, vl_enemigo_lineas = crearEnemigo(0.3, 0.9, 0.3)
vl_enemigo3, vl_enemigo_lineas = crearEnemigo(0.3, 0.3, 0.9)

nodos_naves = ()
nodos_lineas = ()
nodos_sombras = ()
for i in range(4):
    transf = Mat4.from_translation(Vec3(i//2-0.5, 0, i%2-0.5)*4)

    nodos_naves += (Node(),)
    nodos_naves[i].children += (vl_nave,)
    nodos_naves[i].mode = GL_TRIANGLES
    nodos_naves[i].transform = transf

    nodos_lineas += (Node(),)
    nodos_lineas[i].children += (vl_lineas_nave,)
    nodos_lineas[i].mode = GL_LINES
    nodos_lineas[i].transform = transf

    nodos_sombras += (Node(),)
    nodos_sombras[i].children += (vl_sombra_nave,)
    nodos_sombras[i].mode = GL_TRIANGLES
    nodos_sombras[i].transform = transf

nave_lineas = Node()
nave_lineas.mode = GL_LINES
nave_lineas.children = (vl_lineas_nave,) + nodos_lineas

nave_sombra = Node()
nave_sombra.mode = GL_TRIANGLES
nave_sombra.children += (vl_sombra_nave,) + nodos_sombras

nave = Node()
nave.mode = GL_TRIANGLES
nave.children += (vl_nave, nave_lineas) + nodos_naves

cubo = Node()
cubo.mode = GL_TRIANGLES
cubo.children += (vl_cubo,)

toro = Node()
toro.mode = GL_TRIANGLES
toro.children += (vl_toro,)

suelo = Node()
suelo.mode = GL_TRIANGLES
suelo.children += (vl_suelo,)

enemigo_sombra = Node()
enemigo_sombra.mode = GL_LINES
enemigo_sombra.children += (vl_enemigo_lineas,)

enemigo1 = Node()
enemigo1.mode = GL_TRIANGLES
enemigo1.children += (vl_enemigo1,enemigo_sombra)
enemigo1.transform = Mat4.from_translation(Vec3(0,0,2)) @ Mat4.from_rotation(pi/2, Vec3(0,1,0))

enemigo2 = Node()
enemigo2.mode = GL_TRIANGLES
enemigo2.children += (vl_enemigo2,enemigo_sombra)
enemigo2.transform = Mat4.from_translation(Vec3(sin(2*pi/3),0,cos(2*pi/3))*2) @ Mat4.from_rotation(pi*7/6, Vec3(0,1,0))

enemigo3 = Node()
enemigo3.mode = GL_TRIANGLES
enemigo3.children += (vl_enemigo3,enemigo_sombra)
enemigo3.transform = Mat4.from_translation(Vec3(-sin(2*pi/3),0,cos(2*pi/3))*2) @ Mat4.from_rotation(-pi/6, Vec3(0,1,0))

sistema_enemigos = Node()
sistema_enemigos.children += (enemigo1,enemigo2,enemigo3)

grafo = Node()
grafo.children += (suelo, nave, nave_sombra, cubo, toro, sistema_enemigos)

theta = 0.0
phi = 0.0
alpha = 0.0
rotate_left = False
rotate_right = False
forward = False
backward = False
position = Vec3(0,0,0)

proj = Mat4.orthogonal_projection(-win.aspect_ratio*4, win.aspect_ratio*4, -4, 4, 0.1, 50)
program['proj'] = proj

@win.event
def on_draw():
    win.clear()
    grafo.draw()

    global theta, alpha, position
    if rotate_left:
        theta += 0.05
    if rotate_right:
        theta -= 0.05
    
    alpha += 0.01

    c = cos(theta)
    s = sin(theta)
    c2 = cos(phi)
    s2 = sin(phi)

    direction = Vec3(s*c2,s2,c*c2)

    if forward:
        if position[1]<=0 and phi<0:
            direction[1] = 0
        position += direction * 0.05

    elif backward:
        if (position[1]<=0 and phi>0):
            direction[1] = 0
        position -= direction * 0.05

    nave.transform = Mat4.from_translation(position) @ rotacion_nave(c,s,c2,s2)
    nave_sombra.transform = transformada_sombra(position) @ nave.transform
    suelo.transform = ad_infinitum(position)
    cubo.transform = rotacion_bonita(alpha, -6, 2)
    toro.transform = rotacion_bonita(alpha,3,4) @ Mat4.from_scale(Vec3(0.5,0.5,0.5))
    sistema_enemigos.transform = pos_sistema(alpha*3)
    
    program['view'] = Mat4.look_at(position + Vec3(0,4,0), position, Vec3(0,0,1))  

@win.event
def on_mouse_motion(x, y, dx, dy):
    global phi
    if dy > 0.0 and phi < 0.785:
        phi += dy/600
    elif dy < 0.0 and phi > -0.785:
        phi += dy/600

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
    elif symbol == pyglet.window.key.ESCAPE:
        win.close()

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

pyglet.app.run()