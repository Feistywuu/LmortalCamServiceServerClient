import tkinter as tk
import requests
import socket
import sys
import cv2 as cv
import numpy as np
import time
import base64
import os   #change this later to generalize to users\user\videos\
from imutils.video import WebcamVideoStream, VideoStream

HOST, PORT = "192.168.1.160", 80

# can set video dimensions using cv.cap_prop_width etc
#https://docs.opencv.org/master/dd/d43/tutorial_py_video_display.html
#create dropdown for each option in gui


#test = cv.namedWindow('CameraService', cv.WINDOW_AUTOSIZE)
#cv.resizeWindow('CameraService', 1000,700)
streamobject = VideoStream(resolution=(640, 480))
streamobject.start()

# we have access to the frames taking by webcam, now to designate frequency/framerate, how to encode this to
#video form, or a form that can built on server from bytes.

#What form do we send video over as?

#consider the first frame.

class GUI():

    def __init__(self, master):

        self.master = master
        # Main background window
        self.canvas = tk.Canvas(self.master, width=500, height=400)
        self.canvas.pack()
        self.master.title("LmortalCamsService")

        # create a socket (SOCK_STREAM means a TCP socket)
        def sendrequest(serverIP=None):
            fps, st, frames_to_count, cnt = (0, 0, 20, 0)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                # connect to server
                sock.connect((HOST, PORT))
                while True:

                    #try:
                    #send data containing frame, if doesn't exist, except
                    frame = streamobject.stream.read()
                    encoded, buffer = cv.imencode('.jpg', frame, [cv.IMWRITE_JPEG_QUALITY, 80])
                    message = base64.b64encode(buffer)
                    sock.sendto(message, (serverIP, 80))
                    frame = cv.putText(frame, 'FPS: ' + str(fps), (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255),
                                        2)
                    cv.imshow('TRANSMITTING VIDEO', frame)
                    key = cv.waitKey(1) & 0xFF
                    if key == ord('q'):
                        sock.close()
                        print('should break?')
                        break
                    if cnt == frames_to_count:
                        try:
                            fps = round(frames_to_count / (time.time() - st))
                            st = time.time()
                            cnt = 0
                        except:
                            pass
                    cnt += 1

                    #time.sleep(5)

                    #except:
                        #send dummy data to server
                        #sock.sendall(bytes(string + "\n", "utf-8"))

                        # Receive data from the server and shut down
                        #received = str(sock.recv(1024), "utf-8")
                    #break

            print("Sent:     {}".format('things'))
            print("Received: {}".format('stuff back'))

        self.buttonTest = tk.Button(text='Save Boundary', command=(lambda: sendrequest('192.168.1.160')))
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




'Extras'
# can get tk.OptionMenu for dropdown if wanted for camera choice/video quality

#using class WebcamVideoStream from umutils, which uses a daemon thread to read from frames from the video stream,
#allowing option to read and stop

'''
BUFF_SIZE = 65536
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
clientname = socket.gethostbyname()
clientIP = "192.168.1.160" #socket.gethostbyname(clientname)
#HOST, PORT = "192.168.1.160", 9999
port = 9999
socket_address = (clientIP, port)
clientSocket.bind(socket_address)
print('Listening at:',socket_address)
'''