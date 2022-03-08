
import socket
import subprocess
import cv2 as cv
import imutils, config, time
from packet import Packet, PacketType

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


# moving to client, we still create id for host client
class Client:
    def __init__(self, port, idcode, remote_addr=None):
        self.port = port
        self.idcode = idcode
        self.remote_addr = remote_addr
        self.socket_addr = (remote_addr, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.packetnumber = 0
        self.port = port

    # Sending/building packets and Receiving packets
    def listen(self):
        ' Receive packets via .socket, initialize needed variables '

        # create subprocess to run command and open pipe
        #G.proc = subprocess.Popen(G.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        # initialize variables
        BUFF_SIZE = 65536
        server_socket = self.sock

        port = self.port

        socket_address = ('', port)
        server_socket.bind(socket_address)
        print('Listening at:', socket_address)

        expect_frag = 1
        assembledPayload = b''

        # mclient.listen() # XXX

        while True:
            data, client_addr = server_socket.recvfrom(BUFF_SIZE)
            hdr = Packet.parse(data)
            ffmpegproc = hdr.validate()

            # XXX receive data from socket
            # Move recv to Client2 class - Rename Client2 to something fitting
            #
            # result, buffer = mclient.recv()
            # if result:
            #    G.proc.stdin.write(buffer)

            # NOTE: assemble payload
            #   - We can get packets in wrong order
            #   - Packets can disappear

            # print("Header - " + "Type: " + str(hdr.ptype) + " Length: " + str(hdr.payload_length) +
            #      " Id: " + str(hdr.idcode) + " Pnr: " + str(hdr.packetnumber) + " Fragment: " + str(hdr.fragment) + " Got: " + str(len(data)) + " Data: " + str(hdr.data[0:5]))

            ## Start of new frame
            if hdr.ptype == PacketType.Frame:
                assembledPayload = b''
                expect_frag = 1

                # Full frame
                if len(hdr.data) == hdr.payload_length:
                    ffmpegproc.stdin.write(hdr.data)
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
                # else:
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
                    ffmpegproc.stdin.write(assembledPayload)

                    assembledPayload = b''
                    expect_frag = 1

    def send(self, buffer):
        packet = Packet(self, buffer)
        self.packetnumber += 1

        offset = 0
        chunk_size = 32768

        while True:
            dblock = packet.tobytes(offset, chunk_size)
            packet.fragment += 1

            if packet.payload_length > offset + chunk_size:
                #print("Sent1: " + str(packet.idcode) + " Nr: " + str(packet.packetnumber) + " Length: " + str(packet.payload_length) + " Fragment: " + str(packet.fragment))
                self.sock.sendto(dblock, self.socket_addr)
                offset += chunk_size
            else:
                #print("Sent3: " + str(packet.idcode) + " Nr: " + str(packet.packetnumber) + " Length: " + str(packet.payload_length) + " Fragment: " + str(packet.fragment))
                self.sock.sendto(dblock, self.socket_addr)
                break

    @staticmethod
    def videoDataReader(identitycode, devicenum, port, serverip=None):
        """
        Send packets via .socket, initialize needed variables
        Connects to socket, retrieves video data from computer, processes and encodes it.
        Create packet + header class instance using the data
        """

        mclient = Client(port, identitycode, "127.0.0.1")
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
                    break  # VideoCapture probably closed

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


''' matte's receive thoughts '''


def recv(self):
    #packet = Packet2()

    #data, client_addr = server_socket.recvfrom(BUFF_SIZE)
    #hdr = Packet2.parse_header(data)
    # packet.parse_header(data)

    # header = struct.unpack('!I?8sI', data)

    # XXX move to class Packet
    #print("Header - Length: " + str(hdr.payload_length) + " Id: " + str(hdr.idcode) + " Pnr: " + str(hdr.packetnumber) + " Got: " + str(len(data)))


    #payloadLength = len(data)
    return  #packet

