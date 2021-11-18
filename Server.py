import tkinter as tk
import socket
import http.server
import base64
import numpy as np
import cv2 as cv
import time
import io
from io import IOBase as IO
import threading
import socketserver
import imutils
import socketSendAndReceive
import scapySendAndReceive

' Plan of action'
# create Handler that creates a thread for each request     - CURRENT
#- placing stuff from buffer into their own lists
# create server ui

'''Current'''
# abtract away socket, then create scapy abstraction for testing use
# see how scapy receives udp datagrams to emulate socket.recvfrom

'currentcurrent'
# currently on scapy, send/recv + integrate video into send.
# then implement multiple sockets, sending with spoofed ip's - \\\ go back and init. sockets \\\

# need to find separate send/receive functions in scapy
#/send and sniff?
#/payload might not be in the right form - https://stackoverflow.com/questions/39225108/send-scapy-packets-through-raw-sockets-in-python
# OSError: [WinError 10057] A request to send or receive data was disallowed because the socket is not
#connected and (when sending on a datagram socket using a sendto call) no address was supplied

#send at layer 2/3 and how to receive? Does the sniffer sniff the receiving socket or?
# it seems sniffing happens on layer 2 - interface

# might have to create a sniffing thread
#0000 Ether / IP / UDP 192.168.1.160:57688 > 239.255.255.250:ssdp / Raw
#0000 Ether / IP / UDP 51.178.185.84:5152 > 192.168.1.160:5060 / Raw
#which implies we're not receiving on a dedicated port/socket?

# This is our packet - study this:
#<Sniffed: TCP:0 UDP:0 ICMP:0 Other:1>
# 00:00:40:11:39:7f > 45:00:00:24:00:01 (0x7f00) / Raw

# these look like mac addresses?
#/ thus being sent locally between 2 devices on same network - layer 2.
#*correct* was being sent at layer 2

# try fiddling with filters, starting with none to see if I'm receiving packets whatsoever
#/looks like mac address may still be being used despite send layer 3
#/removing filters means server doesn't flush buffer?

#Clearly not getting my packets, but other interesting ones:
#/57621 - spotify
# Lots of ipv6 packets sent to/from *pc* ipv6 address and default gateway, for domains open in chrome.
#/So we can see access to and from the default gateway to our PC, is there a way to sniff packets sent/received
#from default gateway on the other side?

# So we are not getting packets - fiddle with things:
#Possibilities: packet payload of the wrong form, packet header is of the wrong form, sent the wrong way. +?

#Diagonosing:
# Checking of client-side: definitely sending UDP; get summary -
# IP / UDP 127.0.0.1:10002 > 192.168.1.160:10003 / Raw
# Check integrity of payload:
# ip source/dest all correct, udp port all correct, payload is fine before sending client-side
# It is simply not getting there - issue with method of transport.

#
# have i bound the udp ports correctly? bind_layers()
# do i need to define the route taken?

# What am i trying to do? Simulate multiple clients with different source ip's on packets.
#/this can be done server-side after receiving IF modifying on client prior to sending screw up sending.
#/Test

#simply get it to send.
# same network so send via layer 2?
# or define sockets to help send

#does sniffer work on stuff coming from network loopback?
# test different ifaces
# test with python.socket to receive data on

#test with python.socket: try out differnt ifaces
# can we use two ports on same interface, or the rerouted to the loopback interface?
# tried with interface on client, maybe try changing server-side - sniff(), sniffs interfaces by default

# Sending from packet from same address to another port works with sockets, but not with scapy - common issue -
#but I'm not using loopback and sending to source address doesn't seem to be related.

#https://stackoverflow.com/questions/65466433/scapy-sniffed-udp-packets-can-not-be-received-after-sending-to-another-host
# use wireshark to determine what is actually happening
# It seems packet transferred from same address > different ports use for the loopback, thus running into
#problems with scapy.
#SO Wireshark now sees the packet being transferred, but scapy.sniff() doesn't see it - explore


def request_handler():
    threads = []
    #listens to connection from client, upon receiving, kill connection,
    # create thread and listen again for connection, upon confirming the same, handle
    # - will listening in first half pick-up a socket connecting in another thread?
    #OR
    # listen for request, if received, stop listening.
    # create thread and send task of listening to that thread

    ' If multiple connections to single socket'
    # handler can establish connection and then append to a list(buffer) which is defined by sender's address.
    #if receiving lots of information from socket, may take too long sorting each into a buffer for each thread.
    #Spawn a thread to deal with data in each buffer and show on screen.
    # each thread will take a image packet, then let another take a packet whilst the first is processing.

    ''' Multiple different datasets incoming on one socket - how to split?'''
    # Each client will have a different ip address - can use ip in header to then append to a list.
    # Does recvfrom create a buffer for each client address?
    # and how would I test this?

    ' Solution? '
    # Buffer will be a global variable
    # Multiple threads can access it using a lock system of some sort, thus each thread will be doing the
    #'sorting' per say, iterating through buffer to grab frames valid for it.

    ''' Abstract away different send/receive methods so I don't have to write 2x server/client models'''

    'later'
    #IIS on windows 10, app pools
    #iostream

    #socketSendAndReceive.socketReceive()
    scapySendAndReceive.scapyRecv()


def handle(packet, threadsocket):

    fps, st, frames_to_count, cnt = (0, 0, 20, 0)
    while True:
        data = base64.b64decode(packet, ' /')
        npdata = np.fromstring(data, dtype=np.uint8)
        frame = cv.imdecode(npdata, 1)
        frame = cv.putText(frame, 'FPS: ' + str(fps), (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv.imshow("RECEIVING VIDEO", frame)
        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):
            threadsocket.close()
            break
        if cnt == frames_to_count:
            try:
                fps = round(frames_to_count / (time.time() - st))
                st = time.time()
                cnt = 0
            except:
                pass
        cnt += 1


if __name__ == "__main__":
    request_handler()
    #handle()

# UI

#window = tk.Tk()

# add widgets here

#window.title('Hello Python')
#window.geometry("300x200+10+20")
#window.mainloop()

