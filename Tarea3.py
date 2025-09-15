import pyglet
from OpenGL.GL import *
import numpy as np
from numpy.random import rand, randn
import libs.transformations as tr
from libs.easy_shaders import FogModelViewProjectionShaderProgram
import libs.gpu_shape as gp
from libs.basic_shapes import Shape

input("""CONTROLES:
WASD y ratón: movimiento de la nave
R: Grabación de puntos de control
V: Activar/desactivar visualización del recorrido
1: Seguir recorrido
P: DO A BARREL ROLL
C: Cambio de camara

Cuidado al añadir muchos puntos de control sin una tarjeta gráfica dedicada
Presiona enter para comenzar...""")


# OPENGL SETUP
win = pyglet.window.Window()
win.set_exclusive_mouse(True)
win.set_mouse_visible(False)
program = FogModelViewProjectionShaderProgram()
glUseProgram(program.shaderProgram)
glEnable(GL_DEPTH_TEST)
glEnable(GL_CULL_FACE)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glClearColor(0.5, 0.5, 0.8, 1.0)

# CARGAR NAVE
with open("assets\ship_cords.txt", "r") as file:
    ship_vert = np.array(file.read().replace("\n"," ").split(" "))

count = len(ship_vert)//6
dark_vert = np.array(ship_vert).reshape([count,6])
dark_vert[:,3:] = np.zeros(([count,3]))
dark_vert = dark_vert.reshape([count*6])

ship_ind = (0,1,4, 1,2,4, 2,3,4, 3,0,4, 3,2,5, 2,1,5, 1,0,5, 0,3,5,
            6,7,8, 9,8,7, 6,8,9, 9,7,6, 
            10,12,11, 11,12,13, 10,13,12, 10,11,13, 
            14,15,16, 17,19,18, 16,15,18, 14,18,15,
            22,21,20, 24,25,23, 24,21,22, 20,21,24)

lines_ind = (0,1, 1,2, 2,3, 3,0, 4,0, 4,1, 4,2, 4,3, 5,0,5,1, 5,2, 5,3,
            6,7, 7,8, 8,6, 6,9, 9,7, 9,8,
            10,11, 11,12, 12,10, 10,13, 13,11, 13,12,
            14,15, 15,16, 16,17, 17,18, 18,19, 15,18,
            24,21, 25,24, 24,23, 23,22, 22,21, 21,20) 

ship = gp.createGPUShape(program, Shape(ship_vert, ship_ind))
shadow = gp.createGPUShape(program, Shape(dark_vert, ship_ind))
lines =  gp.createGPUShape(program, Shape(dark_vert, lines_ind))

shadow_matrix = np.array([[1.05, 0.0, 0.0, 0.0],
                          [0.0, 0.0, 0.0, 0.0],
                          [0.0, 0.1, 1.0, 0.0],
                          [0.0, 0.0, 0.0, 0.0]], dtype=np.float32)

# CREAR SUELO
length = 72
count = 48
box_len = 2 * length / count
floor_vert = ()
color = True
for x in range(count):
    for z in range(count):
        for u in range(2):
            for v in range(2):
                floor_vert += ((x+u)*box_len-length, -0.1, (z+v)*box_len-length)
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

# OBJETOS
cosines = [np.cos(2*np.pi*i/24) for i in range(24)]
sines = [np.sin(2*np.pi*i/24) for i in range(24)]
def create_torus(r1, r2, c1, c2):
    vertices = []
    for i in range(24):
        c = 0.0
        for j in range(24):
            vertices += [(r1+r2*cosines[j])*cosines[i], r2*sines[j], (r1+r2*cosines[j])*sines[i]]
            vertices += [c1[0,i]*c + c2[0,i]*(1-c) for i in range(3)]
            if j >=12:
                c -= 0.08
            else:
                c += 0.08

    indices = []
    for i in range(576):
        j = (i+24)%576
        k = (i+1)%576
        indices += [i, k, j, j, k, (i+25)%576]

    return gp.createGPUShape(program, Shape(vertices, indices))

