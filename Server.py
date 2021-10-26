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
    #Spawn a thread to deal with data in each buffer and show on screen.

    # will create thread and execute handle() function upon receiving request
    pass


def handle(client_address=None):

    fps, st, frames_to_count, cnt = (0, 0, 20, 0)
    while True:
        print('ready to receive')
        packet, _ = server_socket.recvfrom(BUFF_SIZE)
        print('hi')
        print(packet)
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
    #request_handler()
    handle()

# UI

#window = tk.Tk()

# add widgets here

#window.title('Hello Python')
#window.geometry("300x200+10+20")
#window.mainloop()

