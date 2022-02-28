# UI and functionality for clients to grab their video device data and send it via python .socket.

import tkinter as tk
import cv2 as cv
import Functions

# Initializing Global Variables
IdentityCode = Functions.id_generator()
# BUFF_SIZE = 65516                 actual BUFF_SIZE = 65536, but 20 bytes to make space for socket header



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

# select video device dropdown box


class GUI:

    def __init__(self, master):

        self.master = master

        # Main background window
        self.canvas = tk.Canvas(self.master, width=500, height=400)
        self.canvas.pack()
        self.master.title("LmortalCamsService")

        # send video data via socket
        self.buttonTest = tk.Button(text='Send', command=(lambda: Functions.socketSend(IdentityCode, '127.0.0.1')))
        self.canvas.create_window(330, 50, window=self.buttonTest)

        # capture video from device
        self.buttonTest = tk.Button(text='Camera', command=TestCamera)
        self.canvas.create_window(200, 100, window=self.buttonTest)



master = tk.Tk()

gui = GUI(master)
master.mainloop()
