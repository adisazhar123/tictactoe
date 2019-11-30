import Pyro4
import shortuuid
from game.game_room_controller import GameRoomController


def start_server(game_room_controller_obj, identity):
    daemon = Pyro4.Daemon(host='localhost')
    ns = Pyro4.locateNS('localhost', 1337)
    uri_game_room_controller = daemon.register(game_room_controller_obj)
    print('URI game room controller server: ', uri_game_room_controller)
    uri_name = 'game_room_server_{}'.format(identity)
    print(uri_name)
    ns.register(uri_name, uri_game_room_controller)
    daemon.requestLoop()


if __name__ == "__main__":
    identity = shortuuid.random(length=4)
    game_room_controller = GameRoomController(identity)
    start_server(game_room_controller, identity)
