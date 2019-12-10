import os, sys
sys.path.insert(1, '/home/bani/Documents/tictactoe')

import time
import sys
import Pyro4
import threading
sys.path.insert(1, '/home/adisazhar/projects/python/tictactoe')

from Pyro4.errors import ConnectionClosedError, CommunicationError

from game.game_room_controller import GameRoomController
from server.main_server_controller import MainServerController
from server.communication_server_controller import CommunicationServerController

@Pyro4.expose
class ReplicationController:
    def __init__(self):
        self.config = {'host': 'localhost', 'port': 1337}
        self.main_server_state = None
        self.communication_server_state = None

        self.rooms = {}
        print('replication controller init')
        self.communication_server_connection = None
        self.main_server_connection = None

        self.main_server_being_restarted = 0

        threading.Thread(target=self.ping_game_controllers, daemon=True).start()
        threading.Thread(target=self.ping_communication_controllers, daemon=True).start()
        threading.Thread(target=self.ping_main_server, daemon=True).start()

    def new_room(self, identity):
        self.rooms[identity] = 'empty'
        return "function new_room from replication_controller room: {} added".format(identity)

    def create_rooms(self):
        # for room_id in self.rooms:
        #     print(room_id, '->', self.rooms[room_id])
        return self.rooms

    def update_state(self, identity, state, pyro_obj):
        self.rooms[identity] = {'state': state, 'pyro_connection': pyro_obj}
        print(state)
        return self.rooms[identity]

    def ping(self):
        return "function ping from replication_controller"

    def restart_game_server(self, room_id):
        print('room id', room_id)
        try:
            game_controller_obj = GameRoomController(room_id)
            if 'state' in self.rooms[room_id]:
                game_controller_obj.set_important_props(self.rooms[room_id]['state'])
            daemon = Pyro4.Daemon(host = self.config['host'])
            ns = Pyro4.locateNS(self.config['host'], self.config['port'])
            uri = daemon.register(game_controller_obj)
            ns.register("game_room_server_{}".format(room_id), uri)
            print("{} room created".format(room_id))
            print('check ', game_controller_obj.return_self())
            if 'pyro_connection' in self.rooms[room_id]:
                self.rooms[room_id]['pyro_connection'] = self.connect_to_server("game_room_server_{}".format(room_id))
            else:
                self.rooms[room_id] = {'state': {}, 'pyro_connection': self.connect_to_server("game_room_server_{}".format(room_id))}

            daemon.requestLoop()
        except Exception as e:
            print('error creating game server {} {}'.format(room_id, e))

    def restart_main_server(self):
        main_controller_obj = MainServerController()
        main_controller_obj.set_important_props(self.main_server_state)
        daemon = Pyro4.Daemon(host=self.config['host'])
        ns = Pyro4.locateNS(self.config['host'], self.config['port'])
        uri = daemon.register(main_controller_obj)
        ns.register("main_server", uri)

        print('main server created')

        daemon.requestLoop()

    def restart_connection_server(self):
        connection_controller_obj = CommunicationServerController()
        connection_controller_obj.set_important_props(self.communication_server_state)
        daemon = Pyro4.Daemon(host=self.config['host'])
        ns = Pyro4.locateNS(self.config['host'], self.config['port'])
        uri = daemon.register(connection_controller_obj)
        ns.register("communication_server", uri)

        print('communication server created')

        daemon.requestLoop()

    def connect_to_server(self, name):
        try:
            uri = "PYRONAME:{}@localhost:1337".format(name)
            res = Pyro4.Proxy(uri)
            return res
        except Exception as e:
            return None

    # def ping_main_controller(self):
    #

    def update_main_server_state(self, state):
        self.main_server_state = state

    def update_communication_server_state(self, state):
        self.communication_server_state = state

    def get_communication_connection(self, communication_connection):
        self.communication_server_connection = communication_connection

    def ping_game_controllers(self):
        while True:
            try:
                if self.main_server_connection is not None:
                    self.main_server_state = self.main_server_connection.get_important_props()
                    self.main_server_connection.check_connection()

                for roomId in self.rooms:                    
                    if self.rooms[roomId] is not 'empty':
                        res = self.rooms[roomId]['pyro_connection'].ping()
                        # print('pinging ', self.rooms[roomId]['pyro_connection'].ping())
            except Exception as e:
                threading.Thread(target=self.restart_main_server, daemon=True).start()
                for room_id in self.rooms:
                    threading.Thread(target=self.restart_game_server, args=(room_id,), daemon=True).start()
                break
            time.sleep(3)

    def ping_communication_controllers(self):
        while self.communication_server_connection is None:
            # print('wua', self.communication_server_connection)
            time.sleep(1)

        while True:
            # print('gas')
            try:
                res = self.communication_server_connection.check_connection()
                # print('pinging comm server ', self.communication_server_connection.check_connection())
            except Exception as e:
                threading.Thread(target=self.restart_connection_server, daemon=True).start()
            time.sleep(3)

    def ping_main_server(self):
        while self.main_server_connection is None:
            time.sleep(1)
            self.main_server_connection = self.connect_to_server("main_server")
            print(self.main_server_connection)
