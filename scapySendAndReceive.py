# Abstraction of scapy implementation of udp video data transfer
import scapy.supersocket, scapy.layers.inet, scapy.packet, scapy.layers.inet6, scapy.interfaces, scapy.config, scapy.utils
from scapy import sendrecv, supersocket
import cv2 as cv
import imutils
import base64
import time
import socket


# use for send/receive scapy.sendrecv.sr
# this requires a supersocket instance

# create multiple sockets with different ip's

class Des:
    def __init__(self, port):
        self.port = port

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

    def send_packet(packet11, port):
        des = Des(port)

        def get_pack(packetx):
            udp = scapy.layers.inet.UDP()
            udp.sport = packetx[scapy.layers.inet.UDP].sport
            udp.dport = des.port
            udp.len = packetx[scapy.layers.inet.UDP].len

            ip = scapy.layers.inet.IP()
            ip.version = packetx[scapy.layers.inet.IP].version
            ip.tos = packetx[scapy.layers.inet.IP].tos
            ip.len = packetx[scapy.layers.inet.IP].len
            ip.id = packetx[scapy.layers.inet.IP].id
            ip.flags = packetx[scapy.layers.inet.IP].flags
            ip.frag = packetx[scapy.layers.inet.IP].frag
            ip.ttl = packetx[scapy.layers.inet.IP].ttl
            ip.proto = packetx[scapy.layers.inet.IP].proto
            ip.dst = '192.168.1.160'

            payload = packetx[scapy.packet.Raw].load

            pkt = ip / udp / payload
            pkt = pkt.__class__(bytes(pkt))

            scapy.sendrecv.send(pkt)

        return get_pack(packet11)


    # inititlize video data, socket
    vid = cv.VideoCapture(0)
    BUFF_SIZE = 65536
    WIDTH = 400
    fps, st, frames_to_count, cnt = (0, 0, 20, 0)
    sourcePort = 10002
    sourceIP = '192.168.1.160'
    iface1 = 'Software Loopback Interface 1'
    print(scapy.config.conf.ifaces)
    scapy.config.conf.iface = 'Software Loopback Interface 1'

    # main send loop
    while True:
        _, frame = vid.read()
        frame = imutils.resize(frame, width=WIDTH)
        encoded, buffer = cv.imencode('.jpg', frame, [cv.IMWRITE_JPEG_QUALITY, 80])
        message1 = base64.b64encode(buffer)

        # create packet with a spoofed ip
        packet = scapy.layers.inet.Loopback() / \
                 scapy.layers.inet.IP(dst=serverIP, src=sourceIP) / \
                 scapy.layers.inet.UDP(sport=sourcePort, dport=destinationPort) / message1

        #send_packet(packet, 10003)
        outboundpacket = scapy.sendrecv.sendp(x=packet, return_packets=True, iface=iface1)
        #print(list)
        #print(outboundpacket)
        #print(outboundpacket[0])
        #print(outboundpacket[0][scapy.layers.inet.IP].src)
        #print(outboundpacket[0][scapy.layers.inet.IP].dst)
        #print(outboundpacket[0][scapy.layers.inet.UDP].sport)
        #print(outboundpacket[0][scapy.layers.inet.UDP].dport)
        #outboundpacket.summary()
        print('hi')
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
    port = 10003

    # listen for connection


    # receive data
    while True:

        packetlist = scapy.sendrecv.sniff(filter='udp', count=1, store=True)
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




