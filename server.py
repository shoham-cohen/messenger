import socket
import threading

HOST = '127.0.0.1'
PORT = 55000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

clients = []
nicknames = []


def broadcatst(message):
    for client in clients:
        client.send(message)


def handle(client):
    while True:
        try:
            message = client.recv(1024)
            m = message.decode('utf-8')
            print(f"{nicknames[clients.index(client)]} says {m}")
            broadcatst(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcatst(f"{nickname} is now offline".encode('utf-8'))
            nicknames.remove(nickname)
            break


def receive():
    while True:
        client, address = server.accept()
        print(f"connected with {str(address)}!")

        nickname = client.recv(1024).decode('utf-8')

        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname of the client is {nickname}")
        broadcatst(f"{nickname} connected to the server!\n".encode('utf-8'))
        #client.send("you are connected to the server\n".encode('utf-8'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("Server is running...")
receive()
