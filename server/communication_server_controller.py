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
        self.main_server_connection = self.__connect_server('main_server')
        self.registered_client = set()
        self.registered_client_connections = []
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
    def create_room_command(self, identifier):
        response = self.main_server_connection.create_room_func()
        available_rooms = self.available_rooms_command()
        for connections in self.registered_client_connections:
            # print(connections['identifier'])
            if connections['identifier'] == identifier:
                continue
            connections['connection'].update_list_of_game_rooms(available_rooms)
        return response

    @Pyro4.expose
    def available_rooms_command(self):
        return self.main_server_connection.available_rooms_func()

    @Pyro4.expose
    def register_command(self, identifier):
        if identifier in self.registered_client:
            return None
        self.registered_client_connections.append({'identifier' : identifier, 'connection' : self.__connect_server('gui_server_{}'.format(identifier))})
        self.registered_client.add(identifier)
        return self.main_server_connection.register_func(identifier)

    def __connect_server(self, name):
        try:
            uri = "PYRONAME:{}@localhost:1337".format(name)
            return Pyro4.Proxy(uri)
        except CommunicationError as e:
            logging.error('failed to get {}: {}'.format(name, e))
            return None