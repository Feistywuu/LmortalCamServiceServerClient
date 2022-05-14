# UI and functionality for clients to grab their video device data and send it via python .socket.

import tkinter as tk
import functions
import client
import threading
import config

##TODO
# Optimizing:
# (IN VLC) plays some delayed data, then rolls back and replays data quickly, 'catching up', then is consistently slightly behind
#delayed - why?
#/is there a backlog of frames attained during loading/connecting?
    # narrow down cause
    # regardless of cause, can we drop backlog until program is fully loaded?
    # test in OBS.

# 'TCP-lite'
# create a 'connection' when sending information to host
#   - so open up a socket and start listening on a separate port
# could receive message like 'packet number XX wasn't received'
# would transmit a packet with that data
#   - How do we access this packet data on sender-side?
#   /Do we store a temporary cache of video data that we can pull the required data from?
# send requested packet once, go back to listening.

# https://stackoverflow.com/questions/64304219/how-to-read-image-from-buffer-using-opencv

'Current Workflow'
##Joining:
#/ testvideo button > checks devicenumber dropdown
#/ send video data > checks ip/port entry box > init client + send
##Hosting:
#/ Listen button > init client + start recvfrom socket
# - should listen and recvfrom be separate client functions? Maybe listen can be used for receiving data on the 'sender'
#side, whereas recvfrom for host.

' small things '
# - send video: after inputting ip/port, press enter to finalize box and go to next one.
#   / general UI workflow > selecting a button by default to a allow enter to go to next button/page.
# - testvideo: show tooltip to close it - 'Q.
# - add client name in the packet header?
# - create inherited static method in Page() class, would need to use lambda inside trace().
#       / proving annoying
# - tidy up clientlist prsentation
# - config should contain enums/ variable numbers
# - slightly laggy when 'checkDeviceList' function is called every 3 seconds, but how can we check devicelist without
#calling this function periodically?
#       / use lower level memory tracking
#       /can just use threading as a last resort.
# maybe place stringvar in main tk class and inherit in subclasses?

' Possible Issues/ replace later '
# - when calling functions.returnCameraIndexes, returns this error, could be issue:
# - watch that new client code works properly.
# - test videoDevice dropdown with multiple devices.
# - have a client-chosen username sent through packets in header, rather than idcode.
# - tidy client list, no comma when 1 client.
# - look into: IIS on windows 10, app pools


class Page(tk.Frame):

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

    def show(self):
        self.lift()


class Hosting(Page):

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.clientsString = tk.StringVar(self)
        self.clientlist = list(config.ClientDict.keys())
        self.after(10, self.updateClients)

        # create client for hosting
        def initHostClientAndListen():
            hostClient = client.Client(10003, functions.id_generator(), "127.0.0.1")
            thread = threading.Thread(target=hostClient.listen)
            thread.start()
            config.Threads.append(thread)

        clients = self.clientsString
        clients.set("Currently Connected Clients: ")

        label1 = tk.Label(self, text=functions.getIP())
        label2 = tk.Label(self, text='10003')
        label3 = tk.Label(self, textvariable=clients)
        hostButton = tk.Button(self, text='Listen for video data', command=initHostClientAndListen)

        label1.pack(side="top", fill="both", expand=True)
        label2.pack(side="top", fill="both", expand=True)
        label3.pack(side="top", fill="both", expand=True)
        hostButton.pack(side="left", fill="both", expand=True)

    # method that periodically updates from clientDict
    def updateClients(self):
        '''
        Checks if new clients are in memory, if so, update GUI and display.
        :return: void
        '''

        # if no new clients, end update
        if len(self.clientlist) == len(config.ClientDict):
            self.after(200, self.updateClients)
            return

        # if new clients, create string from them.
        clientstring = ""
        for i in range(len(list(config.ClientDict.keys()))):
            clientstring += str(list(config.ClientDict.keys())[i])[2:-1] + ', '
        textstring = "Currently Connected Clients: " + clientstring
        self.clientsString.set(textstring)                              # set tkinter variable to new clientList
        self.clientlist = list(config.ClientDict.keys())
        self.after(200, self.updateClients)


class Joining(Page):

    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.selectedDevice = tk.StringVar(self)
        self.deviceList = functions.returnCameraIndexes()
        self.after(10, self.checkDeviceList)
        self.updateNeeded = False

        # updating widgets upon text change
        def traceIP(a, b, c):
            new_text = "IP: " + ipVar.get()
            string1.set(new_text)

        def tracePORT(a, b, c):
            new_text = "Port: " + portVar.get()
            string2.set(new_text)

        # update device selection upon optionMenu selection
        def changeDevice(stringvar):
            self.selectedDevice.set(stringvar)
            config.VideoDevices = self.selectedDevice.get()

        # variables for widgets
        ipVar = tk.StringVar(self)
        portVar = tk.StringVar(self)
        string1 = tk.StringVar(self)
        string2 = tk.StringVar(self)
        string1.set("IP: ")
        string2.set("Port: ")
        ipVar.trace('w', traceIP)                                 # run my_tracer if value was changed (w = write)
        portVar.trace('w', tracePORT)                               # run my_tracer if value was changed (w = write)

        # widgets
        ipEntryBox = tk.Entry(self, textvariable=ipVar)
        portEntryBox = tk.Entry(self, textvariable=portVar)
        label1 = tk.Label(self, textvariable=string1)
        label2 = tk.Label(self, textvariable=string2)

        # dropdown box to select video device
        self.selectedDevice.set(self.deviceList[0])
        self.optionMenu = tk.OptionMenu(self, self.selectedDevice, self.deviceList, command=lambda string=self.selectedDevice: changeDevice(string))

        # test video device button
        def testVideo():
            ' Press Q to close video '
            functions.TestCamera(int(self.selectedDevice.get()))
        testButton = tk.Button(self, text="testVideo", command=testVideo)

        # send video data to ip/port button
        def transmitVideo():
            ' Will close testvideo if open, use ip and port given, error message if not given '
            try:
                thread = threading.Thread(target=client.Client.videoDataReader, args=(functions.id_generator(), int(self.selectedDevice.get()), int(portVar.get()), ipVar.get()))
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
        self.optionMenu.pack(side='top')
        testButton.pack()
        transmitButton.pack(side="left", fill="both", expand=True)

    def checkDeviceList(self):
        '''
        :return: bool
        '''
        self.after(3000, self.checkDeviceList)
        if self.deviceList == functions.returnCameraIndexes():
            return
        else:
            self.updateNeeded = True


    def updateVideoDevices(self):
        '''
        Update GUI optionmenus
        :return:
        '''

        # add new options to menu, if new video devices
        if self.deviceList != functions.returnCameraIndexes():
            menu = self.optionMenu["menu"]
            for string in self.deviceList:
                menu.add_command(label=string,
                                 command=lambda value=string:
                                 self.selectedDevice.set(value))

        self.updateNeeded = False



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


