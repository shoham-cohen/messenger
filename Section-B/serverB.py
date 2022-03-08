import socket
import threading
import time

from test import *
from udpsender import sender

HOST = input("server ip: ")
PORT = 55000
# creating the server socket and binds it
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

clients = []
nicknames = []
addresses = []
udpPorts = []
files = ["file1.txt", "file2.txt", "file3.png", "file4.pdf", "file5.gif"]


# send the message to the wanted clients
def broadcatst(message, To):
    for client in clients:
        index = clients.index(client)
        if nicknames[index] in To:
            client.send(message)


# listening to the client and handling its requests
def handle(client):
    while True:
        try:
            message = client.recv(1024)
            m = message.decode('utf-8')
            index = clients.index(client)
            nickname = nicknames[index]
            if "Private:" in m:
                To = list(m.split(" "))
                message = client.recv(1024)
                broadcatst(message, To[1:])
                print(f"#Private# To: {To[1:-1]} From: {message.decode('utf-8')}", end=" ")
            elif m == f"{nickname}: who is connected?\n":
                client.send(f"Online: {str(nicknames)}\n".encode('utf-8'))
            elif "SHOW_FILES" in m:
                Show_Files(client)
            elif "Downloading" in m:
                index = clients.index(client)
                address = addresses[index]
                down_thread = threading.Thread(target=Download, args=(client, address, m))
                down_thread.start()
            else:
                print(f"{m}", end=" ")
                broadcatst(message, nicknames)
        except:
            index = clients.index(client)
            clients.remove(client)
            address = addresses[index]
            addresses.remove(address)
            port = udpPorts[index]
            udpPorts.remove(port)
            client.close()
            nickname = nicknames[index]
            broadcatst(f"{nickname} is now offline\n".encode('utf-8'), nicknames)
            print(f"{nickname} is now offline")
            nicknames.remove(nickname)
            break


# receives new clients and starts the handle method
def receive():
    while True:
        client, address = server.accept()
        print(f"connected with {str(address)}!")

        nickname = client.recv(1024).decode('utf-8')

        nicknames.append(nickname)
        clients.append(client)
        addresses.append(address)
        print(f"Nickname of the client is {nickname}")
        time.sleep(2)
        broadcatst(f"{nickname} is now online!\n".encode('utf-8'), nicknames)
        client.send(f"PORT: {55000+clients.index(client)+1}".encode('utf-8'))
        udpPorts.append(int(55000+clients.index(client)+1))
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


def Show_Files(client):
    client.send(str(str(files)+"\n").encode('utf-8'))


def Download(client, address, m):
    fname = m[12:21]
    run_server(address[0], int(udpPorts[clients.index(client)]), int(16-len(clients)), int(8888), fname)


print("Server is running...")
receive()

