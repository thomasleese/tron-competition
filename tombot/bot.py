#!/usr/bin/env python3
import socket
import sys
import time

import log
import modes
import tron

class Bot(object):
    def __init__(self, socket, name, initial_mode):
        self.socket = socket
        self.name = name
        self.arena = tron.Arena()
        self.mode = None
        self.initial_mode = initial_mode
        self.on_reset()
    
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
            pass
        else:
            self.log(msg)

    def on_arena(self, w, h):
        self.arena.resize(w, h)

    def on_reset(self):
        self.change_mode(getattr(modes, self.initial_mode)())
        self.arena.reset()
    
    def on_bike(self, name, pos, colour):
        self.arena.update_bike(name, pos, colour)
    
    def on_dead(self, name):
        self.arena.kill_bike(name)
    
    def on_disco(self, name):
        self.arena.remove_bike(name)
    
    def change_mode(self, new_mode):
        self.mode = new_mode
        self.log("new mode", new_mode.__class__.__name__)
    
    def on_go(self):
        bike = self.arena.find_bike(self.name)
        bike.debug.clear()

        go = "N"
        new_mode = None

        if not bike.dead:
            if self.mode:
                # main mode
                go, new_mode = self.mode.process(self.arena, bike, go)
                while new_mode:
                    self.change_mode(new_mode)
                    go, new_mode = self.mode.process(self.arena, bike, go)

            # only worth trap prevention if we're going slowly
            go, _ = modes.TrapPrevention().process(self.arena, bike, go)

            # always better to go slower
            go, _ = modes.SlowDown().process(self.arena, bike, go)

        self.socket.write_message(go)

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(( sys.argv[1], int(sys.argv[2]) ))

    initial_mode = "Snail"
    if len(sys.argv) >= 5:
        initial_mode = sys.argv[4]

    Bot(tron.Socket(socket=sock), sys.argv[3], initial_mode)
