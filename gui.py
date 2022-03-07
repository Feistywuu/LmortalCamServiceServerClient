# UI and functionality for clients to grab their video device data and send it via python .socket.

import tkinter as tk
import functions
import client
import threading
import config

'later'
#IIS on windows 10, app pools

' Possible Issues/ replace later '
# - when calling functions.returnCameraIndexes, returns this error, could be issue:
# [ WARN:0] global C:\Users\appveyor\AppData\Local\Temp\1\pip-req-build-2b5g8ysb\opencv\modules\videoio\src\cap_msmf.cpp (435) `anonymous-namespace'::SourceReaderCB::~SourceReaderCB terminating async callback
# - dummy variable none in dropdown to make it look nicer
# - sometimes requires two plays in vlc til it connects - could be issue later

'Current Workflow'
##Joining:
#/ testvideo button > checks devicenumber dropdown
#/ send video data > checks ip/port entry box > init client + send
##Hosting:
#/ Listen button > init client + start recvfrom socket
# - should listen and recvfrom be separate client functions? Maybe listen can be used for receiving data on the 'sender'
#side, whereas recvfrom for host.


class Page(tk.Frame):

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

    def show(self):
        self.lift()


class Hosting(Page):

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        label1 = tk.Label(self, text=functions.getIP())
        label2 = tk.Label(self, text='10003')

        # create client for hosting
        def initHostClientAndListen():
            hostClient = client.Client(10003, functions.id_generator(), "127.0.0.1")
            thread = threading.Thread(target=hostClient.listen)
            thread.start()
            config.Threads.append(thread)
        hostButton = tk.Button(self, text='Listen for video data', command=initHostClientAndListen)

        label1.pack(side="top", fill="both", expand=True)
        label2.pack(side="top", fill="both", expand=True)
        hostButton.pack(side="left", fill="both", expand=True)

    # TODO
    # show list of client id's


class Joining(Page):

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        # entrybox for ip and port
        ipVar = tk.StringVar()
        ipEntryBox = tk.Entry(self, textvariable=ipVar)
        portVar = tk.StringVar()
        portEntryBox = tk.Entry(self, textvariable=portVar)

        label1 = tk.Label(self, text="IP: "+str(ipVar.get()))
        label2 = tk.Label(self, text='Port: ' + str(portVar.get()))

        # dropdown box to select video device
        OPTIONS = functions.returnCameraIndexes()
        master = self
        selectedDevice = tk.StringVar(master)
        selectedDevice.set(OPTIONS[0])
        w = tk.OptionMenu(master, selectedDevice, *OPTIONS)

        # test video device button
        def testVideo():
            ' Press Q to close video '
            functions.TestCamera(int(selectedDevice.get()))
        testButton = tk.Button(self, text="testVideo", command=testVideo)

        # send video data to ip/port button
        def transmitVideo():
            ' Will close testvideo if open, use ip and port given, error message if not given '
            try:
                thread = threading.Thread(target=client.Client.videoDataReader, args=(functions.id_generator(), int(selectedDevice.get()), int(portVar.get()), ipVar.get()))
                thread.start()
                config.Threads.append(thread)
            except TypeError as e:
                print(e)
                # display tkinter error message saying: ip/port invalid
                print('ip/port invalid')

        transmitButton = tk.Button(self, text="Send Video Data", command=transmitVideo)

        ipEntryBox.pack()
        portEntryBox.pack()
        label1.pack(side="top", fill="both", expand=True)
        label2.pack(side="bottom", fill="both", expand=True)
        w.pack(side='top')
        testButton.pack()
        transmitButton.pack(side="left", fill="both", expand=True)

    # TODO
    # button to refresh the device list - runs returnCameraIndexes() again
    # - Entry for quality
    # later: 'connection: successful' message.


class Menu(Page):

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        label = tk.Label(self, text="This is the menu")
        label.pack(side="top", fill="both", expand=True)


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


