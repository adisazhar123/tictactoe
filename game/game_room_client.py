import Pyro4
from Pyro4.errors import CommunicationError


def connect_server():
    try:
        uri = "PYRONAME:game_room_server_ZVLG@localhost:1337"
        return Pyro4.Proxy(uri)
    except CommunicationError as e:
        print(e)


server = connect_server()
response = server.ping()
print(response)

response = server.connect('gui-player:o', 'player')
print(response)

response = server.make_a_move(0, 'o')
response = server.make_a_move(1, 'x')
response = server.make_a_move(2, 'f')

response = server.make_a_move(3, 'f')
response = server.make_a_move(4, 'c')
response = server.make_a_move(5, 'j')

response = server.make_a_move(6, '4')
response = server.make_a_move(7, 'h')
response = server.make_a_move(8, 'q')

print(response)
