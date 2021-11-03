# Intermediatary to receive packets from client and edit them
import scapy.sendrecv
from scapy import asn1, contrib, layers, packet, sendrecv
import random
import socket
import base64
import struct
import math

# create a socket that listens
BUFF_SIZE = 65536
MiddleSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
MiddleSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)     # specify manipulation of socket at
host_name = socket.gethostname()                                            # api level
host_ip = socket.gethostbyname(host_name)
port = 9600

socket_address = (host_ip, port)
MiddleSocket.bind(socket_address)
print('Listening at:', socket_address)

' Problem' 'current'
# See is this bytes object can be changed and if that does anything, otherwise.
#'Bytes' object is immutable, so at what point can I change the ip source? Can I 'debyte' it then edit it?
# probably will have to go back to using scapy, which cannot be integrated with python.socket

# otherwise, might to use arp-spoofing + MitM - which *still* requires access to lower-level network layer, which
#we are denied by denial of raw sockets. So we have to use scapy, question is how.

# So can we just simply use scapy for testing then swap back to sockets for the actual application?

' Solutions'
# read about socket.setoptoopt

#inet_aton() converts internet host address cp from ipv4 numbers and dots notation into binary form( in network
#byte order) and store in the structure that inp points to.
#/or inet_addr()

# maybe we have access to ipv4 packet header, but not the udp


def InfoDump():
    ''' Shows information from packet header and datagram payload '''
    # show source ip
    pass


# receive packets
#/create a socket that listens on port 9600, it should accept udp, ip datagram frames.
while True:
    packet = MiddleSocket.recvfrom(BUFF_SIZE)

    # packet data from tuple
    packet = packet[0]

    # retrieve packet header data, of length 20 bytes
    header_length = 20
    header = packet[:header_length]
    header = struct.unpack('!BBHHHBBH4s4s', header)       # find out format req. length
    print(header)
    source_ip = socket.inet_ntoa(header[8])
    print(source_ip)

    # try scramble source ip
    for i in range(math.floor(len(header[8]))):
        header[8][i] = header[8][-i]
        print(header[8][i])
    print(header[8])

    pass



# receive packets
#/what are we receiving from client? And how should be receive it?

# send to original destination or hard code the destination yourself


' Research '
#(1)
# https://stackoverflow.com/questions/20768107/regarding-struct-unpack-in-python
#(2)
# https://stackoverflow.com/questions/42840636/difference-between-struct-ip-and-struct-iphdr
#/Here it seems byteorder must be defined - little endian or big endian, hence why we use socket.ntohs which
#'converts 16-bit positive integers from network to host byte order'
#/Endianness describing the order a sequence of bytes are stored in memory: big-endian where the 'big-end'
#is stored first, so storing things in a forward fashion and little-endian the opposite.
# https://www.techtarget.com/searchnetworking/definition/big-endian-and-little-endian

'''
# parse ethernet header
    eth_length = 14

    print(packet)
    eth_header = packet[:eth_length]
    print(eth_header)
    eth = struct.unpack('!6s6sH', eth_header)           # why? See (1)
    print(eth)
    eth_protocol = socket.ntohs(eth[2])                 # (2)
    print(eth_protocol)

'''