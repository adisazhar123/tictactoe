import Pyro4
import queue
from threading import Lock, Thread

from Pyro4.errors import CommunicationError


@Pyro4.expose
class GameRoomController:
    def __init__(self, identity):
        self.game_room_name = identity
        self.players = []
        self.spectators = []

        # pyro objects of participants
        self.participant_connections = []

        # init types
        self.TYPE_SPECTATOR = 'spectator'
        self.TYPE_PLAYER = 'player'

        self.TYPE_PLAYER_X = 'player:x'
        self.TYPE_PLAYER_O = 'player:o'

        # Init tic tac toe positions
        self.game_positions = [None] * 9
        self.max_players = 2

        self.communication_server = self.connect_to_server("communication_server")

        self.game_ended = 0

        self.player_turn = self.TYPE_PLAYER_X

        self.positions_to_update = queue.Queue()

        self.lock = Lock()

        print("Game controller is initialised!")

    def connect_to_server(self, name):
        try:
            uri = "PYRONAME:{}@localhost:1337".format(name)
            return Pyro4.Proxy(uri)
        except CommunicationError as e:
            print(e)

    def connect(self, participant, join_type, username):
        player_type = None

        self.lock.acquire()

        if join_type not in [self.TYPE_PLAYER, self.TYPE_SPECTATOR]:
            message = 'command join_type not recognised'
            self.lock.release()
            return {
                'status': 'error',
                'message': message,
                'data': {
                    'participant_type': player_type,
                    'positions': self.game_positions
                }
            }
        player_exist = 0
        p = None
        for player in self.players:
            if player['username'] == username:
                player_exist = 1
                p = player
                player_type = player['role']
                break
        if player_exist:
            self.players.remove(p)
            player = {
                'role': player_type,
                'info': participant,
                'username': username
            }
            self.players.append(player)
            message = 'joined as player'
        # Participant will become spectators when the players amount is fulfilled
        elif join_type == self.TYPE_SPECTATOR or len(self.players) >= self.max_players:
            spec = {
                'role': 'spectator',
                'info': participant
            }
            self.spectators.append(spec)
            self.positions_to_update.put(self.game_positions)
            player_type = 'spectator:{}'.format(len(self.spectators))
            message = 'joined as spectator'
        elif join_type == self.TYPE_PLAYER and not player_exist:
            if len(self.players):
                player_type = self.TYPE_PLAYER_O
            elif not len(self.players):
                player_type = self.TYPE_PLAYER_X
            player = {
                'role': player_type,
                'info': participant,
                'username': username
            }
            self.players.append(player)
            message = 'joined as player'

        self.lock.release()

        print('players: ', self.players)
        print('spectators: ', self.spectators)

        participant_connection = self.connect_to_server("gui_server_{}".format(participant['identifier']))
        print(participant_connection)
        self.participant_connections.append(participant_connection)
        self.positions_to_update.put(self.game_positions)

        return {
            'status': 'ok',
            'message': message,
            'total_player': len(self.players),
            'data': {
                'participant_type': player_type,
                'positions': self.game_positions,
                'turn': self.player_turn
            }
        }

    def make_a_move(self, location, player_type):
        if player_type not in [self.TYPE_PLAYER_X, self.TYPE_PLAYER_O]:
            return {
                'status': 'error',
                'message': 'only player_type player can move',
                'data': {
                    'winner': None,
                    'positions': self.game_positions,
                    'turn': self.player_turn
                }
            }
        elif self.game_positions[location] is not None:
            return {
                'status': 'error',
                'message': 'position is not empty',
                'data': {
                    'winner': None,
                    'positions': self.game_positions,
                    'turn': self.player_turn
                }
            }
        elif self.player_turn != player_type:
            return {
                'status': 'error',
                'message': 'it is {} turn'.format(self.player_turn),
                'data': {
                    'winner': None,
                    'positions': self.game_positions,
                    'turn': self.player_turn
                }
            }
        self.lock.acquire()

        self.game_positions[location] = player_type
        response = self.check_winner()
        self.positions_to_update.put(self.game_positions)
        self.change_player_turn()
        self.update_positions()
        if response is not None:
            self.announce_winner(response)
            self.game_ended = 1
            res = self.communication_server.game_ended(self.game_room_name)
            print('response for game ended: {}'.format(res))
        self.lock.release()

        return {
            'status': 'ok',
            'message': 'successfully moved',
            'data': {
                'winner': response,
                'positions': self.game_positions,
                'turn': self.player_turn
            }
        }

    def change_player_turn(self):
        if self.player_turn == self.TYPE_PLAYER_X:
            self.player_turn = self.TYPE_PLAYER_O
        else:
            self.player_turn = self.TYPE_PLAYER_X

    def check_winner(self):
        # Check horizontal
        if self.game_positions[0] == self.game_positions[1] == self.game_positions[2] is not None:
            return self.game_positions[0]
        elif self.game_positions[3] == self.game_positions[4] == self.game_positions[5] is not None:
            return self.game_positions[3]
        elif self.game_positions[6] == self.game_positions[7] == self.game_positions[8] is not None:
            return self.game_positions[6]

        # Check vertical
        elif self.game_positions[0] == self.game_positions[3] == self.game_positions[6] is not None:
            return self.game_positions[0]
        elif self.game_positions[1] == self.game_positions[4] == self.game_positions[7] is not None:
            return self.game_positions[1]
        elif self.game_positions[2] == self.game_positions[5] == self.game_positions[8] is not None:
            return self.game_positions[2]

        # Check horizontal
        elif self.game_positions[0] == self.game_positions[4] == self.game_positions[8] is not None:
            return self.game_positions[0]
        elif self.game_positions[2] == self.game_positions[4] == self.game_positions[6] is not None:
            return self.game_positions[2]

        return None

    def ping(self):
        return {
            'status': 'ok'
        }

    def update_positions(self):
        position = self.positions_to_update.get()
        to_remove = []
        for participant in self.participant_connections:
            try:
                participant.update_positions(position, self.player_turn)
            except CommunicationError as e:
                print(e)
                to_remove.append(participant)
        for participant in to_remove:
            self.participant_connections.remove(participant)

    def announce_winner(self, winner):
        for participant in self.participant_connections:
            try:
                participant.get_the_winner(winner)
            except CommunicationError as e:
                print(e)
