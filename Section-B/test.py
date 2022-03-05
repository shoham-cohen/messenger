from udpreciever import *
from udpsender import *


class run_server:
    def __init__(self, SERVER_IP, SERVER_PORT, window, client_port):
        print(SERVER_IP, SERVER_PORT, window, client_port)
        print("server Mode: ON")
        c = sender(SERVER_IP, int(SERVER_PORT), int(window), int(client_port))
        filename = input("Enter File Name:")
        c.send(filename)


class run_client:
    def __init__(self, SERVER_IP, SERVER_PORT):
        print(SERVER_IP, SERVER_PORT)
        print("client Mode: ON")
        s = reciever(SERVER_IP, int(SERVER_PORT))
        s.receive()
        print("FILE RECEIVED")
        return
