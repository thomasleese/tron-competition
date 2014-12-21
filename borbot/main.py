#!/usr/bin/env python3
import pygame
import pygame.gfxdraw
import socket
import sys
import time

pygame.init()

import log
import tron

def linesplit(socket):
    # untested
    buffer = socket.recv(4096)
    done = False
    while not done:
        if "\n" in buffer:
            (line, buffer) = buffer.split("\n", 1)
            yield line.strip()
        else:
            more = socket.recv(4096)
            if not more:
                done = True
            else:
                buffer = buffer+more
    if buffer:
        yield buffer

class TronSocket:
    def __init__(self, fd):
        self.fd = fd

    def __del__(self):
        self.fd.close()
    
    def log(self, *msg):
        log.green("TronSocket", *msg)

    def mainloop(self, callback):
        for line in linesplit(self.fd):
            self.read_message(line.split(" "), callback)

    def read_message(self, msg, callback):
        callback(msg)

    def write_message(self, *args):
        msg = ""
        for arg in args:
            msg += str(arg) + " "
            
        self.fd.send(msg + "\n")

class Window(object):
    def __init__(self, w = 100, h = 100):
        self.resize(w, h)
        self.font = pygame.font.SysFont("Source Code Pro", 12, True)
        self.chat_msg = "Let's get going!"
    
    def log(self, *msg):
        log.yellow("Window", *msg)
        
    def resize(self, w, h):
        self.log("resize (", w, "x", h, ")")
        self.window = pygame.display.set_mode(( w, h ))
        pygame.display.set_caption("TRON Bot")
        self.arena_surface = pygame.Surface(( w, h ))
        self.reset()
        
    def reset(self):
        self.log("reset")
        self.arena_surface.fill(( 10, 10, 10 ))

        w = self.window.get_width()
        h = self.window.get_height()
        c = ( 50, 50, 50 )
        for x in range(50, w, 50):
            pygame.gfxdraw.line(self.arena_surface, x, 0, x, h, c)
        for y in range(50, h, 50):
            pygame.gfxdraw.line(self.arena_surface, 0, y, w, y, c)
        
    def update_bike(self, bike):
        pygame.draw.line(self.arena_surface, bike.colour, bike.last_pos, bike.pos)
        
    def draw(self, arena):
        self.window.blit(self.arena_surface, ( 0, 0 ))

        for bike in arena.bikes:
            pygame.draw.rect(self.window, bike.colour, ( bike.pos[0] - 1, bike.pos[1] - 1, 3, 3 ))
            self.window.blit(self.font.render(bike.name, 1, bike.colour), ( bike.pos[0] + 3, bike.pos[1] + 3 ))
            bike.debug.draw(self.window)

        self.window.blit(self.font.render(self.chat_msg, 1, ( 255, 255, 255 )), ( 10, 8 ))

        pygame.display.flip()

class Bot(object):
    def __init__(self, fd, name):
        self.socket = TronSocket(fd)
        self.name = name
        self.arena = tron.Arena()
        self.window = Window()
        self.mode = None
    
        self.send_initial_details(name, ( 0, 128, 200 ))
        self.socket.mainloop(self.handle_message)
    
    def log(self, *msg):
        log.red("Bot", *msg)
    
    def send_initial_details(self, name, colour):
        self.log("sending initial details")
        self.socket.write_message("COLOUR", colour[0], colour[1], colour[2])
        self.socket.write_message("NAME", name)

    def handle_message(self, msg):
        if msg[0] == "ARENA":
            w = int(float(msg[1]) / 100 + 0.5)
            h = int(float(msg[2]) / 100 + 0.5)
            self.on_arena(w, h)
        elif msg[0] == "RESET":
            self.window.chat_msg = "Server: New game!"
            self.on_reset()
        elif msg[0] == "BIKE":
            name = msg[1]
            x = int(float(msg[2]) / 100 + 0.5)
            y = int(float(msg[3]) / 100 + 0.5)
            r = int(msg[4])
            g = int(msg[5])
            b = int(msg[6])
            self.on_bike(name, ( x, y ), ( r, g, b ))
        elif msg[0] == "DEAD":
            name = msg[1]
            self.on_dead(name)
        elif msg[0] == "DISCO" and len(msg) >= 2:
            name = msg[1]
            self.on_disco(name)
        elif msg[0] == "G":
            self.on_go()
        elif msg[0] == "CHAT":
            self.window.chat_msg = msg[1] + ": " + " ".join(msg[2:])
        else:
            self.log(msg)

    def on_arena(self, w, h):
        self.arena.resize(w, h)
        self.window.resize(w, h)
    
    def on_reset(self):
        self.mode = None
        self.arena.reset()
        self.window.reset()
    
    def on_bike(self, name, pos, colour):
        self.arena.update_bike(name, pos, colour)
        self.window.update_bike(self.arena.find_bike(name))
    
    def on_dead(self, name):
        self.arena.kill_bike(name)
    
    def on_disco(self, name):
        self.arena.remove_bike(name)
    
    def change_mode(self, new_mode):
        self.mode = new_mode
        self.log("new mode", new_mode.__class__.__name__)
    
    def on_go(self):
        self.window.draw(self.arena)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

if __name__ == "__main__":
    if len(sys.argv) == 3:
        fd = open(sys.argv[1])
        Bot(fd, sys.argv[2])
    else:
        fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fd.connect(( sys.argv[1], int(sys.argv[2]) ))
        Bot(fd, sys.argv[3])