# BATTLE ROLL
class BattleRoll:
    def __init__(self):
        self.t = 0.0
        self.active = False
        self.step = 1/90
    
    def transform(self):
        if self.t >= 1:
            self.active = False
            self.t = 0
            return tr.identity()
        else:
            angle = 0.8*self.t + 0.1*(1-np.cos(np.pi*self.t)) - 0.2*np.sin(2*np.pi*self.t)
            self.t += self.step
            return tr.rotationZ(2*np.pi*angle)

# HERMITE CURVE
class HermiteCurve:
    def __init__(self):
        self.t = 0.0
        self.n = 0
        self.step = 0.0
        self.poss = [None]
        self.dirs = [[None,None]]
        self.start_dir = np.empty(3)
        self.next_pos = np.empty(3)
        self.active = False
        self.path3D = tuple()
        self.hermite_matrix = np.array([[ 2,-2, 1, 1],
                                        [-3, 3,-2,-1],
                                        [ 0, 0, 1, 0],
                                        [ 1, 0, 0, 0]])

    def hermite_point(self, t, pos1, dir1, pos2, dir2):
        pos_matrix = np.vstack([pos1, pos2, dir1, dir2])
        t_arr = np.array([t**3, t**2, t, 1], dtype=np.float32)
        return t_arr @ self.hermite_matrix @ pos_matrix
    
    def start(self, pos, dir):
        if len(self.poss) > 1:
            self.active = True
            difference = np.linalg.norm(self.poss[1] - pos)
            factor = np.log(difference)
            if difference > 3: 
                self.step = 1 / (40 * factor)
                self.dirs[0][1] = dir * 5 * factor
                self.dirs[1][0] = self.start_dir * 5 * factor
            else:
                self.step = 1/20
                self.dirs[0][1] = dir
                self.dirs[1][0] = self.start_dir
            self.poss[0] = pos
            self.next_pos = self.next_curve_position()

    def end(self):
        self.active = False
        self.t = 0.0
        self.n = 0
        
        global phi, theta
        final_dir = self.dirs[-1][1]
        phi = np.arcsin(final_dir[1]/np.linalg.norm(final_dir))
        if final_dir[2] == 0:
            theta = -(np.pi/2)*(final_dir[0]/abs(final_dir[0]))
        else:
            theta = np.arctan(final_dir[0]/final_dir[2])
            if final_dir[2] > 0:
                theta += np.pi

    def next_curve_position(self):
        self.t += self.step

        if self.t >= 1:
            self.t -= 1
            self.n += 1
            if self.n == len(self.poss)-1:
                self.end()
                return self.poss[-1]
            else:
                difference = np.linalg.norm(self.poss[self.n+1] - self.poss[self.n])
                if difference > 2:
                    self.step = 1 / (40 * np.log(difference))
                else:
                    self.step = 1/20
                
        return self.hermite_point(self.t, self.poss[self.n], self.dirs[self.n][1], self.poss[self.n+1], self.dirs[self.n+1][0])

    def update_pos(self):
        newPos = np.array(self.next_pos)
        self.next_pos = self.next_curve_position()

        newDir = self.next_pos - newPos
        newDir = newDir / np.linalg.norm(newDir)

        return newPos, newDir
    
    def new_point(self, pos, dir):
        if len(self.poss) == 1:
            self.start_dir = np.array(dir)
            self.dirs += [[np.array(dir),np.array(dir)]]
        else:
            norm = np.linalg.norm(pos - self.poss[-1])
            if norm > 2:
                self.dirs += [[np.array(dir),np.array(dir)]]
                log = 7 * np.log(norm)
                self.dirs[-1][0] *= log
                self.dirs[-2][1] *= log
                for t in range(int(log)):
                    self.path3D += (create_midpoint(self.hermite_point(t/int(log),self.poss[-1],self.dirs[-2][1],pos,self.dirs[-1][0])),)
            elif norm > 0.5:
                self.dirs += [[np.array(dir),np.array(dir)]]
            else:
                return
        self.poss += [np.array(pos)]
        self.path3D += (create_checkpoint(pos, dir),)

    def clear(self):
        for node in self.path3D:
            node.clear()
    def draw_3d_path(self):
        for node in self.path3D:
            node.draw()

