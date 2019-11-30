import Pyro4
from Pyro4.errors import CommunicationError


def connect_server():
    try:
        uri = "PYRONAME:game_room_server_CaRz@localhost:1337"
        return Pyro4.Proxy(uri)
    except CommunicationError as e:
        print(e)


server = connect_server()
response = server.ping()
print(response)

response = server.connect('gui-player:o', 'player')
print(response)
