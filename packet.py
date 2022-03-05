import struct
from enum import IntEnum


class PacketType(IntEnum):
    NIL = 0
    Frame = 1
    Data = 2
    DataEnd = 3


PACKET_STRUCT = '!Ihh?8sI'
HEADER_SIZE = struct.calcsize(PACKET_STRUCT)


class Packet2:
    def __init__(self, client, data):
        if client:
            self.fragment = 0
            self.packetnumber = client.packetnumber
            self.idcode = client.idcode
        self.data = data
        if data:
            self.payload_length = len(data)
        else:
            self.payload_length = 0

        self.udpTrue = 1

    @staticmethod
    def parse(data):
        # TODO validate header, or add a def validate()
        packet = Packet2(None, None)
        packet.payload_length, packet.fragment, packet.ptype, packet.udpTrue, packet.idcode, packet.packetnumber = struct.unpack(PACKET_STRUCT, data[:HEADER_SIZE])
        packet.data = data[HEADER_SIZE:]

        return packet

    #def recv
    # header = struct.unpack('!h?8sI', incomingPacket[0])

    #def length(self):
    #    return self.payload_length + self.HEADER_SIZE

    # def to_string()
    #

    def tobytes(self, offset, max_bytes):
        if offset == 0:
            return self.header_tobytes(PacketType.Frame) + self.data[:max_bytes]
        elif self.payload_length < offset + max_bytes:
            return self.header_tobytes(PacketType.DataEnd) + self.data[offset:offset + max_bytes]
        else:
            return self.header_tobytes(PacketType.Data) + self.data[offset:offset + max_bytes]

    # Create byte header
    def header_tobytes(self, ptype = PacketType.NIL):
        return struct.pack(PACKET_STRUCT, self.payload_length, self.fragment, int(ptype), self.udpTrue, self.idcode, self.packetnumber)