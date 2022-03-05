# UI and functionality for clients to grab their video device data and send it via python .socket.

import tkinter as tk
import cv2 as cv
import functions

# Initializing Global Variables
IdentityCode = functions.id_generator()


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


# https://stackoverflow.com/questions/14817210/using-buttons-in-tkinter-to-navigate-to-different-pages-of-the-application


class Page(tk.Frame):

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

    def show(self):
        self.lift()


class Hosting(Page):

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        label = tk.Label(self, text="This is page 1")
        label.pack(side="top", fill="both", expand=True)

    # server host stuff

    # listen button that runs recvfrom() *CURRENT*
    #   / move socketReceive into client class
    #   / call that function.
    #   / put send button in join, so can check still works, edit client class so that socketreceive can be put in.
    #       / see if client inits with remote_address = False

    # show ip and port info clients need
    # show list of client id's


class Joining(Page):

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        label = tk.Label(self, text="This is page 2")
        label.pack(side="top", fill="both", expand=True)

        # send video data via socket
        sendButton = tk.Button(self, text='Send', command=(lambda: functions.videoDataReader(IdentityCode, 0, '127.0.0.1')))
        sendButton.pack(side="left", fill="both", expand=True)
        #self.canvas.create_window(330, 50, window=self.buttonTest)

    # sending video data settings:
    # - entry/dropdown box to select video device, when entered run videoDataReader - this is our video preview.
    # - entry box/button that changes global boolean: Transmit = True
    # - Entry for quality

    # later: 'connection: successful' message.


class Menu(Page):

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        label = tk.Label(self, text="This is the menu")
        label.pack(side="top", fill="both", expand=True)

#class allows shared access to the root tk.Tk object and then our pages can all init an object with the inherited frame class,
#all tk.Frame objects created from the same root tk.Tk object.
#   - allows shared access to tk.TK() object, which is a OOP layer for GUI to build on.
#   - call GUI?

# We put frames > containers
# widgets > frames?
class GUI(tk.Frame):

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        hostingpage = Hosting(self)
        joiningpage = Joining(self)
        menupage = Menu(self)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        hostingpage.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        joiningpage.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        menupage.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        back1 = tk.Button(hostingpage, text="Back", command=menupage.show)
        back2 = tk.Button(joiningpage, text="Back", command=menupage.show)
        hostButton = tk.Button(menupage, text="Host Server", command=hostingpage.show)
        sendButton = tk.Button(menupage, text="Send to a Server", command=joiningpage.show)

        back1.pack(side="top")
        back2.pack(side="top")
        hostButton.pack(side="bottom")
        sendButton.pack(side="bottom")

        menupage.show()


if __name__ == "__main__":
    root = tk.Tk()
    main = GUI(root)
    main.pack(side="top", fill="both", expand=True)
    root.wm_geometry("400x400")
    #root.wm_geometry("1280x800")
    root.mainloop()


'''
# Main background window
        self.canvas = tk.Canvas(self.master, width=500, height=400)
        self.canvas.pack()
        self.master.title("LmortalCamsService")


        # capture video from device
        self.buttonTest = tk.Button(text='Camera', command=TestCamera)
        self.canvas.create_window(200, 100, window=self.buttonTest)
'''
