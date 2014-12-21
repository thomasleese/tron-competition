#!/usr/bin/python3
import asyncore
import random
import socket
import time
import threading

class Client(asyncore.dispatcher_with_send):
    def __init__(self, server, socket):
        super().__init__(socket)
        self.server = server
        self.buffer = b""
        self.connected = True

    def handle_read(self):
        data = self.recv(4196)
        if data:
            self.buffer += data

    def handle_close(self):
        try:
            self.server.clients.remove(self)
            self.buffer += b"DISCO\n" # just in case
            print("Closed connection.")
            self.connected = False
            self.close()
        except ValueError:
            pass # already handled

    def close(self):
        self.connected = False
        super().close()

    def send_message(self, *args):
        try:
            msg = " ".join(map(str, args)) + "\n"
            self.send(msg.encode("utf-8"))
        except OSError:
            pass # clearly disconnected

    def read_message(self):
        while b"\n" in self.buffer:
            line, self.buffer = self.buffer.split(b"\n", 1)
            msg = line.strip().decode("utf-8").split(" ")
            if msg:
                yield msg

class Server(asyncore.dispatcher):
    def __init__(self, port):
        super().__init__()

        self.clients = [ ]
        self._new_clients = [ ]

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(( "", port ))
        self.listen(16) # 16 clients?
        print("Server started on {0}.".format(port))

    def handle_accepted(self, sock, addr):
        client = Client(self, sock)
        print("Incoming connection from {0}.".format(addr))
        self.clients.append(client)
        self._new_clients.append(client)

    def new_clients(self):
        for c in self._new_clients:
            self._new_clients.remove(c)
            yield c

    def send_message(self, *args):
        for client in self.clients:
            client.send_message(*args)

class Bike:
    def __init__(self, name, colour):
        self.name = name
        self.colour = colour
        self.reset()

    def __str__(self):
        return "Bike(name='{0}')".format(self.name)

    def reset(self):
        self.trail = [ ]
        self.dead = False
        self.pos = ( random.randint(0, 80000), random.randint(0, 60000) )
        self.direction = 90 * random.randint(0, 3)
        self.speed = 100
        self.target_speed = 500
        self.acceleration_pool = 0
        self.trail.append(( self.pos, self.pos ))

    def turn(self, angle):
        self.direction += angle
        self.trail.append(( self.pos, self.pos ))

        while self.direction >= 360:
            self.direction -= 360
        while self.direction < 0:
            self.direction += 360

        if self.acceleration_pool < 100:
            self.acceleration_pool += 2

        self.update_speeds()

    def accelerate(self):
        if self.acceleration_pool > 0:
            self.speed += 20
            self.acceleration_pool -= 5
        else:
            self.update_speeds()

    def decelerate(self):
        if self.acceleration_pool > 0:
            self.speed -= 20
            self.acceleration_pool -= 5
        else:
            self.update_speeds()

    def nothing(self):
        if self.acceleration_pool < 100:
            self.acceleration_pool += 2

        self.update_speeds()

    def update_speeds(self):
        if self.target_speed > self.speed:
            self.speed += 30
        elif self.target_speed < self.speed:
            self.speed -= 30

        if abs(self.target_speed - self.speed) < 30:
            self.speed = self.target_speed

    def line_intersection(self, p1, p2, p3, p4):
        x1 = p1[0]; y1 = p1[1]
        x2 = p2[0]; y2 = p2[1]
        x3 = p3[0]; y3 = p3[1]
        x4 = p4[0]; y4 = p4[1]

        d = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
        if d == 0:
            return None

        yd = y1 - y3
        xd = x1 - x3
        ua = ((x4 - x3) * yd - (y4 - y3) * xd) / d
        if ua < 0 or ua > 1:
            return None

        ub = ((x2 - x1) * yd - (y2 - y1) * xd) / d
        if ub < 0 or ub > 1:
            return None

        return ( x1 + (x2 - x1) * ua, y1 + (y2 - y1) * ua )

    def check_collision(self, bike):
        if self.pos[0] < 0 or self.pos[0] >= 80000 or self.pos[1] < 0 or self.pos[1] >= 60000:
            return True

        if not bike.dead:
            line_trail1 = self.trail
            line_trail2 = bike.trail
            if self == bike:
                line_trail1 = line_trail1[:-3]
                line_trail2 = line_trail2[-1:]

            for line1 in line_trail1:
                for line2 in line_trail2:
                    intersect = self.line_intersection(line1[0], line1[1], line2[0], line2[1])
                    if intersect:
                        self.pos = intersect
                        bike.pos = intersect
                        print("{0} collided with {1}".format(self, bike))
                        return True

        return False

    def move(self, dx, dy):
        self.pos = ( int(self.pos[0] + dx), int(self.pos[1] + dy) )

    def update(self, other_bikes):
        if not self.dead:
            if self.direction == 0:
                self.move(0, -self.speed)
            elif self.direction == 90:
                self.move(+self.speed, 0)
            elif self.direction == 180:
                self.move(0, +self.speed)
            elif self.direction == 270:
                self.move(-self.speed, 0)

            self.trail[-1] = ( self.trail[-1][0], self.pos )

            for bike in other_bikes:
                if self.check_collision(bike):
                    self.dead = True
                    break

