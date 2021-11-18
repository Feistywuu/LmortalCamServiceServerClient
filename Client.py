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
import socketSendAndReceive
import scapySendAndReceive


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


class GUI:

    def __init__(self, master):

        self.master = master

        # Main background window
        self.canvas = tk.Canvas(self.master, width=500, height=400)
        self.canvas.pack()
        self.master.title("LmortalCamsService")

        # send video data via socket
        self.buttonTest = tk.Button(text='SendRequest', command=(lambda: scapySendAndReceive.scapySend('192.168.1.160', 10003)))
        #self.buttonTest = tk.Button(text='SendRequest', command=(lambda: socketSendAndReceive.socketSend('192.168.1.160')))
        self.canvas.create_window(330, 50, window=self.buttonTest)
        # command=(lambda: socketSendAndReceive.socketSend('192.168.1.160')))

        # capture video from device
        self.buttonTest = tk.Button(text='Camera', command=TestCamera)
        self.canvas.create_window(200, 100, window=self.buttonTest)


master = tk.Tk()

gui = GUI(master)
master.mainloop()
