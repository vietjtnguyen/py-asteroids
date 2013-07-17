from collections import namedtuple
import math
import random
import time

import pyglet
from pyglet.gl import *
from pyglet.window import key
from pyglet.window import mouse

window = pyglet.window.Window()

BaseVector2 = namedtuple('BaseVector2', ['x', 'y'])
class Vector2(BaseVector2):
    def __add__(a, b):
        if isinstance(b, Vector2):
            return Vector2(a.x+b.x, a.y+b.y)
        else:
            return Vector2(a.x+b, a.y+b)
    def __sub__(a, b):
        if isinstance(b, Vector2):
            return Vector2(a.x-b.x, a.y-b.y)
        else:
            return Vector2(a.x-b, a.y-b)
    def __mul__(a, b):
        if isinstance(b, Vector2):
            return Vector2(a.x*b.x, a.y*b.y)
        else:
            return Vector2(a.x*b, a.y*b)
    def __div__(a, b):
        if isinstance(b, Vector2):
            return Vector2(a.x/b.x, a.y/b.y)
        else:
            return Vector2(a.x/b, a.y/b)

BaseVector3 = namedtuple('BaseVector3', ['x', 'y', 'z'])
class Vector3(BaseVector3):
    def __add__(a, b):
        if isinstance(b, Vector2):
            return Vector2(a.x+b.x, a.y+b.y, a.z+b.z)
        else:
            return Vector2(a.x+b, a.y+b, a.z+b)
    def __sub__(a, b):
        if isinstance(b, Vector2):
            return Vector2(a.x-b.x, a.y-b.y, a.z-b.z)
        else:
            return Vector2(a.x-b, a.y-b, a.z-b)
    def __mul__(a, b):
        if isinstance(b, Vector2):
            return Vector2(a.x*b.x, a.y*b.y, a.z*b.z)
        else:
            return Vector2(a.x*b, a.y*b, a.z*b)
    def __div__(a, b):
        if isinstance(b, Vector2):
            return Vector2(a.x/b.x, a.y/b.y, a.z/b.z)
        else:
            return Vector2(a.x/b, a.y/b, a.z/b)

def unit_vector(angle):
    return Vector2(math.cos(angle), math.sin(angle))

class App():
    def __init__(self):
        self.last_time = time.time()
        self.dt = 1.0
        self.objects = []
    def update_time(self):
        current_time = time.time()
        self.dt = current_time - self.last_time
        self.last_time = current_time
    def add(self, obj):
        self.objects.append(obj)
    def remove(self, obj):
        self.objects.remove(obj)
    def update_objects(self, keys):
        for obj in self.objects:
            obj.update(self.dt, keys)
    def draw_objects(self):
        for obj in self.objects:
            obj.draw()

class Entity(object):
    def __init__(self, parent, **kwargs):
        self.parent = parent
        self.parent.add(self)
        self.position = Vector2(0.0, 0.0)
        self.angle = 0.0
        for key in kwargs:
            setattr(self, key, kwargs[key])
    def remove(self):
        self.parent.remove(self)
    def update(self):
        pass
    def draw(self):
        pass

class Ship(Entity):
    def __init__(self, parent):
        super(Ship, self).__init__(parent)
        self.position = Vector2(400.0, 300.0)
        self.velocity = Vector2(0.0, 0.0)
    def update(self, dt, keys):
        if keys[key.LEFT]:
            self.angle += 4.0*dt
        if keys[key.RIGHT]:
            self.angle -= 4.0*dt
        if keys[key.UP]:
            self.velocity += unit_vector(self.angle)*100.0*dt
        self.position += self.velocity*dt
        if self.position[0] < 0:
            self.position += Vector2(640, 0)
        if self.position[0] > 640:
            self.position -= Vector2(640, 0)
        if self.position[1] < 0:
            self.position += Vector2(0, 480)
        if self.position[1] > 480:
            self.position -= Vector2(0, 480)
    def draw(self):
        glBegin(GL_LINE_LOOP)
        forward = unit_vector(self.angle)
        back_left = unit_vector(self.angle-math.pi*0.75)
        back_right = unit_vector(self.angle+math.pi*0.75)
        glVertex2f(*(self.position+forward*8))
        glVertex2f(*(self.position+back_left*8))
        glVertex2f(*(self.position+back_right*8))
        glEnd()

