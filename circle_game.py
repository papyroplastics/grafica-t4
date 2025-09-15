import pyglet
from OpenGL.GL import *
import numpy as np
import libs.transformations as tr
from libs.easy_shaders import SimpleModelViewProjectionShaderProgram, SimpleTextureShaderProgram
import libs.gpu_shape as gp
from libs.basic_shapes import Shape
from time import time
from PIL import Image


# GL SETUP
win = pyglet.window.Window(700,700)
tex_program = SimpleTextureShaderProgram()
program = SimpleModelViewProjectionShaderProgram()
glEnable(GL_DEPTH_TEST)
glEnable(GL_CULL_FACE)

# CREATE TEXTURE
glUseProgram(tex_program.shaderProgram)

background_verts = [
    -1,  1, 0.9999, 0, 0,
    -1, -1, 1, 0, 1,
     1, -1, 1, 1, 1,
     1,  1, 1, 1, 0]

background_inds = [0,1,2, 0,2,3]

background = gp.createGPUShape(tex_program, Shape(background_verts, background_inds))

texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

image = Image.open("assets\\background.png")
image_data = np.array(image.convert("RGBA"))
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_data.shape[1], image_data.shape[0], 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
glUniform1i(glGetUniformLocation(tex_program.shaderProgram, "samplerTex"), 0)
image.close()
background.texture = texture

# CREATE TANK
glUseProgram(program.shaderProgram)

cosines = [np.cos(2*np.pi*i/24) for i in range(24)]
sines = [np.sin(2*np.pi*i/24) for i in range(24)]

car_verts = tuple()
for i in range(24):
    car_verts += (-sines[i]*0.55, cosines[i]*0.55, 0.25,
                  -sines[i]*0.6, cosines[i]*0.6, 0.15,
                  -sines[i]*0.95, cosines[i]*0.95, 0.15,
                  -sines[i]*1.1, cosines[i]*1.1, 0.0)
car_verts += (0.0, 0.0, 0.6,
              0.0, 0.0, 0.4)
car_verts = np.array(car_verts, dtype=np.float32).reshape((98,3))

blue_car_color = np.array((0.35, 0.35, 0.8,
                           0.6, 0.25, 0.6,
                          0.7, 0.7, 0.7, 
                          0.5, 0.5, 0.5) * 24 + (0.3, 0.3, 0.7, 0.4, 0.4, 0.7)).reshape((98,3))

red_car_color = np.array((0.8, 0.35, 0.35,
                          0.6, 0.25, 0.25,
                          0.7, 0.7, 0.7, 
                          0.5, 0.5, 0.5) * 24 + (0.7, 0.3, 0.3, 0.6, 0.4, 0.4)).reshape((98,3))

#car_shade = np.hstack((car_verts, np.zeros((98,3), dtype=np.float32))).reshape((98*6))
blue_car_verts = np.hstack((car_verts, blue_car_color)).reshape((98*6))
red_car_verts = np.hstack((car_verts, red_car_color)).reshape((98*6))

car_inds = tuple()
for i in range(0,23*4,4):
    j = i+2
    car_inds += (96,i,i+4, 97,j,j+4, i,i+1,i+5, i,i+5,i+4, j,j+1,j+5, j,j+5,j+4)
car_inds += (96,92,0, 97,94,2, 92,93,1, 92,1,0, 94,95,3, 94,3,2)

blue_car = gp.createGPUShape(program, Shape(blue_car_verts, car_inds))
red_car = gp.createGPUShape(program, Shape(red_car_verts, car_inds))

# CREATE SQUERE
squere_verts = [-0.7, 0.7, 0.7, 0.8, 0.8, 0.8,
                -0.7,-0.7, 0.7, 0.8, 0.8, 0.8,
                 0.7,-0.7, 0.7, 0.8, 0.8, 0.8,
                 0.7, 0.7, 0.7, 0.8, 0.8, 0.8,
                -0.7, 0.7, 0.0, 0.6, 0.6, 0.6,
                -0.7,-0.7, 0.0, 0.6, 0.6, 0.6,
                 0.7,-0.7, 0.0, 0.6, 0.6, 0.6,
                 0.7, 0.7, 0.0, 0.6, 0.6, 0.6]
