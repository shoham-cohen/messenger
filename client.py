import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog

HOST = input("enter server ip: ")
PORT = input("enter port: ")


class Client:

    def __init__(self, host, port):
        # creating the client socket and connecting it to the server socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        # GUI
        msg = tkinter.Tk()
        msg.withdraw()
        # get a nickname
        self.nickname = simpledialog.askstring("Nickname", "please choose a nickname", parent=msg)
        self.sock.send(self.nickname.encode('utf-8'))

        self.gui_done = False
        self.running = True
        # run two threads at the same time
        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    # the GUI is pretty simple...
    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")

        self.chat_label = tkinter.Label(self.win, text="Chat: ", bg="lightgray")
        self.chat_label.config(font=("Ariel", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win, height=10)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')

        self.ToWho_label = tkinter.Label(self.win, text="Who to send (blank to all): ", bg="lightgray")
        self.ToWho_label.config(font=("Ariel", 12))
        self.ToWho_label.pack(padx=20, pady=5)

        self.ToWho = tkinter.Text(self.win, height=2, width=20)
        self.ToWho.pack(padx=20, pady=5)

        self.msg_label = tkinter.Label(self.win, text="Message: ", bg="lightgray")
        self.msg_label.config(font=("Ariel", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=2, width=50)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write)
        self.send_button.config(font=("Ariel", 12))
        self.send_button.pack(padx=20, pady=5)

        self.disconnect_button = tkinter.Button(self.win, text="Disconnect", command=self.stop)
        self.disconnect_button.config(font=("Ariel", 12))
        self.disconnect_button.pack(padx=0, pady=5)

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    # write a message, it gets to the server who sends it to the other clients
    def write(self):
        To_Who = self.ToWho.get('1.0', 'end')
        if To_Who == '\n':
            message = f"{self.nickname}: {self.input_area.get('1.0', 'end')}"
            self.sock.send(message.encode('utf-8'))
            self.input_area.delete('1.0', 'end')
        else:
            firstM = f"Private: {To_Who}"
            self.sock.send(firstM.encode('utf-8'))
            self.ToWho.delete('1.0', 'end')
            message = f"{self.nickname}: {self.input_area.get('1.0', 'end')}"
            self.sock.send(message.encode('utf-8'))
            self.input_area.delete('1.0', 'end')

    # stop the GUI of a client and disconnect him from the server
    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.send("".encode('utf-8'))
        self.sock.close()
        exit(0)

    # listening to the server and showing it in the GUI
    # to receive the list of online clients type in the chat- who is connected?
    # to send private message write in the proper place the nicknames of the wanted
    # clients and space between every one including the last one
    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                if self.gui_done:
                    self.text_area.config(state='normal')
                    self.text_area.insert('end', message)
                    self.text_area.yview('end')
                    self.text_area.config(state='disabled')
            except ConnectionAbortedError:
                break
            except:
                print("Error")
                self.sock.close()
                break


client = Client(HOST, int(PORT))
