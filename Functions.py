# Assortment of Functions

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


# pushing frame data to rtmp socket
def ffmpegPipe(framedata):
    """
    Receive raw video data from opencv functions
    Define ffmpeg command with correct parameters
    Use subprocess module to run command inside python and open a pipe where we can write our frame data
    Write to the pipe
    Pipe destination contains in ffmpeg command parameters?
    :return: None
    """
    rtmp_url = "rtmp://127.0.0.1:1935/live/app"

    # gather video information for ffmpeg
    fps = 10            # or 30
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
    p = subprocess.Popen(command, stdin=subprocess.PIPE)

    for frame in framedata:
        p.stdin.write(framedata)




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


def fpsMaintainer(targetfps, previoustime):
    """
    Function to sleep thread according to desired fps.
    Starts recording time spent from first function call, when returning to function call again, sleep() thread
    if amount of time required to set a desired fps is needed.
    :return: time at specific point in function = int
    """
    print('FPS Check')

    # start recording time, with time()
    currentTime = time.time()

    # check value of 1/fps and compare value to time passed since last function call
    elapsedTime = currentTime - previoustime
    desiredSleep = 1 / targetfps
    print(elapsedTime)

    try:
        time.sleep(desiredSleep - elapsedTime)
        print(time.sleep(desiredSleep - elapsedTime))
    except ValueError:
        print('No sleep')

    return currentTime


# Sorting Packets/Payload Data
def sortPacket(mypacket, packetheader, clientdictionary, joblist):
    '''
    All appends to dictionary will be to the end of the value list, ensures processing is FIFO.
    Takes a packet and packet header as an argument.
    Processes the payload into easily displayable frame; appends packet to dictionary as a {client;id}.
    Checks packet header for client id, if new client, create thread to process frames, append to dictionary;
    if current client, just add to dictionary.
    '''
    print('Sorting Packets')

    payload = mypacket
    npdata = np.fromstring(payload, dtype=np.uint8)
    frame = cv.imdecode(npdata, 1)

    # converting from bytes to string
    clientID = packetheader[2].decode('utf-8')

    # check for id in dict
    if clientID in clientdictionary:
        clientdictionary.pop(clientID)
        clientdictionary[clientID] = [frame]
        joblist.append(ProcessFrames(clientID, clientdictionary))
        print('add to clientListKey: ' + clientID)

    if clientID not in clientdictionary:
        clientdictionary[clientID] = [frame]
        print('created clientlist key: ' + clientID)

        # add to threads list
        joblist.append(ProcessFrames(clientID, clientdictionary))


def ProcessFrames(clientid, clientdictionary):
    '''
    Will pop the frame from the bottom of the stack.
    When given a the key from a dictionary, retrieves frames thread-safely and pops them from the dict,
    then performs decoding, timing to show frames as a video
    '''
    previoustime = threading.local()
    previoustime.t = 0.01
    fps, st, frames_to_count, cnt = (0, 0, 20, 0)

    print('Start Processing')
    # iterate over frames in dictionary key
    for i in range(len(clientdictionary[clientid])):
        # iterating through frames

        frame = cv.putText(clientdictionary[clientid][i], 'FPS: ' + str(fps), (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        previoustime.t = fpsMaintainer(10, previoustime.t)
        cv.imshow("RECEIVING VIDEO", frame)

        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):
            #threadsocket.close()
            break


# Sending/building packets and Receiving packets
def socketReceive(clientdictionary, joblist):
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
            payload = base64.b64decode(receivedPayload[0], ' /')        # conversion to bytes allows for easy conc.(?)
            assembledPayload += payload

        npdata = np.fromstring(assembledPayload, dtype=np.uint8)
        frame = cv.imdecode(npdata, 1)
        ffmpegPipe(frame)
        #sortPacket(assembledPayload, header, clientdictionary, joblist)


def socketSend(identitycode, serverIP=None):
    """"
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
            myPacket.send(BUFF_SIZE, client_socket, serverIP, port, header=True)
            myPacket.send(BUFF_SIZE, client_socket, serverIP, port)

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