class Game:
    def __init__(self):
        self.game_server = Server(4567)
        self.spectator_server = Server(4568)
        self.spectator_messages = [ ]
        self.bikes = { }
        self.sudden_death = False
        self.sudden_death_timeout = 10000

    def send_message(self, *args):
        self.game_server.send_message(*args)
        self.spectator_server.send_message(*args)

    def reset(self):
        print("Resetting game.")
        for bike in self.bikes.values():
                bike.reset()

        self.send_message("RESET")
        self.spectator_messages = [ ]
        self.sudden_death = False
        self.sudden_death_timeout = 10000

    def handle_new_clients(self):
        should_reset = False
        for client in self.game_server.new_clients():
            name = None
            colour = None

            time.sleep(1) # give them 1 second to have a name and colour set

            for msg in client.read_message():
                if msg[0] == "NAME":
                    name = msg[1]
                elif msg[0] == "COLOUR":
                    colour = tuple(map(int, msg[1:4]))
                else:
                    break # deserves kicking for saying anything else

            self.bikes[client] = Bike(name, colour)
            client.send_message("ARENA", 80000, 60000)
            should_reset = True

        for client in self.spectator_server.new_clients():
            client.send_message("ARENA", 80000, 60000)
            if not should_reset:
                for msg in self.spectator_messages:
                    client.send_message(*msg)

        if should_reset:
            self.reset()

    def handle_disconnection(self):
        clients = list(self.bikes.keys()) # to change dictionary while iterating
        for client in clients:
            if not client.connected:
                bike = self.bikes[client]
                del self.bikes[client]
                self.send_message("DISCO", bike.name)

    def handle_state(self):
        all_dead = True
        for bike in self.bikes.values():
            if not bike.dead:
                all_dead = False

        if all_dead:
            self.reset()

        for bike in self.bikes.values():
            bike.update(self.bikes.values())

            if bike.dead:
                msg = ( "DEAD", bike.name )
            else:
                msg = ( "BIKE", bike.name ) + bike.pos + bike.colour

            self.spectator_messages.append(msg)
            self.send_message(*msg)

        self.send_message("G")

    def handle_go(self):
        for client, bike in self.bikes.items():
            go = None
            for i in range(1000):
                try:
                    go = next(client.read_message())
                    if go:
                        break
                except StopIteration:
                    pass # nothing to read

                time.sleep(0.01)

            if go == [ "R" ]:
                bike.turn(90)
            elif go == [ "L" ]:
                bike.turn(-90)
            elif go == [ "A" ]:
                bike.accelerate()
            elif go == [ "D" ]:
                bike.decelerate()
            elif go == [ "N" ]:
                bike.nothing()
            elif go and go[0] == "CHAT":
                bike.nothing()
                self.send_message("CHAT", bike.name, *go[1:])
            else:
                print("Killing client - said {0}.".format(go))
                bike.dead = True
                client.close()

    def handle_sudden_death(self):
        if self.sudden_death:
            for bike in self.bikes.values():
                bike.target_speed *= 1.01
        else:
            self.sudden_death_timeout -= 1
            if self.sudden_death_timeout < 0:
                self.sudden_death = True
                self.send_message("CHAT", "Server", "SUDDEN DEATH ACTIVATED!")

    def mainloop(self):
        #import yappi
        #yappi.start()

        while True:
            self.handle_disconnection()
            self.handle_new_clients()

            if self.bikes:
                self.handle_state()
                self.handle_go()
                self.handle_sudden_death()
            else:
                # no point wasting CPU cycles
                time.sleep(1)

            #yappi.print_stats()

threading.Thread(target=Game().mainloop, name="Game").start()
threading.Thread(target=asyncore.loop, name="Networking").start()
