
import random
import string
import struct
import socket
import base64

''' to watch for '''
# beware the scope of n
# socket.sendto in packet send()


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


IdentityCode = id_generator()
PacketNumber = 0                            # tracker variable, which goes up every time a packet is made
# BUFF_SIZE = 65516                 actual BUFF_SIZE = 65536, but 20 bytes to make space for socket header


class Packet:
    """
    length = int = unsigned short
    udpTrue = bool = bool
    cookie = (int,int) = unsigned int
    """

    def __init__(self, data):
        global PacketNumber

        # internal values
        self.raw = data
        self.payloadPartitions = {}

        # header values
        self.length = len(data)
        self.udpTrue = 1
        self.idcode = IdentityCode
        self.packetnumber = PacketNumber


    def partition(self, buffersize):
        """
        Takes the data payload of the packet and split into partitions specified by the buffer size if needed,
        otherwise return the payload as a string
        :return: dict or string
        """
        global PacketNumber

        # provided payload is already in byteform
        n = '0'
        header_length = 15                      # short + bool + string(len=8) + int = 2 + 1 + 8 + 4

        if len(self.raw) >= buffersize:

            # get data, slice byte-string into 65316 slices and make room for the header
            payload = self.raw[header_length:buffersize-header_length]
            remainder = self.raw[buffersize-header_length:]

            # add first partition to dict. of partitions
            self.payloadPartitions[n] = payload
            n = int(n)
            n += 1
            n = str(n)

            # split and add remaining payload to dictionary, iterating until there is one partitions worth left
            while len(remainder) >= buffersize:
                self.payloadPartitions[n] = remainder[:buffersize-header_length]
                remainder = remainder[buffersize-header_length:]
                n = int(n)
                n += 1
                n = str(n)

            # last partition
            if len(remainder) != 0:
                self.payloadPartitions[n] = remainder[:]

            PacketNumber += 1
            self.raw = self.payloadPartitions

            return self.raw

        else:

            return self.raw


    def send(self, buffersize, clientsocket, serverip, port, header=False):
        """
        Take a header or data payload and split into partitions if needed for buffer size,
        if passing header, as argument, pack before sending;
        then send them via socket;
        Otherwise, the payload is split over partitions, send them
        iteratively in order.
        Takes buffer_size as an argument.
        :return: str or dict
        """
        # determine whether header or payload
        if header:

            byteform = struct.pack('!h?8sI', self.length, self.udpTrue, self.idcode, self.packetnumber)
            test = struct.unpack('!h?8sI', byteform)

        # split raw data if too big for buffer
        else:
            byteform = self.partition(buffersize)

        # determine whether raw is in string or dict form, then send
        try:
            for value in byteform.values():
                clientsocket.sendto(value, (serverip, port))
        except:
            clientsocket.sendto(byteform, (serverip, port))


        return byteform



'''
        # create struct of header
        class Header:
            def __init__(self, dataa, idcode, packetnumber):
                self.length = len(dataa)
                self.udpTrue = True
                self.idcode = idcode
                self.packetnumber = packetnumber

        self.header = Header(data, self.id, PacketNumber)

'''

# Define Packet class
    # attributes will be the contents of the packet header:
        # header( value/length of payload, packet type, cookie)
            # value = buf_size = 65536,thus unsigned short is fine
                # **be aware this isn't 1 memory too big**
                # this require the header to be sent separately, prior to the payload, or else they will be memory
                #overflow
            # packet type = bool (udp, or not udp)
            # cookie = unsigned int, we want a storage of 2^32, since at 30 fps, we will reach 2^16 in 30 minutes.
        # then we want to create the packet itself, with the payload, this will determine information in the
        #header
        #if payload is bigger than buf_size, then it must be split into different packets

        # then we will pack this into a string/byte format, using .pack()
    # payload should be callable by packet.raw()
    # define a send function, which can send the header and/or payload