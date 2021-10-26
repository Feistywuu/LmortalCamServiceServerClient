import tkinter as tk
import socket
import cv2 as cv
import numpy as np
import time
import base64
import imutils
from imutils.video import WebcamVideoStream, VideoStream
import base64
import sys

HOST, PORT = "192.168.1.160", 80

BUFF_SIZE = 65536
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
host_name = socket.gethostname()
host_ip = '192.168.1.160'   # socket.gethostbyname(host_name)
port = 9999

vid = cv.VideoCapture(0)

client_socket.connect((host_ip, port))

class GUI:

    def __init__(self, master):

        self.master = master
        # Main background window
        self.canvas = tk.Canvas(self.master, width=500, height=400)
        self.canvas.pack()
        self.master.title("LmortalCamsService")

        # create a socket (SOCK_STREAM means a TCP socket)
        def sendrequest(serverIP=None):
            fps, st, frames_to_count, cnt = (0, 0, 20, 0)
            print('test3')
            while True:

                WIDTH = 400
                while vid.isOpened():
                    print('test1')
                    _, frame = vid.read()
                    frame = imutils.resize(frame, width=WIDTH)
                    encoded, buffer = cv.imencode('.jpg', frame, [cv.IMWRITE_JPEG_QUALITY, 80])
                    message1 = base64.b64encode(buffer)
                    client_socket.sendto(message1, (serverIP, port))
                    frame = cv.putText(frame, 'FPS: ' + str(fps), (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255),
                                        2)
                    cv.imshow('TRANSMITTING VIDEO', frame)
                    key = cv.waitKey(1) & 0xFF
                    if key == ord('q'):
                        client_socket.close()
                        break
                    if cnt == frames_to_count:
                        try:
                            fps = round(frames_to_count / (time.time() - st))
                            st = time.time()
                            cnt = 0
                        except:
                            pass
                    cnt += 1

        print("Sent:     {}".format('things'))
        print("Received: {}".format('stuff back'))

        self.buttonTest = tk.Button(text='SendRequest', command=(lambda: sendrequest('192.168.1.160')))
        self.canvas.create_window(330, 50, window=self.buttonTest)

        # capture video from device
        def TestCamera():
            cap = cv.VideoCapture(0)
            cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv.CAP_PROP_FPS, 30)

            if not cap.isOpened():
                print("Cannot open camera")
                exit()
            while True:
                # capture frame-by-frame
                ret, frame = cap.read()

                # if frame is read correctly ret is True
                if not ret:
                    print("Can't receive frame (stream end?). Exiting ...")
                    break

                # Display the resulting frame
                cv.imshow('CameraService', frame)
                if cv.waitKey(1) == ord('q'):
                    break

            # When everything done, release the capture
            cap.release()
            cv.destroyAllWindows()

        self.buttonTest = tk.Button(text='Camera', command=TestCamera)
        self.canvas.create_window(200, 100, window=self.buttonTest)


master = tk.Tk()

gui = GUI(master)
master.mainloop()
