# Abstraction of scapy implementation of udp video data transfer
import scapy.supersocket, scapy.layers.inet, scapy.packet, scapy.layers.inet6, scapy.interfaces, scapy.config, scapy.utils
from scapy import sendrecv, supersocket
import cv2 as cv
import imutils
import base64
import time
import socket

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


class Packet:
    '''
    length = int = unsigned short
    udpTrue = bool = bool
    cookie = (int,int) = unsigned int
    '''

    def __init__(self, data):
        self.length = int
        self.udpTrue = bool
        self.cookie = (int, int)

        # checking if data fits within packet size, if not split over separate packets
        # so if payload is already in byteform
        BUFF_SIZE = 65536
        if data >= BUFF_SIZE:
            # get data, slice 65536 bytes off the front
            # create packet with a payload with remaining byte-string. Length as defined, udpTrue = true, cookie - same.
            # repeat step if needed
            pass
        else:
            self.payload = data

    def header(self):
        ''' Here the packet '''
        pass

    def raw(self):
        pass

    def send(self):
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




