import Pyro4
from Pyro4.errors import CommunicationError


def connect_server():
    try:
        uri = "PYRONAME:gui_server_adistya@localhost:1337"
        return Pyro4.Proxy(uri)
    except CommunicationError as e:
        print(e)


server = connect_server()
response = server.ping()
print(response)