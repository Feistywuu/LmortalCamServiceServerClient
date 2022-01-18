# Abstraction of scapy implementation of udp video data transfer
import scapy.supersocket, scapy.layers.inet, scapy.packet, scapy.layers.inet6, scapy.interfaces, scapy.config, scapy.utils
from scapy import sendrecv, supersocket
import cv2 as cv
import imutils
import base64
import time
import random
import socket
import string

# Define Packet class
    # attributes will be the contents of the packet header:
        # header( value/length of payload, packet type, cookie)
            # value = buf_size = 65536,thus unsigned short is fine
                # **be aware this isn't 1 memory too big**
                # this require the header to be sent separately, prior to the payload, or else they will be memory
                #overflow
            # packet type = bool (udp, or not udp)
            # cookie = unsigned int, we want a storage of 2^32, since at 30 fps, we will reach 2^16 in 30 minutes.
        # then we want to create the packet itself, with the payload, this will determine information in the
        #header
        #if payload is bigger than buf_size, then it must be split into different packets

        # then we will pack this into a string/byte format, using .pack()
    # payload should be callable by packet.raw()
    # define a send function, which can send the header and/or payload

''' to watch for '''
# beware the scope of n


def id_generator():
    """
    create client id at runtime that can be contained in packet header
    id of form: 'xxxxxxxx', where x can be lower/upper character or number 0-9
    thus of size, char = c: cccccccc
    :return: str
    """
    # string 8 characters long
    idString = ''
    for x in range(0, 7):
        deciderVar = random.randint(0, 1)
        if deciderVar == 0:
            letters = random.choice(string.ascii_letters)
            idString.join(letters)
        else:
            num = random.choice(string.digits)
            idString.join(num)

    return idString


IdentityCode = id_generator()
PacketNumber = 0                            # tracker variable, which goes up every time a packet is made

# BUFF_SIZE = 65516                 actual BUFF_SIZE = 65536, but 20 bytes to make space for socket header


class Packet:
    """
    length = int = unsigned short
    udpTrue = bool = bool
    cookie = (int,int) = unsigned int
    """

    def __init__(self, data, buffersize):
        global PacketNumber

        # internal values
        self.payload = str
        self.payloadPartitions = {}
        self.id = IdentityCode

        # header values
        self.length = int
        self.udpTrue = True
        self.cookie = (self.id, PacketNumber)


        # checking if data fits within packet size, if not, split over separate packets
        # provided payload is already in byteform
        n = '0'
        header_length = 11                      # short + bool + 8 chars = 2 + 1 + 8
        if len(data) >= BUFF_SIZE:

            # get data, slice byte-string into 65316 slices and make room for the header
            payload = data[header_length:BUFF_SIZE-header_length]
            remainder = data[BUFF_SIZE-header_length:]

            # add first partition to dict. of partitions
            self.payloadPartitions[n] = payload
            n = int(n)
            n += 1
            n = str(n)

            # split and add remaining payload to dictionary, iterating until there is one partitions worth left
            while len(remainder) >= BUFF_SIZE:
                self.payloadPartitions[n] = remainder[:BUFF_SIZE-header_length]
                remainder = remainder[BUFF_SIZE-header_length:]
                n = int(n)
                n += 1
                n = str(n)

            # last partition
            if len(remainder) != 0:
                self.payloadPartitions[n] = remainder[:]

            # set header values - length, add to packetNumber
            packetLength = 0
            for value in self.payloadPartitions.values():
                print(len(value))
                packetLength += len(value)
            self.length = packetLength
            PacketNumber += 1
        else:
            self.payload = data

    def partition(self, buffersize):
        """
        Takes the data payload of the packet and split into partitions specified by the buffer size
        :return:
        """

        if len(data) >= buffersize:

            # get data, slice byte-string into 65316 slices and make room for the header
            payload = data[header_length:buffersize-header_length]
            remainder = data[buffersize-header_length:]

            # add first partition to dict. of partitions
            self.payloadPartitions[n] = payload
            n = int(n)
            n += 1
            n = str(n)

            # split and add remaining payload to dictionary, iterating until there is one partitions worth left
            while len(remainder) >= buffersize:
                self.payloadPartitions[n] = remainder[:buffersize-header_length]
                remainder = remainder[buffersize-header_length:]
                n = int(n)
                n += 1
                n = str(n)

            # last partition
            if len(remainder) != 0:
                self.payloadPartitions[n] = remainder[:]

            # set header values - length, add to packetNumber
            packetLength = 0
            for value in self.payloadPartitions.values():
                print(len(value))
                packetLength += len(value)
            self.length = packetLength
            PacketNumber += 1
        else:
            self.payload = data


    def header(self):
        """
        Takes the packet header info, stored as object attributes, packs them in byteform.
        """
        pass

    def raw(self):
        """
        Take the payload from object attribute and
        :return:
        """
        pass

    def send(self):
        """
        Take a header or data payload and split into partitions if needed for buffer size
        Then send them via socket, if payload is split over partitions, send them
        iteratively in order.
        :return: null
        """
        pass


