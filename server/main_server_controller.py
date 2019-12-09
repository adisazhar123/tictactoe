import sys

from server import Test

sys.path.insert(1, '/home/andika/Documents/learn/python/tictactoe/game')

import Pyro4
import Pyro4.errors
import shortuuid
import time
from game.game_room_controller import GameRoomController
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
        self.registered_client = set()
        self.lock = Lock()

        self.game_rooms_obj = {}

        self.test = Test.TestController()

        threading.Thread(target=self.check_objects, daemon=True).start()

    def set_important_props(self, props):
        self.available_rooms = props['available_rooms']
        self.game_rooms_obj = props['game_rooms_obj']
        self.registered_client = props['registered_client']

    @Pyro4.expose
    def get_important_props(self):
        return {
            'available_rooms': self.available_rooms,
            'game_rooms_obj': self.game_rooms_obj,
            'registered_client': self.registered_client,
        }

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

    @Pyro4.expose
    def delete_room_func(self, identifier):
        self.lock.acquire()
        _room = None
        for room in self.available_rooms:
            if room['id'] == identifier:
                _room = room
                break
        self.available_rooms.remove(_room)
        self.lock.release()
        logging.info('delete room {}'.format(identifier))
        return {
            'status': 'ok',
            'message': 'delete room',
            'data': self.available_rooms_func()['data']
        }

    @Pyro4.expose
    def register_func(self, identifier):
        self.registered_client.add(identifier)
        logging.info('added client {}'.format(identifier))
        return {
            'status': 'ok',
            'message': 'register client',
            'data': self.registered_client
        }

    @Pyro4.expose
    def unregister_func(self, identifier):
        self.registered_client.remove(identifier)
        logging.info('removed client {}'.format(identifier))
        return {
            'status': 'ok',
            'message': 'unregister client',
            'data': self.registered_client
        }

    # def game_ended(self, identifier):
    #     found = 0
    #     for room in self.available_rooms:
    #         if room.id == identifier:
    #             self.available_rooms

    def __create_room(self, identity):
        game_room = GameRoomController(identity)
        self.game_rooms_obj[identity] = game_room

        daemon = Pyro4.Daemon(host = self.config['host'])
        ns = Pyro4.locateNS(self.config['host'], self.config['port'])
        uri = daemon.register(game_room)
        ns.register("game_room_server_{}".format(identity), uri)
        daemon.requestLoop()

    @Pyro4.expose
    def get_game_room_obj(self, id):
        props = self.game_rooms_obj[id].get_important_props()
        print('game room obj is: ', props)
        return props

    def check_objects(self):
        while True:
            for id in self.game_rooms_obj:
                print(self.game_rooms_obj[id].players)
            time.sleep(3)
