# Assortment of Functions
import os
import random
import string
import socket
import base64
import cv2 as cv
import imutils
import time
import threading
import numpy as np
import struct
import Packet as packet
import ffmpeg
import subprocess
import sys
import config

# merge sortpackets with recv
# move decode/processing to ffmpeg side - if needed
# use multiprocessing for gui and socketrecv maybe
# when do we close pipes?
# get vid properties for ffmpeg before info is piped.
# issue if trouble reading empty stdin.

""" check data format states """

# missing:
#npdata = np.fromstring(payload, dtype=np.uint8)
#frame = cv.imdecode(npdata, 1)
#   - does this matter?

'Errors'
# OSError: [Errno 22] Invalid argument
# [rawvideo @ 0000017167043880] Packet corrupt (stream = 0, dts = 0). \\\\ probably wrong packet form

# - Works When:
#/ VideoCapture() > ToBytes() > ffmpeg()

# - Currently:
# VideoCapture() > imutils.resize() > imencode() > b64encode()
# packetPartition/putting back together() > b64decode() > imdecode() > [ ToBytes() > stdin/bufferform ]

# NEED TO READ io.TEXTBUFFER AT START OF FFMPEG
# ffmpeg function will receive io.textwrapper, need to decode within that function?
#   /might be okay because that is what happens already - how does ffmpeg read stdin data?

' Current'
# compare base64 on client and server side
# see how it differs from what goes into debug.

""" Options """
# make python script that takes stdin, then runs command line ffmpeg, so many another subprocess?
#   /still requires information to be passed to the stdin, thus buffered.

# what forms does ffmpeg receive, maybe there's one that accepts bufferstream?

# Look at debug.py and see form when it works and compare to model.

# packet corrupt, need function that can check frame data isolated.

# maybe imutils changes to np array form which is why it's needed


# pipe and processing functions
def ffmpegPipeInit(subproc, vidproperties=None):
    """
    Receives data from a previous pipe, with subproc as the argument.
    Receive raw video data from opencv functions
    Define ffmpeg command with correct parameters
    Use subprocess module to run command inside python and open a pipe where we can write our frame data
    Write to the pipe
    Pipe destination contains in ffmpeg command parameters?
    :return: subprocess
    """
    rtmp_url = "rtmp://127.0.0.1:1935/live/app"

    # gather video information for ffmpeg
    fps = 10
    width = 400
    height = 300

    command = ['ffmpeg',
               '-y',
               '-f', 'rawvideo',                            # global/input options
               '-vcodec', 'rawvideo',
               '-pix_fmt', 'bgr24',
               '-s', "{}x{}".format(width, height),
               '-r', str(fps),                              # force fps to stated value
               '-i', '-',                                   # input url from pipe
               '-pix_fmt', 'yuv420p',                       # output file options
               '-preset', 'ultrafast',
               '-c:v', 'libx264',
               '-f', 'flv',
               '-listen', '1',
               rtmp_url]

    # create subprocess to run command and open pipe
    p = subprocess.Popen(command, stdin=subproc.stdout)

    return p


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

    print('debug1')

    # init ffmpeg process /w pipes + sorting process w/pipes
    p1 = subprocess.Popen([sys.executable, 'Process.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    print('debug2')
    p2 = ffmpegPipeInit(p1)
    print('debug3')

    # append to dict
    config.ClientDict[clientid].append([p1, p2])

    # write to stdin of first pipe - subproc
    print(mypacket)
    npdata = np.fromstring(mypacket, dtype=np.uint8)
    frame = cv.imdecode(npdata, 1)
    print(frame)
    p1.stdin.write(frame.tobytes())
    print('debug4')


# Sending/building packets and Receiving packets
def socketReceive():
    ' Receive packets via .socket, initialize needed variables '

    # initialize variables
    BUFF_SIZE = 65536
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    print(host_ip)
    port = 10003

    socket_address = (host_ip, port)
    server_socket.bind(socket_address)
    print('Listening at:', socket_address)

    # receive data from socket
    while True:

        # assuming recvfrom is FIFO
        # receive first header, unpack, get length of payload
        payloadLength = 0
        assembledPayload = bytes('', 'utf-8')

        incomingPacket = server_socket.recvfrom(BUFF_SIZE)      # in tuple form (buffer, (source_ip, port))
        header = struct.unpack('!h?8sI', incomingPacket[0])
        print('Received Header')

        while header[0] != payloadLength:

            receivedPayload = server_socket.recvfrom(BUFF_SIZE)
            print('Received Payload')

            # combine current payload with last payload and loop if payload isn't length specified by header
            payloadLength += len(receivedPayload[0])
            print(receivedPayload[0])
            payload = base64.b64decode(receivedPayload[0], ' /')        # conversion to bytes allows for easy conc.(?)
            assembledPayload += payload


        # check if new client, if so create subprocesses and pipes
        clientID = header[2].decode('utf-8')
        if clientID not in config.ClientDict:

            # init both subprocess and write to pipe.stdin
            sortPacket(assembledPayload, clientID)

        print('testing recvloop')


def socketSend(identitycode, serverip=None):
    """
    Send packets via .socket, initialize needed variables
    Connects to socket, retrieves video data from computer, processes and encodes it.
    Create packet + header class instance using the data
    """

    # initialize variables
    HOST, PORT = "192.168.1.160", 80
    packetnumber = 0

    BUFF_SIZE = 65516
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
    host_name = socket.gethostname()
    host_ip = '192.168.1.192'  # socket.gethostbyname(host_name)
    port = 10003

    vid = cv.VideoCapture(0)

    print(vid.get(cv.CAP_PROP_FPS))
    print(vid.get(cv.CAP_PROP_FRAME_WIDTH))
    print(vid.get(cv.CAP_PROP_FRAME_HEIGHT))

    client_socket.connect((host_ip, port))

    fps, st, frames_to_count, cnt = (0, 0, 20, 0)
    while True:

        WIDTH = 400
        while vid.isOpened():
            # get video frames, process
            _, frame = vid.read()
            frame = imutils.resize(frame, width=WIDTH)
            encoded, buffer = cv.imencode('.jpg', frame, [cv.IMWRITE_JPEG_QUALITY, 80])
            message1 = base64.b64encode(buffer)
            print(message1)

            # create packet
            myPacket = packet.Packet(message1, identitycode, packetnumber)

            # send header, then payload
            myPacket.send(BUFF_SIZE, client_socket, serverip, port, header=True)
            myPacket.send(BUFF_SIZE, client_socket, serverip, port)

            frame = cv.putText(frame, 'FPS: ' + str(fps), (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255),
                               2)
            print(frame)
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
            packetnumber += 1


# Global Variable issue
'''
https://towardsdatascience.com/unraveling-pythons-threading-mysteries-e79e001ab4c
# - How to be sure we are referencing the clientList[key] we had at function call, and not using an updated version,
#mid-way through function?
#either use lock system, or creates a temporary cache dict - local value in handle function - and then update and
#compare with global dict when retrieving it
#/Lock system would be quicker than having the iterate through a cache.

# Due to how the GIL works: “In order to support multi-threaded Python programs, the interpreter regularly releases 
and reacquires the lock — by default, every ten bytecode instructions” thus, unless threads are of unequal length, 
doing the same task, splitting bytewise ends badly.
Thus locks are needed.
'''

