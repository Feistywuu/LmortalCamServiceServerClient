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

''' CURRENTLY '''
# server receives information if there is a break in the client send loop, otherwise receives nothing - why?
# stuck at self.rfile(), when it stop reading the socket stream?
# +++++
# thread gets stuck on socket stream, can dedicate entire thread to socket stream, however we need to pass on the
#frames to the processing thread. We need some sort of information in bytecode/packet about end of frames.

' Plan of action'
#

''' figure out'''
# whilst one thread is 'stuck' in constant socket-stream, is that data availabe to other threads?
# If data is received in a big chunk, there has to be some frame-data/header information to signify the end of a
#frame?

# One thread listens for server-user events and client requests, and spawns handler thread upon accepting request
#/Server type create a thread for each request
# If using TCP stream socket, will need to create child process/thread for each client connection.
# put time in client udp packets to control framerate
# remember double-buffering,

#can use lower level socket module to define headers in UDP packets, to contain information on fps(?)

#listen while loop, to spawn thread for socket connecting

# can use handle_one_request to send to do() function

# create thread upon accepting client request
#socketserver.StreamRequestHandler
class HandlerClass(socketserver.StreamRequestHandler):

    def handle(self):

        fps, st, frames_to_count, cnt = (0, 0, 20, 0)
        print('hello?')
        while True:
            print('hi')
            self.data = self.request.recv(1024).strip()
            #self.data = self.rfile.readline().strip()
            print('hi2')
            print("{} wrote:".format(self.client_address[0]))
            print(self.data)
            data = base64.b64decode(self.data)
            print(data)
            npdata = np.frombuffer(data, dtype=np.uint8)
            print(npdata)
            frame = cv.imdecode(npdata, 1)
            print(frame)
            frame = cv.putText(frame, 'FPS: ' + str(fps), (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv.imshow("RECEIVING VIDEO", frame)
            key = cv.waitKey(1) & 0xFF
            if key == ord('q'):
                HandlerClass.finish(self)
                break
            if cnt == frames_to_count:
                try:
                    fps = round(frames_to_count / (time.time() - st))
                    st = time.time()
                    cnt = 0
                except:
                    pass
            cnt += 1
            time.sleep(2.0)

                # Likewise, self.wfile is a file-like object used to write back
                # to the client
                #self.wfile.write(self.data.upper())

        print('test')


if __name__ == "__main__":
    # get host ipv4
    HOST, PORT = socket.gethostbyname(socket.getfqdn()), 80

    # Create the server, binding to localhost on port 80, instantiating Handler of HandlerClass
    with http.server.ThreadingHTTPServer((HOST, PORT), HandlerClass) as server:
        # Activate the server; this will keep running until you interrupt the program with Ctrl-C
        server.serve_forever()







# UI

#window = tk.Tk()

# add widgets here

#window.title('Hello Python')
#window.geometry("300x200+10+20")
#window.mainloop()

