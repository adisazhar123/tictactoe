import Pyro4
import shortuuid


@Pyro4.expose
class TestController:
    def __init__(self):
        pass

    def ping(self):
        return 'ok from test'


def start_server(game_room_controller_obj, identity):
    daemon = Pyro4.Daemon(host='10.151.30.140')
    ns = Pyro4.locateNS('10.151.30.140', 1337)
    uri_game_room_controller = daemon.register(game_room_controller_obj)
    uri_name = 'test_server'
    print(uri_name)
    ns.register(uri_name, uri_game_room_controller)
    daemon.requestLoop()


if __name__ == "__main__":
    identity = shortuuid.random(length=4)
    game_room_controller = TestController()
    start_server(game_room_controller, identity)
