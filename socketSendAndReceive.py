# Abstraction of .socket implementation of udp video data transfer

import socket
import base64
import cv2 as cv
import imutils
import time
import threading
import numpy as np
from copy import deepcopy
import struct
import Packet as packet


# Dictionary holding {clientID;video frames} key;value pairs.
# ClientDict must be FIFO, as of 3.7 python dict is now ordered.
# CLientDict = { clientID;[frame1, ..., frameN] , ...}
ClientDict = {}
Threads = []


# order determined when they are added to threads list
#   need to add main thread to this list somehow
#   order of execute (for loop), will be defined in server, thus need to import Threads[].
#   request_handler won't be part of Threads[]
#   start

# will need to create another thread for the gui in server
# processframes needs to loop until there are no frames left to process, but if they all join before starting next jobs
#some will have stopped will others are finishing, thus they have to be independent.
# OR they don't join and wait for eachother.


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


def sortPacket(mypacket, packetheader):
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
    if clientID in ClientDict:
        ClientDict[clientID].append(frame)
        print('add to clientListKey: ' + clientID)

    if clientID not in ClientDict:
        ClientDict[clientID] = [frame]
        print('created clientlist key: ' + str(id(ClientDict[clientID])))

        # add to threads list
        x = threading.Thread(target=ProcessFrames, args=[clientID])
        Threads.append(x)
        x.start()


def ProcessFrames(clientid):
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
    while True:
        # start of process loop
        for i in range(len(ClientDict[clientid])):
            # iterating through frames

            frame = cv.putText(ClientDict[clientid][i], 'FPS: ' + str(fps), (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            previoustime.t = fpsMaintainer(10, previoustime.t)
            cv.imshow("RECEIVING VIDEO", frame)

            key = cv.waitKey(1) & 0xFF
            if key == ord('q'):
                #threadsocket.close()
                break


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
            payload = base64.b64decode(receivedPayload[0], ' /')        # conversion to bytes allows for easy conc.(?)
            assembledPayload += payload

        sortPacket(assembledPayload, header)


def socketSend(serverIP=None):
    """"
    Send packets via .socket, initialize needed variables
    """

    # initialize variables
    HOST, PORT = "192.168.1.160", 80

    BUFF_SIZE = 65516
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
    host_name = socket.gethostname()
    host_ip = '192.168.1.192'  # socket.gethostbyname(host_name)
    port = 10003

    vid = cv.VideoCapture(0)

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
            myPacket = packet.Packet(message1)

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

