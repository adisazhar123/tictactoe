import os, sys
sys.path.insert(1, '/home/adisazhar/projects/python/tictactoe')

from server.communication_server_controller import CommunicationServerController
import Pyro4

def start_with_ns():
    __host = "localhost"
    __port = 1337
    with Pyro4.Daemon(host = __host) as daemon:
        try:
            communication_server = CommunicationServerController()
        except ValueError as e:
            print(e)
            return
        ns = Pyro4.locateNS(__host, __port)
        uri_server = daemon.register(communication_server)
        print("URI communication server : ", uri_server)
        ns.register("communication_server", uri_server)
        daemon.requestLoop()
    print('\nexited..')


if __name__ == '__main__':
    start_with_ns()