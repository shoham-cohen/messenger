import socket
import threading
import time
from tkinter import *
import tkinter.scrolledtext
from tkinter import simpledialog

from test import run_client
from udpreciever import reciever

HOST = input("enter server ip: ")
PORT = 55000
SELF_IP = input("enter your ipv4 address: ")
UDP_PORT = -1

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

        self.files_button = tkinter.Button(self.win, text="Show files", command=self.Show_Files)
        self.files_button.config(font=("Ariel", 12))
        self.files_button.place(x=20, y=5)

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

        def Pop_Button1():
            filewin = Toplevel(self.win)
            button = Button(filewin, text="Download file1.txt", command=self.Download("file1.txt"))
            button.pack()

        def Pop_Button2():
            filewin = Toplevel(self.win)
            button = Button(filewin, text="Download file2.txt", command=self.Download("file2.txt"))
            button.pack()

        def Pop_Button3():
            filewin = Toplevel(self.win)
            button = Button(filewin, text="Download file3.png", command=self.Download("file3.png"))
            button.pack()

        def Pop_Button4():
            filewin = Toplevel(self.win)
            button = Button(filewin, text="Download file4.pdf", command=self.Download("file4.pdf"))
            button.pack()

        def Pop_Button5():
            filewin = Toplevel(self.win)
            button = Button(filewin, text="Download file5.gif", command=self.Download("file5.gif"))
            button.pack()

        menubar = Menu(self.win)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="file1.txt", command=Pop_Button1)
        filemenu.add_command(label="file2.txt", command=Pop_Button2)
        filemenu.add_command(label="file3.png", command=Pop_Button3)
        filemenu.add_command(label="file4.pdf", command=Pop_Button4)
        filemenu.add_command(label="file5.gif", command=Pop_Button5)

        menubar.add_cascade(label="File", menu=filemenu)

        self.win.config(menu=menubar)

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
                if "PORT:" in message:
                    x = message.split(" ")
                    self.UDP_PORT = int(x[1])
                    print(self.UDP_PORT)
                elif self.gui_done:
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

    def Show_Files(self):
        self.sock.send("SHOW_FILES".encode('utf-8'))

    def Download(self, FileName):
        self.sock.send(("Downloading "+FileName+"\n").encode('utf-8'))
        run_client(SELF_IP, self.UDP_PORT)
        self.sock.send("file received\n".encode('utf-8'))


client = Client(HOST, int(PORT))