class Bullet(Entity):
    def __init__(self, parent, position, velocity):
        super(Bullet, self).__init__(parent)
        self.position = position
        self.velocity = velocity
        self.life = 10.0
    def update(self, dt, keys):
        self.position += self.velocity*dt
        if self.position[0] < 0:
            self.position += Vector2(640, 0)
        if self.position[0] > 640:
            self.position -= Vector2(640, 0)
        if self.position[1] < 0:
            self.position += Vector2(0, 480)
        if self.position[1] > 480:
            self.position -= Vector2(0, 480)
        self.life -= dt
        if self.life <= 0.0:
            self.remove()
        for obj in self.parent.objects:
            if isinstance(obj, Asteroid):
                d = obj.position - self.position
                dist = math.sqrt(d[0]*d[0]+d[1]*d[1])
                if dist < obj.radius:
                    obj.remove()
                    if obj.radius > 10.0:
                        Asteroid(self.parent, obj.position, Vector2(random.uniform(-100, 100), random.uniform(-100, 100)), 8, obj.radius - 10.0)
                        Asteroid(self.parent, obj.position, Vector2(random.uniform(-100, 100), random.uniform(-100, 100)), 8, obj.radius - 10.0)
                    self.remove()
                    break
    def draw(self):
        glBegin(GL_LINES)
        glVertex2f(*(self.position))
        glVertex2f(*(self.position-self.velocity*0.03))
        glEnd()

class Asteroid(Entity):
    def __init__(self, parent, position, velocity, sides, radius):
        super(Asteroid, self).__init__(parent)
        self.position = position
        self.velocity = velocity
        self.angular_velocity = random.uniform(-0.5, 0.5)
        self.sides = sides
        self.radius = radius
        self._generate_points()
    def _generate_points(self):
        angle_step = 2.0*math.pi/float(self.sides)
        self.spokes = []
        self.points = []
        for side in range(0, self.sides):
            angle = side*angle_step
            radius = random.uniform(self.radius*0.8, self.radius*1.2)
            self.spokes.append((angle, radius))
    def update(self, dt, keys):
        self.position += self.velocity*dt
        if self.position[0] < -self.radius:
            self.position += Vector2(800+2*self.radius, 0)
        if self.position[0] > 800+self.radius:
            self.position -= Vector2(800+2*self.radius, 0)
        if self.position[1] < -self.radius:
            self.position += Vector2(0, 600+2*self.radius)
        if self.position[1] > 600+self.radius:
            self.position -= Vector2(0, 600+2*self.radius)
        self.angle += self.angular_velocity*dt
    def draw(self):
        glBegin(GL_LINE_LOOP)
        for angle, radius in self.spokes:
            point = unit_vector(angle+self.angle)*radius
            glVertex2f(*(self.position+point))
        glEnd()

app = App()
ship = Ship(app)
for i in range(0, 10):
    Asteroid(app, Vector2(random.uniform(0, 800), random.uniform(0, 600)), Vector2(random.uniform(-100, 100), random.uniform(-100, 100)), 8, 30.0)

@window.event
def on_key_press(symbol, modifiers):
    global app
    if symbol == key.SPACE:
        Bullet(app, ship.position, ship.velocity + unit_vector(ship.angle)*400.0)

@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        pass

keys = key.KeyStateHandler()
window.push_handlers(keys)

@window.event
def on_draw():
    global app
    window.clear()
    app.update_time()
    app.update_objects(keys)
    app.draw_objects()

pyglet.app.run()

