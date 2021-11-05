# Abstraction of scapy implementation of udp video data transfer
import scapy.supersocket, scapy.layers.inet, scapy.packet
from scapy import sendrecv, supersocket
import cv2 as cv

# use for send/receive scapy.sendrecv.sr
# this requires a supersocket instance

# create multiple sockets with different ip's


def packetSummary(pkt):
    ' Returns a tuple of (data, ip) from packet '

    if scapy.layers.inet.UDP in pkt:
        ip_src = pkt[scapy.layers.inet.UDP].src

        #for interest
        print(pkt.layers())
        print(pkt[scapy.layers.inet.UDP].payload)
    else:
        ip_src = '0.0.0.0'
        print(''' couldn't identify packet as UDP / not received''')

    return bytes(pkt[scapy.layers.inet.UDP].payload), ip_src


def scapySend():
    ' Send packets using scapy library '

    # inititlize video data, sockets
    vid = cv.VideoCapture(0)


    # pack video data into packet with spoofed ip's

    socket = scapy.supersocket.L3RawSocket()


    pass


# receive data in a tuple with ip, so that it can be sorted via threading

#for incoming packets, perform function > returns tuple (data, ip)

def scapyRecv():
    ' Receive packets using scapy library '


    packetSummary()

