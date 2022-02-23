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
import errno

""" check data format states """
# Transformations done to data: data remains the same until the end OR if data requires partitioning.
# VideoCapture() > imutils.resize() > imencode() > b64encode()
# packetPartition/putting back together() > b64decode() > imdecode() > [ ToBytes() > stdin/bufferform ]

'Errors'
# BrokenPipeError: [Errno 32] Broken pipe
# OSError: [Errno 22] Invalid argument - sometimes this is returned
#   /Both of these errors apply to p1.stdin.write() line, checking frame integrity reveals:
#       /that the frame shows fine with cv.imshow() in isolation, thus the issue in not with the frame itself. *DONE*
#   / Are these both just messages based on closing by ending the process? Thus differing at code pos. when closed.
#       / NO, fails without closing *DONE*
#   /Is data invalid form to placed into pipe? No *DONE*
#   / It has to be related to the pipes - and how they are set up / linked together:
#       /related to not closing the p1.stdin?

#   / Look at when BrokenPipeError happens - maybe trigger since wrong argument is put in ffmpeg (not jpeg valid,
#   /which then causes the error)
#       / Usually indicates I/O errors, so receiving pipe closing the pipe whilst sending creates a buffer expecting
#       /data to be received.
#           / definitely data is in the wrong form ffmpeg, find the right form for jpeg.
#               / try jpeg > pil > ffmpeg https://stackoverflow.com/questions/47126370/opencv-write-jpeg-buffer-into-popen-object
#   / imutils image resize() shouldn't affect ffmpeg entirely? Otherwise requires packet partition concatenation.


# [rawvideo @ 0000017167043880] Packet corrupt (stream = 0, dts = 0). \\\\ probably wrong packet form

' BrokenPipeError'
# Sympton of underlying somewhere else, probably.
# maybe require stdin.close at some point?

' Packet Corrupt - *DONE*?'
# [rawvideo @ 0000020cc73a3880] Packet corrupt (stream = 0, dts = 0). returns without writing to pipe.
#   /Upon changing to jpeg ffmpeg 'images2pipe' rather than 'rawvideo' packet corrupt doesn't appear, but still
#   /returns BrokenPipeError.

# Problem with popen being initialized with an empty stdin?

#       / data could be corrupted during np.fromstring() or imdecode() with wrong args
#               /removing imencode() on both sides
#                       / testing packet conc. functions now - doesn't work - *fix later*
#                           /changing packet.elgnth from short > int; 15 > 17 byte header size
#                           /need to split apart payload before sending
#                       / testing imencode() arguments to simply compress and keep as rawvideo
#                       / OR changing ffmpeg arguments to accept , imencode(), .jpg video data. # CURRENT, imencode() on.
#                           / do we use imdecode()?
#                           / or we change arguments in ffmpeg without imdecode()
#                               / does imencode() change rgb etc format
#                               / is colour change required after imdecode()
#                                   /Probably not since ffmpeg returns invalid argument when bgr > rgb change *DONE*

' vague to do'
# merge sortpackets with recv
# move decode/processing to subprocesses - if needed
# use multiprocessing for gui and socketrecv maybe
# when do we close pipes?
# get vid properties for ffmpeg before info is piped.
# issue if trouble reading empty stdin.


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
               '-f', 'image2pipe',                            # global/input options
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
    print(p1)
    print('debug2')
    p2 = ffmpegPipeInit(p1)
    print('debug3')

    # append to dict
    config.ClientDict[clientid].append([p1, p2])

    # write to stdin of first pipe - subproc
    print(mypacket)
    npdata = np.fromstring(mypacket, dtype=np.uint8)
    frame = cv.imdecode(npdata, 1)
    #frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    print(frame)
    try:
        p1.stdin.write(frame.tobytes())
    except IOError as e:
        print(e)
        if e.errno == errno.EPIPE:
            print('it is epipe')
            print(e)
            exit()
        exit()
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
            print('Received Payload, header length then payload length:')
            print(header[0])
            print(len(receivedPayload[0]))

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

