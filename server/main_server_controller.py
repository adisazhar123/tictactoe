import os, sys
sys.path.insert(1, '/home/andika/Documents/learn/python/tictactoe/game')

import Pyro4
import Pyro4.errors
import shortuuid
import time
from game.game_room_controller import GameRoomController
from threading import Lock
import threading


class MainServerController(object):
    def __init__(self):
        self.config = {'host': 'localhost', 'port': 1337}
        self.available_rooms = []
        self.lock = Lock()

    @Pyro4.expose
    def create_room_func(self) -> dict:
        self.lock.acquire()
        identity = shortuuid.random(length=4)
        t = threading.Thread(target=self.__create_room, args=(identity,))
        t.daemon = True
        t.start()
        self.lock.release()
        self.available_rooms.append({
            'id': identity,
            'created_at': time.time()
        })
        print('room created')
        return {
            'status': 'ok',
            'message': 'game room succesfully created',
            'data': identity
        }

    @Pyro4.expose
    def available_rooms_func(self) -> dict:
        print('list of available rooms')
        return {
            'status': 'ok',
            'message': 'list of game rooms',
            'data': self.available_rooms
        }

    def __create_room(self, identity):
        game_room = GameRoomController(identity)
        daemon = Pyro4.Daemon(host = self.config['host'])
        ns = Pyro4.locateNS(self.config['host'], self.config['port'])
        uri = daemon.register(game_room)
        ns.register("game_room_server_{}".format(identity), uri)
        daemon.requestLoop()