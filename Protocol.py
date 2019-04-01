from Torrent import Torrent
import struct
from bitstring import BitArray

class Protocol:
    def __init__(self):
        self.torrent = Torrent()   

    def getIndexOcurrence(self, pieces, buf):
        try: 
            return buf[pieces]
        except: 
            return False

    def create_msg_handshake(self):
        hash1 = self.torrent.getInfoHash()
        peerID= self.torrent.getPeerId()
        pstrlen = bytes([19])
        pstr = b'BitTorrent protocol'
        reserved = (bytes([0]) * 8)
        return pstrlen + pstr + reserved + hash1 + bytearray(peerID, 'utf-8')

    def decode_msg_handshake(self, msg):
        if len(msg) < 68:
            print("------------ Wrong Handshake: message is smaller.")
            return False;

        info_hash = self.torrent.getInfoHash()
        pstr_recd = msg[1 : 20]
        reserved_recd = struct.unpack('>8B', msg[20 : 28])
        info_hash_recd = msg[28 : 48]

        if(info_hash_recd != info_hash):
            print("---------- Wrong Handshake: info hash is not the same")
            return False;
        return True;

    def create_msg_bitfield(self, buf):
        bitField = []
        for piece in range(self.torrent.getTotalPieces()):
            if (self.getIndexOcurrence(buf, piece)):
                bitField.insert(piece, 1)
            else: bitField.insert(piece, 0)

        msgBytes = BitArray(bitField)
        msgLength = 1 + len(msgBytes.tobytes())
        return struct.pack(">IB{}s".format(len(msgBytes.tobytes())), msgLength, 5, msgBytes.tobytes())
            

    def decode_msg_bitfield(self, msg):
        pieceArray = []
        i = 0
        bitArray = BitArray(msg)
        for x in range(len(bitArray)):
            if bitArray[x] == True:
                pieceArray.insert(x, True)
            else:
                pieceArray.insert(x, False)
        
        return pieceArray

    def create_msg_interested(self):
        return struct.pack("!Ib", 1, 2)

    def decode_msg_interested(self, msg):
        return self.create_msg_unchoke();

    def create_msg_request(self, piece_index, piece_length, offset):
        print(piece_length)
        return struct.pack('>IbIII',13,6,piece_index,offset,piece_length)

    def create_msg_unchoke(self):
        return struct.pack("!Ib", 1, 1)

    def create_msg_piece(self, piece_index, offset):
        data = self.torrent.readFromFile(piece_index)
        return struct.pack('>IbIII', 13+len(data), 7, piece_index, offset, data)

    def generateRequestPayload(self, index, offset, length):
        requestId = bytes([6])
        index = index.to_bytes(4, 'big')
        offset = offset.to_bytes(4, 'big')
        length = length.to_bytes(4, 'big')
        return bytes([0, 0, 0, 13]) + requestId + index + offset + length

    

    