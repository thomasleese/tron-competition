import pygame
import random
from pygame.locals import *

class Boring:
    def process(self, arena, bike, go):
        north = bike.calc_danger(0)
        east = bike.calc_danger(90)
        west = bike.calc_danger(-90)
        gap = bike.speed * 1.5

        if north <= gap:
            if east > gap and west > gap:
                return "R" if east > west else "L", None
            elif east <= gap and west <= gap:
                if north <= gap * 0.5: # really really close to an edge
                    return "R" if east > west else "L", None
            elif east <= gap:
                return "L", None
            elif west <= gap:
                return "R", None

        return "N", None

class BlockOff:
    def __init__(self):
        self.next_move = None

    def process(self, arena, bike, go):
        north = bike.calc_danger(0)
        east = bike.calc_danger(90)
        west = bike.calc_danger(-90)
        gap = bike.speed * 1.5

        if self.next_move:
            move = self.next_move
            self.next_move = None
            return move, None

        if north <= gap:
            move = "R" if east > west else "L"
            self.next_move = move
            return move, None

        return "N", None

class AlwaysTurn:
    def process(self, arena, bike, go):
        east = bike.calc_danger(90)
        west = bike.calc_danger(-90)
        gap = bike.speed * 5

        if east >= gap or west >= gap:
            return "R" if east > west else "L", None
        else:
            return "N", None

class Snail:
    def process(self, arena, bike, go):
        north = bike.calc_danger(0)
        east = bike.calc_danger(90)
        gap = bike.speed * 2

        if north > gap and east <= gap:
            return "N", None
        elif north > gap and east > gap:
            return "R", None
        elif north <= gap and east > gap:
            return "R", None
        elif north <= gap and east <= gap:
            return "L", Boring()
        else:
            return "N", Boring()

class Random:
    def __init__(self):
        self.modes = [
            Snail(),
            Boring(),
            BlockOff(),
            AlwaysTurn(),
        ]
        self.mode = self.modes[0]

    def process(self, arena, bike, go):
        if random.randint(0, 100) == 0:
            self.mode = random.choice(self.modes)

        go, new_mode = self.mode.process(arena, bike, go)
        if new_mode:
            self.mode = new_mode

        return go, None

class TrapPrevention:
    def process(self, arena, bike, go):
        new_angle = 0
        if go == "L":
            new_angle -= 90
        elif go == "R":
            new_angle += 90

        if bike.detect_trap(new_angle):
            north = bike.calc_danger(new_angle)
            east = bike.calc_danger(new_angle + 90)
            west = bike.calc_danger(new_angle - 90)
            
            if go == "R":
                return "N" if north > west else "L", None
            elif go == "L":
                return "N" if north > east else "R", None
            elif go == "N":
                return "R" if east > west else "L", None

        return go, None

class SlowDown:
    def process(self, arena, bike, go):
        if go == "N" and random.randint(0, 3) == 0:
            return "D", None

        return go, None

class Input:
    def process(self, arena, bike, go):
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            return "L", None
        elif keys[K_RIGHT]:
            return "R", None
        else:
            return "N", None