pyramid_vertices = np.array([0.1, 0.1, 0.1, 0.2, 0.2, 0.8,
                            -0.1, 0.1, 0.1, 0.2, 0.2, 0.8,
                            -0.1,-0.1, 0.1, 0.2, 0.2, 0.8,
                             0.1,-0.1, 0.1, 0.2, 0.2, 0.8,
                             0.0, 0.0,-0.25, 0.4, 0.4, 0.8], dtype=np.float32)
pyramid_indices = np.array([0,1,2, 0,2,3, 0,4,1, 1,4,2, 2,4,3, 3,4,0])
pyramid_gpushape = gp.createGPUShape(program, Shape(pyramid_vertices, pyramid_indices))

def create_checkpoint(pos, dir):
    s2 = dir[1]
    c2 = np.sqrt(1-s2**2)
    s = -dir[0] / c2
    c = -dir[2] / c2

    node = SimplerNode()
    node.child= pyramid_gpushape
    node.transform = tr.translate(*pos) @ tr.trigRotationY(s,c) @ tr.trigRotationX(s2,c2)
    return node

sphere_vertices = [0, 1, 0, 3, 3, 8]
angles = [np.pi/4,0,-np.pi/4]
for a in angles:
    for i in range(8):
        sphere_vertices += [np.sin(np.pi*i/4)*np.cos(a), np.sin(a), np.cos(np.pi*i/4)*np.cos(a), 3, 3, 8]
sphere_vertices += [0,-1, 0, 3, 3, 8]
sphere_vertices = np.array(sphere_vertices, dtype=np.float32) * 0.1

sphrere_indices = []
for i in range(1,9):
    sphrere_indices += [0,i,i%8+1, i,8+i,i%8+9, i,i%8+9,i%8+1]
sphrere_indices = np.array(sphrere_indices)
inverted = np.ones(len(sphrere_indices))*26-(np.array(sphrere_indices)+np.ones(len(sphrere_indices)))
sphrere_indices = np.hstack((sphrere_indices, inverted))
sphrere_gpushape = gp.createGPUShape(program, Shape(sphere_vertices, sphrere_indices))

def create_midpoint(pos):
    node = SimplerNode()
    node.child = sphrere_gpushape
    node.transform = tr.translate(*pos)
    return node

# CREATE SCENEGRAPH
class Node:
    def __init__(self):
        self.transform = tr.identity()
        self.children = []
        self.mode = GL_TRIANGLES

    def draw(self, parent_transform = tr.identity()):
        new_transform = parent_transform @ self.transform
        for child in self.children:
            if isinstance(child, Node):
                child.draw(new_transform)
            else:
                glUniformMatrix4fv(model_loc, 1, GL_TRUE, new_transform)
                program.drawCall(child, self.mode)

    def clear(self):
        for child in self.children:
            child.clear()

class SimplerNode:
    def __init__(self):
        self.transform = tr.identity()
        self.child = None
    def draw(self):
        glUniformMatrix4fv(model_loc, 1, GL_TRUE, self.transform)
        program.drawCall(self.child, GL_TRIANGLES)
    def clear(self):
        self.child.clear()

donuts = []
for i in range(4):
    torusNode = Node()
    torusNode.children += [create_torus(2.5+rand()*2, 0.3+rand()*2, rand(1,3), rand(1,3))]
    torusNode.transform = tr.translate(40*rand()-20,20*rand()+6,40*rand()-20)@tr.rotationY(2*np.pi*(rand()))@tr.rotationX(np.pi*(0.5+0.5*randn()))
    donuts.append(torusNode)

linesNode = Node()
linesNode.mode = GL_LINES
linesNode.children += [lines]

shipNode = Node()
shipNode.children += [ship, linesNode]

floorNode = Node()
floorNode.children += [floor]

shadowNode = Node()
shadowNode.children += [shadow]

scene = Node()
scene.children += [shipNode, floorNode, shadowNode] + donuts