def packetSummary(pkt):
    ' Returns a tuple of (data, ip) from packet '

    if scapy.layers.inet.UDP in pkt:
        print(scapy.layers.inet.UDP.src)
        ip_src = pkt[scapy.layers.inet.UDP].src
        print(ip_src)

        # for interest
        print(pkt.layers())
        print(pkt[scapy.layers.inet.UDP].payload)
    else:
        ip_src = '0.0.0.0'
        print(''' couldn't identify packet as UDP / not received''')

    print('received and end')
    #return bytes(pkt[scapy.layers.inet.UDP].payload), ip_src


def scapySend(serverIP=None, destinationPort=None):
    ' Send packets using scapy library '

    # initialize video data, socket
    vid = cv.VideoCapture(0)
    BUFF_SIZE = 65536
    WIDTH = 400
    fps, st, frames_to_count, cnt = (0, 0, 20, 0)
    iface1 = 'Software Loopback Interface 1'
    scapy.config.conf.iface = 'Software Loopback Interface 1'

    # packet data
    sourcePort1 = 10002
    sourceIP1 = '192.168.1.191'
    sourcePort2 = 10002
    sourceIP2 = '200.200.200.200'


    # main send loop
    while True:

        # generate data payloads
        _, frame = vid.read()
        frame = imutils.resize(frame, width=WIDTH)
        encoded, buffer = cv.imencode('.jpg', frame, [cv.IMWRITE_JPEG_QUALITY, 80])
        message1 = base64.b64encode(buffer)
        message2 = 'I AM TESTING YOU!!!!!!!!'
        message2 = bytes(message2, 'utf-8')
        message2 = base64.b64encode(message2)

        # create packets with a spoofed ip
        packets = []
        packet1 = scapy.layers.inet.Loopback() / \
                 scapy.layers.inet.IP(dst=serverIP, src=sourceIP1) / \
                 scapy.layers.inet.UDP(sport=sourcePort1, dport=destinationPort) / message1
        #packet2 = scapy.layers.inet.Loopback() / \
        #          scapy.layers.inet.IP(dst=serverIP, src=sourceIP2) / \
        #          scapy.layers.inet.UDP(sport=sourcePort2, dport=destinationPort) / message2
        packets.append(packet1)
        #packets.append(packet2)
        scapy.sendrecv.sendp(x=packets, return_packets=True, iface=iface1)

        frame = cv.putText(frame, 'FPS: ' + str(fps), (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255),
                           2)
        cv.imshow('TRANSMITTING VIDEO', frame)
        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):
            # client_socket.close()
            # close scapy socket
            print('should exit')
            break
        if cnt == frames_to_count:
            try:
                fps = round(frames_to_count / (time.time() - st))
                st = time.time()
                cnt = 0
            except:
                pass
        cnt += 1


# receive data in a tuple with ip, so that it can be sorted via threading

# for incoming packets, perform function > returns tuple (data, ip)

def scapyRecv():
    ' Receive packets using scapy library '

    # initialize variables, socket
    #socket = scapy.supersocket.SuperSocket()
    port = 10004

    # listen for connection


    # receive data
    while True:

        packetlist = scapy.sendrecv.srp(filter='udp')
        # (opened_socket=True) w/ init. socke
        packet = packetlist[0]
        print(packetlist)
        print(packet.summary())
        #print(packet)
        print('before packet check')
        # check if udp AND ip, but also check a different way.
        try:
            if packet[scapy.layers.inet.UDP] and packet[scapy.layers.inet.IP]:
                #print(packet[scapy.layers.inet.UDP])
                #print(packet[scapy.layers.inet.IP])
                if packet[scapy.layers.inet.IP].src == '240.240.0.1':
                    print('sniffed the RIGHT packet')
                print(packet[scapy.layers.inet.IP].src)
                #ip_src = packet[scapy.layers.inet.IP].src
                #print(ip_src)
                #print(packet)
                #packet.show()
        except IndexError as e:
            print('sniffed the wrong packet ' + str(e))
            try:
                if packet[scapy.layers.inet.UDP] and packet[scapy.layers.inet6.IPv6]:
                    print('sniffed ipv6 packet: '+str(packet[scapy.layers.inet6.IPv6].src))
            except IndexError as e:
                print('Not UDP/(ipv4, ipv6): '+str(e))