squere_inds = [0,1,2, 0,2,3, 0,4,5, 0,5,1, 1,5,6, 1,6,2, 2,6,7, 2,7,3, 3,7,4, 3,4,0]

squere = gp.createGPUShape(program, Shape(squere_verts, squere_inds))


# DYNAMIC OBJECT
circle_bbox = [np.array([-1.1,1.1]), np.array([-1.1,-1.1]), np.array([1.1,-1.1]), np.array([1.1,1.1])]
l = 1.578
fast_squere_bbox = [np.array([-l,l]), np.array([-l,-l]), np.array([l,-l]), np.array([l,l])]
l = 0.7
squere_bbox = [np.array([-l,l]), np.array([-l,-l]), np.array([l,-l]), np.array([l,l])]

class Player:
    def __init__(self, x, y, gpushape):
        self.pos = np.array([x, y], dtype=np.float32)
        self.speed = np.zeros(2, dtype=np.float32)
        self.acc = np.zeros(2, dtype=np.float32)
        self.dash_cd = time()
        self.squere_dc = time()
        self.gpushape = gpushape

    def update_pos(self, dt, destination):
        self.speed *= 0.97
        if mouse_press:
            if np.any(self.pos != destination):
                self.acc = destination - self.pos
                self.acc /= np.linalg.norm(self.acc)
                self.speed += self.acc * 6 * dt
        self.pos += self.speed * 6 * dt

    def dash(self, destination):
        if np.any(self.pos != destination) and self.dash_cd + 1.5 < time():
            direction = destination - self.pos
            direction /= np.linalg.norm(direction)
            self.speed *= 0.5
            self.speed += direction * 4
            self.dash_cd = time()

    def trow_squere(self):
        if self.squere_dc + 1 < time():
            direction = world_mouse_pos - self.pos
            if direction[0] != 0:
                direction /= np.linalg.norm(direction)
                angle = np.arctan(direction[1]/direction[0])
                squere_list.append(SquereBlock(*(self.pos + direction*3), angle, (direction+self.speed)*6))
            elif direction[1] != 0:
                direction /= np.linalg.norm(direction)
                squere_list.append(SquereBlock(*(self.pos + direction*3), 0, (direction+self.speed)*6))
            self.squere_dc = time()

    def draw(self):
        glUniformMatrix4fv(model_loc, 1, GL_TRUE, tr.translate(*self.pos, 0))
        program.drawCall(self.gpushape)
    
    def crash(self, enemy):
        dif = enemy.pos - self.pos
        for point in circle_bbox:
            x, y = np.abs(dif - point)

            if x < 1.1 and y < 1.1:
                dif_norm = np.dot(dif,dif)
                if dif_norm < 4.84:

                    speed_change = np.zeros(2)
                    player_sp_proj = np.dot(dif, self.speed)
                    enemy_sp_proj = np.dot(dif, enemy.speed)

                    if player_sp_proj > 0:
                        speed_change -= player_sp_proj * dif / dif_norm
                    if enemy_sp_proj < 0:
                        speed_change += enemy_sp_proj * dif / dif_norm
                    self.speed += speed_change
                    enemy.speed -= speed_change
                    break
    
    def fast_cube_colision(self, cube):
        dif = cube.pos - self.pos
        for point in fast_squere_bbox:
            x, y = np.abs(dif + point)
            if x < 1.578 and y < 1.578:
                self.cube_colision(cube, dif)
                break

    def cube_colision(self, cube, dif):
        poss = []
        diffs = []
        for point in squere_bbox:
            point_pos = cube.pos + cube.rotmat[:2,:2] @ point
            poss.append(point_pos)
            dif_to_point = np.linalg.norm(point_pos - self.pos)
            diffs.append(dif_to_point)

        ind1 = diffs.index(min(diffs))
        a = diffs.pop(ind1)
        ind2 = diffs.index(min(diffs))
        b = diffs[ind2]
        c = 1.4
        

        s = (a+b+c)/2
        area = np.sqrt(s*(s-a)*(s-b)*(s-c))
        dist = 2 * area / c

        if dist < 1.1:
            dif_norm = np.dot(dif,dif)
            speed_change = np.zeros(2)
            player_sp_proj = np.dot(dif, self.speed)
            cube_sp_proj = np.dot(dif, enemy.speed)

            if player_sp_proj > 0:
                speed_change -= player_sp_proj * dif / dif_norm
            if cube_sp_proj < 0:
                speed_change += cube_sp_proj * dif / dif_norm
            self.speed += speed_change * 0.4
            cube.speed -= speed_change * 1.5

            if ind1 == ind2-1:
                cube.rot += speed_change[0] * 0.5
            else:
                cube.rot -= speed_change[0] * 0.5

