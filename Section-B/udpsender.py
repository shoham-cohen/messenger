import socket
import threading
from packet import *
import time

global win_start, curr_ack, exp_ack, acks_buff, lock, num_of_pckts, packets
win_start = -1
curr_ack = -1
exp_ack = 0
acks_buff = []
packets = []


class sender:

    def __init__(self, server_IP, server_port, window, client_pkt_port):

        self.server_IP = server_IP
        self.server_port = server_port
        self.window = window
        self.pkt_port = client_pkt_port
        self.ack_port = client_pkt_port + 5
        self.server_address = (server_IP, server_port)

        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        send_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        send_socket.bind(('', self.pkt_port))
        self.send_socket = send_socket

        ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ack_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ack_socket.bind(('', self.ack_port))
        self.ack_socket = ack_socket

    def run(self):
        global win_start, curr_ack, exp_ack, acks_buff, lock, packets
        while True:
            if curr_ack == num_of_pckts and not acks_buff:
                return

            data, address = self.ack_socket.recvfrom(1024)
            data = json.loads(data.decode('utf-8'))
            if check_ack(data):
                with lock:
                    ack_number = data['number']
                    if ack_number > exp_ack and ack_number not in acks_buff:
                        print("Out of order : ", ack_number)
                        acks_buff.append(ack_number)
                        acks_buff.sort()
                        temppkt = json.loads(packets[ack_number].decode('utf-8'))
                        temppkt['sent'] = True
                        packets[ack_number] = make_json(temppkt['data'], temppkt['type'], temppkt['number'],
                                                        temppkt['sent'], temppkt['checksum'])

                    elif ack_number == exp_ack:
                        print(ack_number)
                        curr_ack += 1
                        exp_ack += 1
                        temppkt = json.loads(packets[ack_number].decode('utf-8'))
                        temppkt['sent'] = True
                        packets[ack_number] = make_json(temppkt['data'], temppkt['type'], temppkt['number'],
                                                        temppkt['sent'], temppkt['checksum'])
                        print(acks_buff)
                        while acks_buff and acks_buff[0] == exp_ack:
                            curr_ack = exp_ack
                            exp_ack = acks_buff[0] + 1
                            acks_buff.remove(acks_buff[0])
                            acks_buff.sort()

    def send(self, filename):
        fd = open(filename, 'rb')
        content = fd.read()
        global win_start, curr_ack, exp_ack, acks_buff, lock, num_of_pckts, packets
        packets = make_pktlist(content, filename)
        num_of_pckts = len(packets) - 1
        lock = threading.Lock()
        acks_buff = []

        def reset_head():
            while True:
                global win_start, curr_ack, exp_ack, acks_buff, lock
                if curr_ack < num_of_pckts:
                    win_start = curr_ack
                time.sleep(0.7)

        win_thread = threading.Thread(target=reset_head)
        ack_thread = threading.Thread(target=self.run)
        ack_thread.start()
        time.sleep(0.7)
        win_thread.start()

        while curr_ack < num_of_pckts:
            with lock:
                while win_start - curr_ack < self.window:
                    win_start += 1
                    if win_start > num_of_pckts:
                        break
                    curr_pkt = json.loads(packets[win_start].decode('utf-8'))
                    if not curr_pkt['sent']:
                        print("Sending Packet to Server: ", curr_pkt['number'])
                        self.send_socket.sendto(packets[win_start], self.server_address)

        ack_thread.join()
        return
