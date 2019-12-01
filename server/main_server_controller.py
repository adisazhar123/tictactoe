import os, sys
sys.path.insert(1, '/home/andika/Documents/learn/python/tictactoe/game')

import Pyro4
import Pyro4.errors
import shortuuid
import time
from game_room_controller import GameRoomController
from threading import Lock
import threading
import logging

logging.basicConfig(filename='MainServerController.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


class MainServerController(object):
    def __init__(self):
        self.config = {'host': 'localhost', 'port': 1337}
        self.available_rooms = []
        self.lock = Lock()
        self.threads = []

    @Pyro4.expose
    def check_connection(self) -> str:
        return 'ok'

    @Pyro4.expose
    def ping_interval(self) -> int:
        return 3

    @Pyro4.expose
    def create_room_func(self) -> dict:
        try:
            self.lock.acquire()
            identity = shortuuid.random(length=4)
            logging.info('creating thread for room {}'.format(identity))
            t = threading.Thread(target=self.__create_room, args=(identity,))
            t.daemon = True
            t.start()
            logging.info('successfully create thread for room {}'.format(identity))
            # todo: feature to autoremove rooms if status not used
            timestamp = time.time()
            self.available_rooms.append({
                'id': identity,
                'status': 'active',
                'last_used': timestamp,
                'created_at': timestamp,
            })
            self.threads.append({
                'id': identity,
                'thread': t
            })
            self.lock.release()
        except Exception as e:
            return {
                'status': 'error',
                'message': e,
                'data': None
            }

        return {
            'status': 'ok',
            'message': 'game room succesfully created',
            'data': identity
        }

    @Pyro4.expose
    def available_rooms_func(self) -> dict:
        logging.info('available_rooms_func')
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