import Pyro4

from replication_controller import ReplicationController


def start_with_ns():
    __host = "localhost"
    __port = 1337
    with Pyro4.Daemon(host = __host) as daemon:
        try:
            replication_server = ReplicationController()
        except ValueError as e:
            print(e)
            return
        ns = Pyro4.locateNS(__host, __port)
        uri_server = daemon.register(replication_server)
        print("URI replication server : ", uri_server)
        ns.register("replication_server", uri_server)
        daemon.requestLoop()
    print('\nexited..')


if __name__ == '__main__':
    start_with_ns()
