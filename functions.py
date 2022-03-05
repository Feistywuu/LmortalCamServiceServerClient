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
from packet import Packet2, PacketType
import config as config

" to work on "
#/ understanding it all:
#   /Why is the chunk size 32768: (2^16)/2 = 2^15?, is this a limit by something, since if it was, the sendto function sends
#   a dblock of 32768 + header at same time, thus would go over limit?
#   / db is of size 32789, so go over the chunk size, why is it defined at 2^15?
#   /header is first 21 bytes of chunks
#/We have server GUI, server client, consumer-client, consumer-GUI, packet functions#
#   / move socketRecv to client *CURRENT*
#   / split socket socketSend into socketInit and Send(), same with socketReceive().
#       /create state boolean, which send button alters, which then allows send() in videoDataReader()
#               / Config.transmitData
#       /funnel ip and port data into
#       /init when clientGUI runs, send when button is pressed.
#       / when devicenumber can be specified, has to stop socketINIT() and run again with new device.
#           / create ChooseDevice() button which init the videoReading()
#   / put GUI together, then def functions for client/server
#       / initial gui page: join? / host?
#           / then subsequent respective pages.
#       /will require threading* so that client send() doesn't block.
#/Implement threading with multiple clients.
#   / function that inits subprocess and piping for each client, use clientID and put into dict.
#/could try making clientgui in front-end language

' vague to do'
# merge sortpackets with recv
# move decode/processing to subprocesses - if needed
# use multiprocessing for gui and socketrecv maybe
# get vid properties for ffmpeg before info is piped.
# issue if trouble reading empty stdin.


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


G = lambda: ...
G.rtmp_url = "rtmp://127.0.0.1:1935/live/app"
G.fps = 30
G.width = 640
G.height = 480


#'-f', 'image2pipe',
# '-r', str(fps),
# '-vcodec', 'rawvideo',

# '-s', "{}x{}".format(G.width, G.height),
# '-pix_fmt', 'bgr24',

G.command = ['ffmpeg',
            '-y',
            '-re',
            '-c:v', 'mjpeg',
            '-r', str(G.fps),
            '-i', '-',                              # input url from pipe
            '-pix_fmt', 'yuv420p',                  # output file options
            '-preset', 'ultrafast',
            '-c:v', 'libx264',
            '-bufsize', '64M',
            '-f', 'flv',
            '-listen', '1',
             G.rtmp_url]


# Sorting Packets/Payload Data
def sortPacket(mypacket, clientid):
    '''
    Creates subprocesses p1, p2, for each new client with a defined pipeline with functions - ffmpeg - along the way,
    eventually piped to a rtmp server.
    '''


    # init ffmpeg process /w pipes + sorting process w/pipes
    p = subprocess.Popen([sys.executable, 'Process.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

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


# Sending/building packets and Receiving packets
def socketReceive():
    ' Receive packets via .socket, initialize needed variables '

    # create subprocess to run command and open pipe
    G.proc = subprocess.Popen(G.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    # initialize variables
    BUFF_SIZE = 65536
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    #host_name = socket.gethostname()
    #host_ip = socket.gethostbyname(host_name)

    port = 10003

    socket_address = ('', port)
    server_socket.bind(socket_address)
    print('Listening at:', socket_address)

    expect_frag = 1
    assembledPayload = b''

    # mclient.listen() # XXX

    while True:
        data, client_addr = server_socket.recvfrom(BUFF_SIZE)
        hdr = Packet2.parse(data)

        # XXX receive data from socket
        # Move recv to Client2 class - Rename Client2 to something fitting
        #
        # result, buffer = mclient.recv()
        # if result:
        #    G.proc.stdin.write(buffer)

        # NOTE: assemble payload
        #   - We can get packets in wrong order
        #   - Packets can disappear


        #print("Header - " + "Type: " + str(hdr.ptype) + " Length: " + str(hdr.payload_length) +
        #      " Id: " + str(hdr.idcode) + " Pnr: " + str(hdr.packetnumber) + " Fragment: " + str(hdr.fragment) + " Got: " + str(len(data)) + " Data: " + str(hdr.data[0:5]))

        ## Start of new frame
        if hdr.ptype == PacketType.Frame:
            assembledPayload = b''
            expect_frag = 1

            # Full frame
            if len(hdr.data) == hdr.payload_length:
                G.proc.stdin.write(hdr.data)
            else:
                assembledPayload += hdr.data

        # More data
        if hdr.ptype == PacketType.Data:
            if expect_frag == hdr.fragment:
                expect_frag += 1
                assembledPayload += hdr.data
            else:
                # We dropped something, just give up this frame
                assembledPayload = b''
                expect_frag = 999

            ## XXX Instead of dropping the full frame we could write zeroes/take img data from last frame?
            #else:
            #    ## Missing data block, just write some zeroes
            #    expect_frag += 1
            #    assembledPayload += b'\x00' * len(hdr.data)

            #    if expect_frag == hdr.fragment:
            #        expect_frag += 1
            #        assembledPayload += hdr.data
            #    else:
            #        # more missing..
            #        print("more missing")

        if hdr.ptype == PacketType.DataEnd:
            if expect_frag == hdr.fragment:
                assembledPayload += hdr.data
                G.proc.stdin.write(assembledPayload)

                assembledPayload = b''
                expect_frag = 1


# XXX rename? not really our socketsend?
# more like a client video reader thing.

# My thought reading original code is we have the components: GUI + Client + Packet
# Packet - describe data
# Client - Connect/send
# GUI - Runs this/initiate

def videoDataReader(identitycode, devicenum, serverip=None):
    """
    Send packets via .socket, initialize needed variables
    Connects to socket, retrieves video data from computer, processes and encodes it.
    Create packet + header class instance using the data
    """

    mclient = Client(10003, identitycode, "127.0.0.1")
    vid = cv.VideoCapture(devicenum)

    # XXX send header info?
    print(vid.get(cv.CAP_PROP_FPS))
    print(vid.get(cv.CAP_PROP_FRAME_WIDTH))
    print(vid.get(cv.CAP_PROP_FRAME_HEIGHT))

    fps, st, frames_to_count, cnt = (0, 0, 20, 0)
    while True:
        while vid.isOpened():
            # get video frames, process
            gotFrame, frame = vid.read()

            if gotFrame:
                frame = imutils.resize(frame, width=G.width, height=G.height)
                encoded, buffer = cv.imencode('.JPEG', frame, [cv.IMWRITE_JPEG_QUALITY, 80])

                if encoded and config.transmitData:
                    mclient.send(buffer.tobytes())
            else:
                break # VideoCapture probably closed

            frame = cv.putText(frame, 'FPS: ' + str(fps), (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255),
                               2)
            cv.imshow('TRANSMITTING VIDEO', frame)
            key = cv.waitKey(1) & 0xFF
            if key == ord('q'):
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

