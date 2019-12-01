import Pyro4
import time
from Pyro4.errors import CommunicationError, ConnectionClosedError
import threading
import os
import sys

server = None
interval = 1

def gracefully_exits():
    print("disconnecting..")
    time.sleep(0.5)
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)

def connect_server():
    try:
        uri = "PYRONAME:communication_server@localhost:1337"
        return Pyro4.Proxy(uri)
    except CommunicationError as e:
        print(e)

def communicate() -> bool:
    try:
        res = server.check_connection()
        if res == 'ok':
            pass
    except:
        return False
    return True

def job_ping_server_ping_ack() -> threading.Thread:
    t = threading.Thread(target=ping_server)
    t.start()
    return t

def ping_server():
    while True:
        alive = communicate()
        if not alive:
            alive = communicate()
            if not alive:
                print("\ncommunication server is down [DETECT BY ping ack]")
                break
        time.sleep(interval)
    gracefully_exits()

if __name__ == "__main__":
    server = connect_server()
    try:
        interval = server.ping_interval()
        server._pyroTimeout = interval
        t = job_ping_server_ping_ack()
    except:
        print('communication server not running')
        sys.exit(0)

    try:
        # please fill this section to communicate with communication server 
        # this server refers to communication server 
        # start section
        
        print(server.create_room_command())

        # end section to communicate, always wrap with try except 
    except (ConnectionClosedError, CommunicationError) as e:
        print(str(e))

    t.join()