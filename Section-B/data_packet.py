import json
import hashlib


# calculate the checksum using md5 func
def calculate_checksum(data, type, pkt_number, sent):
    temp = str(data) + ":" + type + ":" + str(pkt_number) + ":" + str(sent)
    return hashlib.md5(temp.encode()).hexdigest()


def make_pktlist(file_data, fname):
    packets = []
    packet_num = 0
    while len(file_data) != 0:
        data = file_data[:64]
        packet_num += 1
        csum = calculate_checksum(data, "data_pkt", packet_num - 1, False)
        data = make_json(data, "data_pkt", packet_num - 1, False, csum)
        packets.append(data)
        file_data = file_data[64:]

    packet_num += 1
    data = bytes(fname, 'utf-8')
    csum = calculate_checksum(data, "file_pkt", packet_num - 1, False)
    data = make_json(data, "file_pkt", packet_num - 1, False, csum)
    packets.append(data)

    packet_num += 1
    data = bytes("Bye", 'utf-8')
    csum = calculate_checksum(data, "close_pkt", packet_num - 1, False)
    data = make_json(data, "close_pkt", packet_num - 1, False, csum)
    packets.append(data)
    return packets


def check_checksum(pkt):
    curr = json.loads(pkt.decode('utf-8'))
    data = bytes(curr["data"])
    type = curr["type"]
    number = curr["number"]
    sent = curr["sent"]
    if calculate_checksum(data, type, number, sent) == curr['checksum']:
        return True
    else:
        return False


def check_ack(ack):
    ack_data = bytes(ack['data'])
    if calculate_checksum(ack_data, ack['type'], ack['number'], ack['sent']) == ack['checksum']:
        return True
    else:
        return False


def make_json(data, pkt_type, number, status, csum):
    pkt_dict = {
        "data": list(data),
        "type": pkt_type,
        "number": number,
        "sent": status,
        "checksum": csum

    }
    pkt_json = json.dumps(pkt_dict).encode('utf-8')
    return pkt_json


def getdict(pkt):
    return json.loads(pkt.decode('utf-8'))


def createAck(data_num):
    data = "Ack Sent"
    data = bytes(data, 'utf-8')
    csum = calculate_checksum(data, "ack", data_num, True)
    ackpkt = make_json(data, "ack", data_num, True, csum)
    return ackpkt
