# Assortment of Functions
import random
import string
import socket
import cv2 as cv
import imutils
import time
import numpy as np
import subprocess
import sys
import errno

from client import Client
from packet import Packet, PacketType
import config as config

" to work on "
#/server host and join gui stuff *current*
#/Implement threading with multiple clients.
#   / function that inits subprocess and piping for each client, use clientID and put into dict.

# rename socketReceive() > listen()

' vague to do'
# merge sortpackets with recv
# move decode/processing to subprocesses - if needed
# use multiprocessing for gui and socketrecv maybe
# get vid properties for ffmpeg before info is piped.
# issue if trouble reading empty stdin.


# gui functions
def getIP():
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    return host_ip


def returnCameraIndexes():
    # checks the first 10 indexes.
    index = 0
    arr = []
    i = 10
    while i > 0:
        cap = cv.VideoCapture(index)
        if cap.read()[0]:
            arr.append(str(index))
            cap.release()
        index += 1
        i -= 1
    arr.append('None')
    return arr


def TestCamera(device=None):
    cap = cv.VideoCapture(device)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv.CAP_PROP_FPS, 30)

    if not cap.isOpened():
        print("Trying default device")
        cap = cv.VideoCapture(0)
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

# miscellaneous Functions
def id_generator():
    """
    create client id at runtime that can be contained in packet header
    id of form: 'xxxxxxxx', where x can be lower/upper character or number 0-9
    thus of size, char = c: cccccccc
    :return: str
    """
    # string 8 characters long
    idString = ''

    for x in range(0, 8):
        deciderVar = random.randint(0, 1)
        if deciderVar == 0:
            letter = random.choice(string.ascii_letters)
            idString = idString + letter
        else:
            number = random.choice(string.digits)
            idString = idString + number

    idString = bytes(idString, 'utf-8')
    return idString


# Sorting Packets/Payload Data
def sortPacket(mypacket, clientid):
    '''
    Creates subprocesses p1, p2, for each new client with a defined pipeline with functions - ffmpeg - along the way,
    eventually piped to a rtmp server.
    '''


    # init ffmpeg process /w pipes + sorting process w/pipes
    #p = subprocess.Popen([sys.executable, 'pProcess.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    # append to dict
    #config.ClientDict[clientid].append([p1, p2])

    # write to stdin of first pipe - subproc
    print(mypacket)
    npdata = np.fromstring(mypacket, dtype=np.uint8)
    frame = cv.imdecode(npdata, 1)
    #frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    print(frame)
    #p1.stdin.write(frame.tobytes())

    print('debug4')

# XXX rename? not really our socketsend?
# more like a client video reader thing.

# My thought reading original code is we have the components: GUI + Client + Packet
# Packet - describe data
# Client - Connect/send
# GUI - Runs this/initiate



