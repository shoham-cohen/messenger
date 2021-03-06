import socket
import threading

HOST = '127.0.0.1'
PORT = 55000

# creating the server socket and binds it
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

clients = []
nicknames = []


# send the message to the wanted clients
def broadcatst(message, To):
    for client in clients:
        index = clients.index(client)
        if nicknames[index] in To:
            client.send(message)


# listening to the client and handling it's requests
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
                client.send(f"Online: {str(nicknames)}".encode('utf-8'))
            else:
                print(f"{m}", end=" ")
                broadcatst(message, nicknames)
        except:
            index = clients.index(client)
            clients.remove(client)
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

        print(f"Nickname of the client is {nickname}")
        broadcatst(f"{nickname} connected to the server!\n".encode('utf-8'), nicknames)

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()
        # client.send("you are connected to the server\n".encode('utf-8'))


print("Server is running...")
receive()
