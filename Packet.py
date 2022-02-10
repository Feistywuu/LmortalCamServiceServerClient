# Packet class to wrap payload and header information in

import struct


class Packet:
    """
    length = int = unsigned short
    udpTrue = bool = bool
    cookie = (int,int) = unsigned int
    """

    def __init__(self, data, identitycode, packetnumber):

        # internal values
        self.raw = data
        self.payloadPartitions = {}

        # header values
        self.length = len(data)
        self.udpTrue = 1
        self.idcode = identitycode
        self.packetnumber = packetnumber


    def partition(self, buffersize):
        """
        Takes the data payload of the packet and split into partitions specified by the buffer size if needed,
        otherwise return the payload as a string
        :return: dict or string
        """

        # provided payload is already in byteform
        n = '0'
        header_length = 15                      # short + bool + string(len=8) + int = 2 + 1 + 8 + 4

        if len(self.raw) >= buffersize:

            # get data, slice byte-string into 65316 slices
            payload = self.raw[:buffersize+1]
            remainder = self.raw[buffersize+1:]

            # add first partition to dict. of partitions
            self.payloadPartitions[n] = payload
            n = int(n)
            n += 1
            n = str(n)

            # split and add remaining payload to dictionary, iterating until there is one partitions worth left
            while len(remainder) >= buffersize:
                self.payloadPartitions[n] = remainder[:buffersize+1]
                remainder = remainder[buffersize+1:]
                n = int(n)
                n += 1
                n = str(n)

            # last partition
            if len(remainder) != 0:
                self.payloadPartitions[n] = remainder[:]

            self.packetnumber += 1
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
