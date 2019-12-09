import os, sys
sys.path.insert(1, '/home/andika/Documents/learn/python/tictactoe/game')

import Pyro4
from Pyro4.errors import CommunicationError
import logging
import threading
import time

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
            self.main_server_connection._pyroTimeout = interval
            tpa = self.job_ping_server_ping_ack()
            self.replication_server = self.__connect_server("replication_server")
            print(self.replication_server.ping())
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
        try:
            response = self.main_server_connection.create_room_func()
        except Exception as e:
            self.reconnect_main_server()
            response = self.main_server_connection.create_room_func()

        available_rooms = self.available_rooms_command()
        to_remove = []
        for idx, connections in enumerate(self.registered_client_connections):
            # print(connections['identifier'])
            if connections['identifier'] == identifier:
                continue
            try:
                connections['connection'].update_list_of_game_rooms(available_rooms)
            except CommunicationError as e: 
                logging.error('failed to connect to client {}: {}'.format(connections['identifier'], e))
                self.registered_client.remove(connections['identifier'])
                try:
                    self.main_server_connection.unregister_func(connections['identifier'])
                except Exception as e:
                    self.reconnect_main_server()
                    self.main_server_connection.unregister_func(connections['identifier'])
                to_remove.append(connections)

        for conn in to_remove:
            self.registered_client_connections.remove(conn)

        print(self.replication_server.new_room(response['data']))

        return response

    @Pyro4.expose
    def available_rooms_command(self):
        try:
            return self.main_server_connection.available_rooms_func()
        except Exception as e:
            self.reconnect_main_server()
            return self.main_server_connection.available_rooms_func()

    @Pyro4.expose
    def delete_room_command(self, identifier):
        try:
            return self.main_server_connection.delete_room_func(identifier)
        except Exception as e:
            self.reconnect_main_server()
            return self.main_server_connection.delete_room_func(identifier)

    @Pyro4.expose
    def register_command(self, identifier):
        if identifier in self.registered_client:
            return None
        self.registered_client_connections.append({'identifier' : identifier, 'connection' : self.__connect_server('gui_server_{}'.format(identifier))})
        self.registered_client.add(identifier)
        try:
            return self.main_server_connection.register_func(identifier)
        except Exception as e:
            self.reconnect_main_server()
            return self.main_server_connection.register_func(identifier)

    @Pyro4.expose
    def game_ended(self, identifier):
        try:
            return self.main_server_connection.delete_room_func(identifier)
        except Exception as e:
            self.reconnect_main_server()
            return self.main_server_connection.delete_room_func(identifier)

    @Pyro4.expose
    def push_to_replication_server(self, identity, pyro_obj):
        try:
            print('di dalem siniii123')
            main_server_state = self.main_server_connection.get_important_props()
            print('sdhjfgjsdfggj', main_server_state)
            game_state = self.main_server_connection.get_game_room_obj(identity)
            response = self.replication_server.update_state(identity, game_state, pyro_obj)
            self.replication_server.update_main_server_state(main_server_state)

            print('in here ok', response)
        except Exception as e:
            print('exksepsi ', e)
            # pass
            self.reconnect_main_server()
            main_server_state = self.main_server_connection.get_important_props()
            game_state = self.main_server_connection.get_game_room_obj(identity)
            response = self.replication_server.update_state(identity, game_state, pyro_obj)
            self.replication_server.update_main_server_state(main_server_state)
            print('in here ok--2', response)

    def __connect_server(self, name):
        try:
            uri = "PYRONAME:{}@localhost:1337".format(name)
            return Pyro4.Proxy(uri)
        except CommunicationError as e:
            logging.error('failed to get {}: {}'.format(name, e))
            return None

    def gracefully_exits(self):
        print("disconnecting..")
        time.sleep(0.5)
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

    def communicate(self) -> bool:
        try:
            res = self.main_server_connection.check_connection()
            if res == 'ok':
                pass
        except:
            self.reconnect_main_server()
            return False
        return True

    def job_ping_server_ping_ack(self) -> threading.Thread:
        t = threading.Thread(target=self.ping_server)
        t.start()
        return t

    def reconnect_main_server(self):
        self.main_server_connection = self.__connect_server('main_server')

    def ping_server(self):
        while True:
            alive = self.communicate()
            if not alive:
                alive = self.communicate()
                if not alive:
                    print("\nmain server is down [DETECT BY ping ack]\n")
                    print(self.replication_server.create_rooms())
                    break
            time.sleep(self.ping_interval())
        # self.gracefully_exits()