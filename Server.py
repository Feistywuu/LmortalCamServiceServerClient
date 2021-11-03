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

' Plan of action'
# create Handler that creates a thread for each request     - CURRENT
#- placing stuff from buffer into their own lists
# create server ui

''' Figure Out '''
#how to break the program

BUFF_SIZE = 65536
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print(host_ip)
port = 9999

socket_address = (host_ip, port)
server_socket.bind(socket_address)
print('Listening at:', socket_address)




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

    ''' Spoofing IP addresses to test threading'''  # CURRENT
    # Either use a library like scapy or find information in packet headers and edit them?
    # Editing information in packet headers may require admin privileges

    ''' CURRENT'''
    # Learn to use winpcap or scapy to edit/send packets
    # winpcap is much lower level, whereas scapy would have the whole process of packet sniffing abstracted out
    #rather than having to: https://stackoverflow.com/questions/34842326/mitm-with-winpcap-and-or-sockets-c
    #/We receive the datagram payload, but no packet headers or anything

    # Finding right modules in scapy to use

    # Currently able to edit source address in packet header, however the problem may remain that
    #upon receive the source address is corrected, in which cause arp poisoning(?) may be required?

    'later'
    #IIS on windows 10, app pools
    #iostream



    # receive data from socket
    First = True
    while True:
        buffer, client_adress = server_socket.recvfrom(BUFF_SIZE)
        print('start')
        print(buffer)
        print(client_adress)
        buffer = bytes.decode(buffer, 'utf-8')          # is this needed? Or can i just slice it
        print(buffer)
        buffer = base64.b64decode(buffer)
        print(buffer)
        print(buffer[:20])
        buffer = bytes.decode(buffer, 'utf-8')
        print(buffer[:20])
        #buffer = buffer.decode('hex')
        #print(buffer)

        #rawIp = buffer[:20]
        #rawIp = str(rawIp)
        #print(rawIp)

        print('test')

        # initialize first time connection settings
        if First:
            #create list and append to it
            #spawn thread and work on list
            pass

        First = False


def handle(packet):

    fps, st, frames_to_count, cnt = (0, 0, 20, 0)
    while True:
        data = base64.b64decode(packet, ' /')
        npdata = np.fromstring(data, dtype=np.uint8)
        frame = cv.imdecode(npdata, 1)
        frame = cv.putText(frame, 'FPS: ' + str(fps), (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv.imshow("RECEIVING VIDEO", frame)
        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):
            server_socket.close()
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