# SET TRANSFORMS
model_loc = glGetUniformLocation(program.shaderProgram, "model")
viewProj_loc = glGetUniformLocation(program.shaderProgram, "viewProj")
shipPos_loc = glGetUniformLocation(program.shaderProgram, "shipPos")
PERSPECTIVE = tr.perspective(60, win.aspect_ratio, 0.5, 100)
ORTHOGRAPHIC = tr.ortho(-win.aspect_ratio*4, win.aspect_ratio*4, -4, 4, 0.1, 50)

# Programa :D
theta = 0.0
phi = 0.0
rotate_left = False
rotate_right = False
forward = False
backward = False
visible_path = True
third_person = True
position = np.array([0, 6, 0], dtype=np.float32)
direction = np.array([0, 0, -1], dtype=np.float32)
animation = HermiteCurve()
roll = BattleRoll()

def updateScenegraph():
    global theta, position, direction
    if animation.active:
        position, direction = animation.update_pos()
        s2 = direction[1]
        c2 = np.sqrt(1-s2**2)
        s = -direction[0] / c2
        c = -direction[2] / c2

    else:
        if rotate_left:
            theta += 0.05
        if rotate_right:
            theta -= 0.05

        s = np.sin(theta)
        c = np.cos(theta)
        s2 = np.sin(phi)
        c2 = np.cos(phi)

        direction = np.array((-s*c2,s2,-c*c2))

        if forward:
            if position[1]<=4 and phi<0:
                position += direction * np.array([0.08, 0.0, 0.08])
            else:
                position += direction * 0.08

        elif backward:
            if position[1]<=4 and phi>0:
                position -= direction * np.array([0.08, 0.0, 0.08])
            else:
                position -= direction * 0.08

    if roll.active:
        shipNode.transform = tr.translate(*position) @ tr.trigRotationY(s,c) @ tr.trigRotationX(s2,c2) @ roll.transform()
    else:
        shipNode.transform = tr.translate(*position) @ tr.trigRotationY(s,c) @ tr.trigRotationX(s2,c2)

    if third_person:
        view = tr.lookAt(position - tr.scale(4,0.8,4)[:3,:3] @ direction, position, np.array([0,1,0]))
        glUniformMatrix4fv(viewProj_loc, 1, GL_TRUE, PERSPECTIVE @ view)
    else:
        view = tr.lookAt(position * np.array([1,0,1]) + np.array([0,49,0]), position, np.array([0,0,-1]))
        glUniformMatrix4fv(viewProj_loc, 1, GL_TRUE, ORTHOGRAPHIC @ view)

    glUniform3f(shipPos_loc, *position)
    floorNode.transform = tr.translate(6*(position[0]//6), 0, 6*(position[2]//6))
    shadowNode.transform = shadow_matrix @ shipNode.transform

@win.event
def on_draw():
    win.clear()
    scene.draw()
    if visible_path:
        animation.draw_3d_path()
    updateScenegraph()
    
@win.event
def on_mouse_motion(x, y, dx, dy):
    global phi
    if not animation.active:
        if dy > 0.0 and phi < 0.785:
            phi += dy/600
        elif dy < 0.0 and phi > -0.785:
            phi += dy/600

@win.event
def on_key_press(symbol, mods):
    global rotate_left, rotate_right, forward, backward, visible_path, third_person
    if symbol == pyglet.window.key.A:
        rotate_left = True
    elif symbol == pyglet.window.key.D:
        rotate_right = True
    elif symbol == pyglet.window.key.W:
        forward = True
    elif symbol == pyglet.window.key.S:
        backward = True
    elif symbol == pyglet.window.key.R and not animation.active:
        animation.new_point(position, direction)
    elif symbol == pyglet.window.key._1 and not animation.active:
        animation.start(position, direction)
    elif symbol == pyglet.window.key.V:
        visible_path = not visible_path
    elif symbol == pyglet.window.key.P and not roll.active:
        roll.active = True
    elif symbol == pyglet.window.key.C:
        third_person = not third_person
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

@win.event
def on_close():
    scene.clear()
    animation.clear()
    glDeleteProgram(program.shaderProgram)

pyglet.app.run()