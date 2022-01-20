# Abstraction of .socket implementation of udp video data transfer

import socket
import base64
import cv2 as cv
import imutils
import time
import threading
import numpy as np
from copy import deepcopy
import Packet as packet


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
    print('test3')
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

            # send packets
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


# Need a dictionary of client's based on their IP's to check packet against.
# of form { ip1:[frame1,....,frameN], ...., ipN:[frame1, ..., frameN]}  (ip=string)
ClientDict = {}
Threads = []
print('id of clientlist: ' + str(id(ClientDict)))


# order determined when they are added to threads list
#   need to add main thread to this list somehow
#   order of execute (for loop), will be defined in server, thus need to import Threads[].
#   request_handler won't be part of Threads[]
#   start

# will need to create another thread for the gui in server
# processframes needs to loop until there are no frames left to process, but if they all join before starting next jobs
#some will have stopped will others are finishing, thus they have to be independent.
# OR they don't join and wait for eachother.

def sortPackets(packet):
    '''
    If packet is received with a new source IP, create a list, append to it and spawn thread,
    otherwise append packet to list associated with IP.
    packet = tuple(payload, (ip,port))
    '''
    print('sortPackets: starting')
    print(ClientDict)
    payload = packet[0]
    source_ip = packet[1][0]

    # check for ip in dict
    # if ip in dict, add payload to value list
    if source_ip in ClientDict:
        ClientDict[source_ip].append(payload)
        print('add to clientListKey: ' + source_ip)

    # if not in dict, add ip:payload as key:[value]
    if source_ip not in ClientDict:
        ClientDict[source_ip] = [payload]
        print('created clientlist key: ' + str(id(ClientDict[source_ip])))
        print(ClientDict[source_ip])

        # add to threads list
        print([source_ip])
        x = threading.Thread(target=ProcessFrames, args=[source_ip])
        Threads.append(x)
        x.start()


def CacheandClearDict(key):
    '''
    Firstly, locks thread to the interpreter, to avoid any race conditions.
    When passed a key from a dictionary, make a copy() of it, then delete value in original dict, then unlock.
    :param key:
    :return: [frames]
    '''

    # lock thread to interpreter
    Lock = threading.Lock()
    Lock.acquire()

    print('CachingfromDict: Locked')  # maybe comments are overkill?
    print(key)
    print(key[0])
    print(type(key[0]))
    print(str(key[0]))
    print(ClientDict)
    print(ClientDict[key[0]])

    # copy data and cache
    frameCache = deepcopy(ClientDict[key[0]])
    print(frameCache)

    # delete data
    del ClientDict[key[0]]

    # unlock thread
    print('CachingfromDict: about to unlock')
    Lock.release()
    return frameCache


def ProcessFrames(key):
    '''
     When given a the key from a dictionary, retrieves frames thread-safely and pops them from the dict,
     then performs decoding, timing to show frames as a video
    '''
    print('very start of ProcessFrames')
    fps, st, frames_to_count, cnt = (0, 0, 20, 0)

    print('Start Processing')
    # iterate over frames in cache
    while True:
        print('value of key in while loop, before CacheandClearDict()')
        print(key)
        frameCache = CacheandClearDict([key])
        for i in range(len(frameCache)):
            data = base64.b64decode(frameCache[i], ' /')
            npdata = np.fromstring(data, dtype=np.uint8)
            frame = cv.imdecode(npdata, 1)
            frame = cv.putText(frame, 'FPS: ' + str(fps), (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv.imshow("RECEIVING VIDEO", frame)
            key = cv.waitKey(1) & 0xFF
            if key == ord('q'):
                #threadsocket.close()
                break
            if cnt == frames_to_count:
                try:
                    fps = round(frames_to_count / (time.time() - st))
                    st = time.time()
                    cnt = 0
                except:
                    pass
            cnt += 1

    # go back and delete same elements from framecache and updating framecache


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
    First = True
    while True:
        mypacket = server_socket.recvfrom(BUFF_SIZE)      # in tuple form (buffer, (source_ip, port))
        print('starting main receive loop again')
        #print(packet)
        sortPackets(mypacket)





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

