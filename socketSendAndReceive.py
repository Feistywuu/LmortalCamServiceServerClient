# Abstraction of .socket implementation of udp video data transfer

import socket
import base64
import cv2 as cv
import imutils
import time


def socketSend(serverIP=None):
    ' Send packets via .socket, initialize needed variables '

    # initialize variables
    HOST, PORT = "192.168.1.160", 80

    BUFF_SIZE = 65536
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
    host_name = socket.gethostname()
    host_ip = '192.168.1.160'  # socket.gethostbyname(host_name)
    port = 10001

    vid = cv.VideoCapture(0)

    client_socket.connect((host_ip, port))

    fps, st, frames_to_count, cnt = (0, 0, 20, 0)
    print('test3')
    while True:

        WIDTH = 400
        while vid.isOpened():
            print('test1')
            _, frame = vid.read()
            frame = imutils.resize(frame, width=WIDTH)
            print(frame)
            encoded, buffer = cv.imencode('.jpg', frame, [cv.IMWRITE_JPEG_QUALITY, 80])
            print(buffer)
            message1 = base64.b64encode(buffer)
            print(message1)
            client_socket.sendto(message1, (serverIP, port))
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



def socketReceive():
    ' Receive packets via .socket, initialize needed variables '

    # initialize variables
    BUFF_SIZE = 65536
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    print(host_ip)
    port = 10001

    socket_address = (host_ip, port)
    server_socket.bind(socket_address)
    print('Listening at:', socket_address)

    # receive data from socket
    First = True
    while True:
        buffer, client_adress = server_socket.recvfrom(BUFF_SIZE)
        print('start')
        print(buffer)
        print(client_adress)
        buffer = bytes.decode(buffer, 'utf-8')  # is this needed? Or can i just slice it
        buffer = base64.b64decode(buffer)

        print('test')

        # initialize first time connection settings
        if First:
            # create list and append to it
            # spawn thread and work on list
            pass

        First = False

    pass