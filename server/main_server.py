import os, sys
sys.path.insert(1, '/home/andika/Documents/learn/python/tictactoe/server')

from server.main_server_controller import MainServerController
import Pyro4


def get_global_server(name = "globalserver"):
    try:
        uri = "PYRONAME:{}@localhost:1337".format(name)
        gserver = Pyro4.Proxy(uri)
        return gserver
    except:
        sys.exit(0)


def start_with_ns():
    __host = "localhost"
    __port = 1337
    with Pyro4.Daemon(host = __host) as daemon:
        main_server = MainServerController()
        ns = Pyro4.locateNS(__host, __port)
        uri_server = daemon.register(main_server)
        print("URI main  server : ", uri_server)
        ns.register("main_server", uri_server)
        daemon.requestLoop()
    print('\nexited..')


if __name__ == '__main__':
    start_with_ns()