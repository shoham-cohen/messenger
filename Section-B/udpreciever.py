from data_packet import *
import socket

global expected_pkt, curr_pkt, pkt_buffer, pkt_list


class reciever:

    def __init__(self, server_IP, server_port):
        self.server_IP = server_IP
        self.server_port = server_port
        self.ack_port = server_port + 5

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('', server_port))
        self.server_socket = server_socket

        ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ack_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ack_socket.bind(('', self.ack_port))
        self.ack_socket = ack_socket

    def receive(self):
        global expected_pkt, curr_pkt, pkt_buffer, pkt_list
        expected_pkt = 0
        curr_pkt = -1
        pkt_buffer = []
        pkt_list = []
        flag = False

        while True:
            data, from_address = self.server_socket.recvfrom(1024)
            client_address = (from_address[0], from_address[1] + 5)
            temp = getdict(data)
            if checkSumVerification(data):
                ackpkt = createAck(temp['number'])
                self.ack_socket.sendto(ackpkt, client_address)
                print(temp['number'])
                if temp['number'] == expected_pkt:
                    expected_pkt += 1
                    curr_pkt = temp["number"]
                    pkt_list.append(data)
                    while pkt_buffer and pkt_buffer[0] == expected_pkt:
                        curr_pkt = expected_pkt
                        expected_pkt += 1
                        pkt_buffer.remove(pkt_buffer[0])
                        pkt_buffer.sort()

                elif temp['number'] > expected_pkt and temp['number'] not in pkt_buffer:
                    pkt_list.append(data)
                    pkt_buffer.append(temp['number'])
                    pkt_buffer.sort()

            for pkt in pkt_list:
                temp = getdict(pkt)
                if temp['number'] == curr_pkt:
                    if temp['pkt_type'] == 'close_pkt':
                        flag = True
                        break

            if flag:
                break

        for i in range(len(pkt_list)):
            temp = getdict(pkt_list[i])
            pkt_list[i] = temp

        final_data_list = sorted(pkt_list, key=lambda k: k['number'])

        for pkt in final_data_list:
            if pkt["pkt_type"] == "file_pkt":
                filename = "output_" + bytes(pkt['data']).decode('utf-8')
                break

        fd = open(filename, "wb")
        for pkt in final_data_list:
            if pkt["pkt_type"] == "data_pkt":
                fd.write(bytes(pkt['data']))
