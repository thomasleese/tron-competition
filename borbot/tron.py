import math
import pygame
import pygame.gfxdraw

import log

def wrap_angle(angle):
    while angle < 0:
        angle += 360
    
    while angle > 270:
        angle -= 360
    
    return angle

def next_pos(pos, angle, increment = 1):
    angle = wrap_angle(angle)
    
    if angle == 0:
        pos[1] -= increment
    elif angle == 90:
        pos[0] += increment
    elif angle == 180:
        pos[1] += increment
    elif angle == 270:
        pos[0] -= increment
    
    return pos

class DebugDraw(object):
    def __init__(self):
        self.lines = []
    
    def add_danger(self, colour, position, angle, value):
        colour = ( colour[0], colour[1], colour[2], 50 )
        start_pos = list(position)
        end_pos = next_pos(list(position), angle, value)
        
        self.lines.append(( start_pos[0], start_pos[1], end_pos[0], end_pos[1], colour ))
    
    def draw(self, surface):
        for line in self.lines:
            pygame.gfxdraw.line(surface, *line)
        
    def clear(self):
        self.lines = []

class Bike(object):
    def __init__(self, arena, name, pos):
        self.arena = arena
        self.name = name
        self.pos = pos
        self.last_pos = pos
        self.colour = ( 0, 0, 0 )
        self.dead = False
        self.debug = DebugDraw()
    
    def log(self, *msg):
        log.blue("Arena", *msg)
    
    @property
    def angle(self):
        if self.last_pos[1] == self.pos[1]:
            return 90 if self.last_pos[0] < self.pos[0] else 270
        else:
            return 0 if self.last_pos[1] > self.pos[1] else 180
    
    @property
    def velocity(self):
        x = self.pos[0] - self.last_pos[0]
        y = self.last_pos[1] - self.pos[1]
        return ( x, y )
    
    @property
    def speed(self):
        vel = self.velocity
        return int(math.sqrt(vel[0] * vel[0] + vel[1] * vel[1]))
    
    def next_pos(self, pos, angle, increment = 1):
        return next_pos(pos, self.angle + angle, increment)
    
    def calc_danger(self, angle, pos = None):
        if pos == None:
            pos = self.pos
        
        value = self.arena.calc_danger(pos, self.angle + angle)
        colour = ( self.colour[0] * 1.2, self.colour[1] * 1.2, self.colour[2] * 1.2, 50 )
        self.debug.add_danger(colour, pos, self.angle + angle, value)
        return value
    
    def detect_trap(self, angle):
        danger_ahead = self.calc_danger(angle, self.pos)
        for i in range(danger_ahead - self.speed, self.speed, -max(1, self.speed)):
            next_pos = self.next_pos(list(self.pos), angle, i)
            d = self.calc_danger(angle + 90, next_pos) + self.calc_danger(angle - 90, next_pos)
            if d >= self.speed * 3:
                return False
        return True

class Arena(object):
    def __init__(self):
        self.resize(100, 100)
    
    def log(self, *msg):
        log.purple("Arena", *msg)
    
    def resize(self, w, h):
        self.log("resize (", w, "x", h, ")")
        self.width = w
        self.height = h
        self.reset()
    
    def reset(self):
        self.log("reset")
        self.bikes = []
        self.grid = [ [ None for y in range(self.height) ] for x in range(self.width) ]
    
    def get_point(self, pos):
        # wall
        if pos[0] < 0 or pos[1] < 0 or pos[0] >= self.width or pos[1] >= self.height:
            return True

        # trails
        return self.grid[pos[0]][pos[1]]
    
    def calc_danger(self, start_pos, angle):
        dist = 0
        
        pos = list(start_pos)
        while not self.get_point(pos):
            dist += 1
            pos = next_pos(pos, angle)
        
        return dist
    
    def find_bike(self, name):
        for bike in self.bikes:
            if bike.name == name:
                return bike
        
        return None
    
    def find_or_create_bike(self, name, pos):
        bike = self.find_bike(name)
        if bike:
            return bike
        
        bike = Bike(self, name, pos)
        self.bikes.append(bike)
        return bike
    
    def update_bike(self, name, pos, colour):
        bike = self.find_or_create_bike(name, pos)
        bike.last_pos = bike.pos
        bike.pos = pos
        bike.colour = colour
        
        pos = list(bike.last_pos)
        while pos != list(bike.pos):
            try:
                self.grid[pos[0]][pos[1]] = bike
            except IndexError:
                break
            
            pos = next_pos(pos, bike.angle)
    
    def kill_bike(self, name):
        bike = self.find_bike(name)
        if bike:
            bike.dead = True
            
            for x in range(self.width):
                for y in range(self.height):
                    if self.grid[x][y] == bike:
                        self.grid[x][y] = None
    
    def remove_bike(self, name):
        self.kill_bike(name)
        
        bike = self.find_bike(name)
        if bike:
            self.bikes.remove(bike)
