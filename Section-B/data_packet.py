import json
import hashlib


def checksum(data, pkt_type, number, status):
    hash_str = str(data) + ":" + pkt_type + ":" + str(number) + ":" + str(status)
    return hashlib.md5(hash_str.encode()).hexdigest()


def make_pktlist(content, filename):
    packet_list = []
    pno = 0
    while len(content) != 0:
        data = content[:64]
        pno += 1
        csum = checksum(data, "data_pkt", pno - 1, False)
        data = jsonify(data, "data_pkt", pno - 1, False, csum)
        packet_list.append(data)
        content = content[64:]

    pno += 1
    file = filename
    data = bytes(file, 'utf-8')
    csum = checksum(data, "file_pkt", pno - 1, False)
    data = jsonify(data, "file_pkt", pno - 1, False, csum)
    packet_list.append(data)

    pno += 1
    bye = "Bye"
    data = bytes(bye, 'utf-8')
    csum = checksum(data, "close_pkt", pno - 1, False)
    data = jsonify(data, "close_pkt", pno - 1, False, csum)
    packet_list.append(data)
    return packet_list


def checkSumVerification(pkt):
    currpkt = json.loads(pkt.decode('utf-8'))
    d = bytes(currpkt["data"])
    t = currpkt["pkt_type"]
    n = currpkt["number"]
    s = currpkt["status"]
    if checksum(d, t, n, s) == currpkt['checksum']:
        return True
    else:
        return False


def check_ack(ack):
    ack_data = bytes(ack['data'])
    if checksum(ack_data, ack['pkt_type'], ack['number'], ack['status']) == ack['checksum']:
        return True
    else:
        return False


def jsonify(data, pkt_type, number, status, csum):
    pkt_dict = {
        "data": list(data),
        "pkt_type": pkt_type,
        "number": number,
        "status": status,
        "checksum": csum

    }
    pkt_json = json.dumps(pkt_dict).encode('utf-8')
    return pkt_json


def getdict(pkt):
    return json.loads(pkt.decode('utf-8'))


def createAck(data_num):
    data = "Ack Sent"
    data = bytes(data, 'utf-8')
    csum = checksum(data, "ack", data_num, True)
    ackpkt = jsonify(data, "ack", data_num, True, csum)
    return ackpkt
