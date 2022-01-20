
''' To Do'''

''' How to transmit video over connection'''

#TCP requires data in the form of a stream of bytes.


#Currently client sends request and server handles it.
#   choose device in client, limit to 480p, - use opencv


# since gui uses a process to check for events, to be able to interact with tkinter whilst
#opencv is recording(also a while loop), need multiprocessing
#or use opencv highgui as a gui

#\\\\	Client	\\\\

# send http requests to server
#   -send in form required by server
#   receive 'connection established etc'

#create ui
# show device in UI
# dropdown box for device,quality,port,server ip

#Variables:
#Select video device, quality, port, server ip.


#\\\\	Server:	\\\\\\\\
#Variables:
#Accept

#- Create TCP server.
#   - make server
#   - receive data - how?
#       - create socket that receives data stream
#       - use https requests/ requests.post
#   - performs specified method in the request.

#- Create sockets on start-up that are in a listening state

#- create a unique socket for each client connection in a child process/thread, when they connect.

# Then how do we get to OBS? Does it


'''
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

    fps, st, frames_to_count, cnt = (0, 0, 20, 0)
    while True:
        mypacket = server_socket.recvfrom(BUFF_SIZE)      # in tuple form (buffer, (source_ip, port))
        raw = mypacket[0]
        print(raw)
        data = base64.b64decode(raw, ' /')
        npdata = np.fromstring(data, dtype=np.uint8)
        print(data)
        frame = cv.imdecode(npdata, 1)
        frame = cv.putText(frame, 'FPS: ' + str(fps), (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv.imshow("RECEIVING VIDEO", frame)
        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):
            # threadsocket.close()
            break
        if cnt == frames_to_count:
            try:
                fps = round(frames_to_count / (time.time() - st))
                st = time.time()
                cnt = 0
            except:
                pass
        cnt += 1


        #print('starting main receive loop again')
        #print(packet)
        #sortPackets(mypacket)
'''