class Enemy(Player):
    def __init__(self, x, y, gpushape):
        self.pos = np.array([x, y], dtype=np.float32)
        self.speed = np.zeros(2, dtype=np.float32)
        self.acc = np.zeros(2, dtype=np.float32)
        self.gpushape = gpushape
        self.destination = (np.random.random_sample(2) * 14) - (np.ones(2) * 7)
        self.alive = True

    def update_ia(self, dt):
        if self.alive:
            self.speed *= 0.97
            direction = self.destination - self.pos
            if abs(np.sum(direction)) > 0.5:
                self.acc = direction
                self.acc /= np.linalg.norm(self.acc)
                self.speed += self.acc * 6 * dt
            else:
                self.destination = (np.random.random_sample(2) * 13) - (np.ones(2) * 6.5)
            self.pos += self.speed * 6 * dt
            if np.dot(self.pos, self.pos) > 109.15:
                self.alive = False
                self.pos = np.ones(2) * 13

    def draw(self):
        if self.alive:
            glUniformMatrix4fv(model_loc, 1, GL_TRUE, tr.translate(*self.pos, 0))
            program.drawCall(self.gpushape)


class SquereBlock:
    def __init__(self, x, y, angle, speed): 
        self.pos = np.array([x, y], dtype=np.float32)
        self.speed = np.array(speed, dtype=np.float32)
        self.acc = np.zeros(2, dtype=np.float32)
        self.angle = angle
        self.rot = (np.random.random_sample() * 3 + 1) * np.random.choice(np.array([-1,1]))
        self.rotmat = tr.identity()
    
    def update(self, dt):
        self.speed *= 0.99
        self.rot *= 0.99
        self.angle += self.rot * dt
        self.pos += self.speed * dt

    def draw(self):
        self.rotmat = tr.rotationZ(self.angle)
        model = tr.translate(*self.pos,0) @ self.rotmat
        glUniformMatrix4fv(model_loc, 1, GL_TRUE, model)
        program.drawCall(squere)
    
    def fast_cube_colision(self, other):
        dif = other.pos - self.pos
        for point in fast_squere_bbox:
            x, y = np.abs(dif + point)
            if x < 1.578 and y < 1.578:
                self.cube_colision(other, dif)
                break
                 
    def cube_colision(self, other, dif):
        for point in squere_bbox:
            x,y = self.rotmat[:2,:2] @ (other.rotmat[:2,:2] @ point + dif)
            if abs(x) < 0.7 and abs(y) < 0.7:
                dif_norm = np.dot(dif, dif)
                speed_change = np.zeros(2)
                self_sp_proj = np.dot(dif, self.speed)
                enemy_sp_proj = np.dot(dif, enemy.speed)

                if self_sp_proj > 0:
                    speed_change -= self_sp_proj * dif / dif_norm
                if enemy_sp_proj < 0:
                    speed_change += enemy_sp_proj * dif / dif_norm
                self.speed += speed_change
                other.speed -= speed_change
                
                pt = np.array([x,y])
                pt_dot = np.dot(pt,pt)
                sp = other.speed - self.speed
                speed_proj = np.dot(pt,sp) * pt / pt_dot
                perpendicular = sp - speed_proj
                rot = np.linalg.norm(perpendicular) * 0.1
                
                if x > 0.5:
                    if y > 0:
                        self.rot += rot
                    else:
                        self.rot -= rot
                elif x < -0.5:
                    if y > 0:
                        self.rot -= rot
                    else:
                        self.rot += rot
                elif y > 0.5:
                    if x > 0:
                        self.rot -= rot
                    else:
                        self.rot += rot
                elif y < -0.5:
                    if x > 0:
                        self.rot += rot
                    else:
                        self.rot -= rot
                else:
                    self.rot += rot

                break


