import time

import Pyro4
import threading

from Pyro4.errors import ConnectionClosedError, CommunicationError

from game.game_room_controller import GameRoomController
from server.main_server_controller import MainServerController


@Pyro4.expose
class ReplicationController:
    def __init__(self):
        self.config = {'host': 'localhost', 'port': 1337}
        self.main_server_state = None

        self.rooms = {}
        print('replication controller init')
        threading.Thread(target=self.ping_game_controllers, daemon=True).start()

    def new_room(self, identity):
        self.rooms[identity] = None
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
        game_controller_obj = GameRoomController(room_id)
        game_controller_obj.set_important_props(self.rooms[room_id]['state'])
        daemon = Pyro4.Daemon(host = self.config['host'])
        ns = Pyro4.locateNS(self.config['host'], self.config['port'])
        uri = daemon.register(game_controller_obj)
        ns.register("game_room_server_{}".format(room_id), uri)
        print("{} room created".format(room_id))
        print('check ', game_controller_obj.return_self())

        self.rooms[room_id]['pyro_connection'] = self.connect_to_server("game_room_server_{}".format(room_id))

        daemon.requestLoop()

    def restart_main_server(self):
        main_controller_obj = MainServerController()
        main_controller_obj.set_important_props(self.main_server_state)
        daemon = Pyro4.Daemon(host=self.config['host'])
        ns = Pyro4.locateNS(self.config['host'], self.config['port'])
        uri = daemon.register(main_controller_obj)
        ns.register("main_server", uri)

        print('main server created')

        daemon.requestLoop()

    def connect_to_server(self, name):
        try:
            uri = "PYRONAME:{}@localhost:1337".format(name)
            return Pyro4.Proxy(uri)
        except CommunicationError as e:
            print(e)

    # def ping_main_controller(self):
    #

    def update_main_server_state(self, state):
        self.main_server_state = state

    def ping_game_controllers(self):
        while True:
            for roomId in self.rooms:
                print(self.rooms[roomId])
                if self.rooms[roomId] is not None:
                    try:
                        print('pinging ', self.rooms[roomId]['pyro_connection'].ping())
                    except Exception as e:
                        threading.Thread(target=self.restart_main_server, daemon=True).start()
                        threading.Thread(target=self.restart_game_server, args=(roomId,), daemon=True).start()
            time.sleep(3)
