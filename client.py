import os, sys
import socket, struct
from enum import IntEnum

from packet import Packet2


class Client:
    def __init__(self, port, idcode, remote_addr=False):
        self.port = port
        self.idcode = idcode
        self.remote_addr = remote_addr
        self.socket_addr = (remote_addr, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.packetnumber = 0
        self.port = port

    def recv(self):
        pass

    def listen(self):
        pass

    def send(self, buffer):
        packet = Packet2(self, buffer)
        self.packetnumber += 1

        offset = 0
        chunk_size = 32768

        while True:
            dblock = packet.tobytes(offset, chunk_size)
            packet.fragment += 1

            if packet.payload_length > offset + chunk_size:
                #print("Sent1: " + str(packet.idcode) + " Nr: " + str(packet.packetnumber) + " Length: " + str(packet.payload_length) + " Fragment: " + str(packet.fragment))
                self.sock.sendto(dblock, self.socket_addr)
                offset += chunk_size
            else:
                #print("Sent3: " + str(packet.idcode) + " Nr: " + str(packet.packetnumber) + " Length: " + str(packet.payload_length) + " Fragment: " + str(packet.fragment))
                self.sock.sendto(dblock, self.socket_addr)
                break


''' matte's receive thoughts '''


def recv(self):
    #packet = Packet2()

    #data, client_addr = server_socket.recvfrom(BUFF_SIZE)
    #hdr = Packet2.parse_header(data)
    # packet.parse_header(data)

    # header = struct.unpack('!I?8sI', data)

    # XXX move to class Packet
    #print("Header - Length: " + str(hdr.payload_length) + " Id: " + str(hdr.idcode) + " Pnr: " + str(hdr.packetnumber) + " Got: " + str(len(data)))


    #payloadLength = len(data)
    return  #packet