# TRANSFORMS
model_loc = glGetUniformLocation(program.shaderProgram, "model")
view_loc = glGetUniformLocation(program.shaderProgram, "view")
proj_loc = glGetUniformLocation(program.shaderProgram, "projection")
PERSPECTIVE = tr.perspective(100, win.aspect_ratio, 1, 10)
VIEW = tr.lookAt(np.array([0,0,10]), np.array([0,0,0]), np.array([0,1,0]))
glUniformMatrix4fv(proj_loc, 1, GL_TRUE, PERSPECTIVE)
glUniformMatrix4fv(view_loc, 1, GL_TRUE, VIEW)
glUniformMatrix4fv(model_loc, 1, GL_TRUE, tr.identity())

# GLOBAL VARIABLES
player = Player(0, -6, blue_car)
enemy = Enemy(0,6, red_car)
squere_list = []
world_mouse_pos = np.zeros(2, dtype=np.float32)
mouse_press = False
factor = 2/win.height

def updateScene(dt):
    player.update_pos(dt, world_mouse_pos)
    enemy.update_ia(dt)
    for shape in squere_list:
        shape.update(dt)
    player.crash(enemy)
    for shape in squere_list:
        player.fast_cube_colision(shape)
        enemy.fast_cube_colision(shape)
        for shape2 in squere_list:
            shape.fast_cube_colision(shape2)

@win.event
def on_draw():
    win.clear()
    glUseProgram(tex_program.shaderProgram)
    tex_program.drawCall(background)
    glUseProgram(program.shaderProgram)
    player.draw()
    enemy.draw()
    for shape in squere_list:
        shape.draw()


@win.event
def on_mouse_press(x, y, button, modifiers):
    global mouse_press, world_mouse_pos
    if button == pyglet.window.mouse.LEFT:
        mouse_press = True
        world_mouse_pos = (np.array([x,y]) * factor - np.ones(2)) * 12
    elif button == pyglet.window.mouse.RIGHT:
        player.dash((np.array([x,y]) * factor - np.ones(2)) * 12)

@win.event
def on_mouse_release(x, y, button, modifiers):
    global mouse_press
    if button == pyglet.window.mouse.LEFT:
        mouse_press = False

@win.event
def on_mouse_motion(x, y, dx, dy):
    global world_mouse_pos
    world_mouse_pos = (np.array([x,y]) * factor - np.ones(2)) * 12

@win.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global world_mouse_pos
    world_mouse_pos = (np.array([x,y]) * factor - np.ones(2)) * 12

@win.event
def on_key_press(symbol, mods):
    if symbol == pyglet.window.key.T:
        player.trow_squere()

@win.event
def on_close():
    blue_car.clear()
    red_car.clear()
    squere.clear()
    background.clear()
    glDeleteProgram(tex_program.shaderProgram)
    glDeleteProgram(program.shaderProgram)

pyglet.clock.schedule_interval(updateScene, 1/60)

pyglet.app.run()