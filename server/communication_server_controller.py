import os, sys
sys.path.insert(1, '/home/andika/Documents/learn/python/tictactoe/game')

import Pyro4
from Pyro4.errors import CommunicationError
import logging

logging.basicConfig(filename='CommunicationServerController.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


class CommunicationServerController(object):
    def __init__(self):
        self.main_server_connection = self.__connect_main_server()
        try:
            interval = self.main_server_connection.ping_interval()
        except:
            raise ValueError('could not initiate CommunicationServerController')

    @Pyro4.expose
    def check_connection(self) -> str:
        return 'ok'

    @Pyro4.expose
    def ping_interval(self) -> int:
        return 3

    @Pyro4.expose
    def create_room_command(self):
        return self.main_server_connection.create_room_func()

    @Pyro4.expose
    def available_rooms_command(self):
        return self.main_server_connection.available_rooms_func()

    def __connect_main_server(self):
        try:
            uri = "PYRONAME:main_server@localhost:1337"
            return Pyro4.Proxy(uri)
        except CommunicationError as e:
            logging.error('failed to get main_server: {}'.format(e))
            return None