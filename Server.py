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
# import scapySendAndReceive

' Plan of action'
# create Handler that creates a thread for each request     - CURRENT
#- placing stuff from buffer into their own lists
# create server ui

'''Current'''
# abtract away socket, then create scapy abstraction for testing use
# see how scapy receives udp datagrams to emulate socket.recvfrom

'currentcurrent'
# currently on scapy, send/recv + integrate video into send.


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

    socketSendAndReceive.socketReceive()


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

