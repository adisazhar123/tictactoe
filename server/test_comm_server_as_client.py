import Pyro4
import time
from Pyro4.errors import CommunicationError


def connect_server():
    try:
        uri = "PYRONAME:main_server@localhost:1337"
        return Pyro4.Proxy(uri)
    except CommunicationError as e:
        print(e)


if __name__ == "__main__":
    server = connect_server()
    response = server.create_room_func('andi')
    print(response)
    time.sleep(2)
    response = server.available_rooms_func()
    print(response)