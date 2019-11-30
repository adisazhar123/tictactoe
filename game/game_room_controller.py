import Pyro4
from threading import Lock, Thread

# TODO:
# 1. contact main server once initialized
# 2. propagate data to connected users


@Pyro4.expose
class GameRoomController:
    def __init__(self, identity):
        self.game_room_name = identity
        self.players = []
        self.spectators = []

        # init types
        self.TYPE_SPECTATOR = 'spectator'
        self.TYPE_PLAYER = 'player'

        self.TYPE_PLAYER_X = 'player:x'
        self.TYPE_PLAYER_O = 'player:o'

        # Init tic tac toe positions
        self.game_positions = [None] * 9
        self.max_players = 2

        self.player_turn = self.TYPE_PLAYER_X

        self.lock = Lock()

        print("Game controller is initialised!")

    def connect(self, participant, join_type):
        player_type = None

        self.lock.acquire()

        if join_type not in [self.TYPE_PLAYER, self.TYPE_SPECTATOR]:
            message = 'command join_type not recognised'
            self.lock.release()
            return {
                'status': 'ok',
                'message': message,
                'data': player_type
            }
        # Participant will become spectators when the players amount is fulfilled
        elif join_type == self.TYPE_SPECTATOR or len(self.players) >= self.max_players:
            spec = {
                'role': 'spectator',
                'info': participant
            }
            self.spectators.append(spec)
            player_type = 'spectator:{}'.format(len(self.spectators))
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

        print('players: ', self.players)
        print('spectators: ', self.spectators)

        return {
            'status': 'ok',
            'message': message,
            'data': player_type
        }

    def make_a_move(self, location, player_type):
        self.lock.acquire()
        self.game_positions[location] = player_type
        response = self.check_winner()
        self.lock.release()
        print('game positions: ', self.game_positions)

        return {
            'status': 'ok',
            'message': 'successfully moved',
            'data': {
                'winner': response,
                'positions': self.game_positions
            }
        }

    def check_winner(self):
        # Todo return which player won
        # Check horizontal
        if self.game_positions[0] == self.game_positions[1] == self.game_positions[2] is not None \
                or self.game_positions[3] == self.game_positions[4] == self.game_positions[5] is not None \
                or  self.game_positions[6] == self.game_positions[7] == self.game_positions[8] is not None:
            return "a winner is found"
        # Check vertical
        elif self.game_positions[0] == self.game_positions[3] == self.game_positions[6] is not None \
                or self.game_positions[1] == self.game_positions[4] == self.game_positions[7] is not None \
                or self.game_positions[2] == self.game_positions[5] == self.game_positions[8] is not None:
            return "a winner is found"
        # Check horizontal
        elif self.game_positions[0] == self.game_positions[4] == self.game_positions[8] is not None \
                or self.game_positions[2] == self.game_positions[4] == self.game_positions[6] is not None:
            return "a winner is found"
        return None

    def ping(self):
        return {
            'status': 'ok'
        }
