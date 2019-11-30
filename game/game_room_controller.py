import Pyro4
from threading import Lock, Thread


@Pyro4.expose
class GameRoomController:
    def __init__(self, identity):
        self.game_room_name = identity
        self.players = []
        self.spectators = []
        # Init tic tac toe positions
        self.game_positions = [''] * 9
        self.max_players = 2

        self.TYPE_SPECTATOR = 'spectator'
        self.TYPE_PLAYER = 'player'

        self.TYPE_PLAYER_X = 'player:x'
        self.TYPE_PLAYER_O = 'player:o'

        self.lock = Lock()

        print("Game controller is initialised!")

    def connect(self, participant, join_type):
        player_type = ''

        self.lock.acquire()

        if join_type not in [self.TYPE_PLAYER, self.TYPE_SPECTATOR]:
            message = 'command join_type not recognised'
            self.lock.release()
            return {
                'status': 'ok',
                'message': message,
                'game_info': player_type
            }
        # Participant will become spectators when the players amount is fulfilled
        elif join_type == self.TYPE_SPECTATOR or len(self.players) >= self.max_players:
            spec = {
                'role': 'spectator',
                'info': participant
            }
            self.spectators.append(spec)
            message = 'joined as spectator'
        elif join_type == self.TYPE_PLAYER:
            if len(self.players):
                player_type = self.TYPE_PLAYER_O
            else:
                player_type = self.TYPE_PLAYER_X
            player = {
                'role': player_type,
                'info': participant
            }
            self.players.append(player)
            message = 'joined as player'

        self.lock.release()

        print(self.players)
        print(self.spectators)

        return {
            'status': 'ok',
            'message': message,
            'game_info': player_type
        }

    def make_a_move(self, location, player_type):
        self.game_positions[location] = player_type

    def ping(self):
        return {
            'status': 'ok'
        }


if __name__ == '__main__':
    grc = GameRoomController('identity123')
