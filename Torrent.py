import bencoder
import hashlib
import os
import math

class Torrent():
    def __init__(self): 
        self.metainfo = self.decodeTorrentFile()
        self.num_pieces= self.getTotalPieces()
        self.piece_length = self.getPieceLength()
        self.tracker_list = self.getTrackerList()
        self.info_hash= self.getInfoHash()
        self.peer_id = self.getPeerId()
        self.left = self.getLeft()

    def decodeTorrentFile(self):
        f = open("testtorrent.torrent", "rb")
        metainfo = bencoder.decode(f.read())
        return metainfo

    def getFileLength(self):
        pieces = self.metainfo[b'info'][b'length']
        return int(pieces)

    def getTotalPieces(self):
        pieces = self.metainfo[b'info'][b'pieces']
        num_pieces= int(len(pieces)/20)
        return num_pieces

    def getPieceLength(self): 
        piece_length = self.metainfo[b'info'][b'piece length']
        return int(piece_length)

    def getTorrentName(self):
        name = self.metainfo[b'info'][b'name']
        return name;

    def getTrackerList(self):
        announce_list= self.metainfo[b'announce-list']
        return announce_list

    def getInfoHash(self):
        info = self.metainfo[b'info']
        info_hash= hashlib.sha1(bencoder.encode(info)).digest()
        return info_hash

    def getPeerId(self):
        peer_id= '-AZ2060-611784544578'
        return peer_id
    
    def getLeft(self): 
        left = self.metainfo[b'info'][b'length']
        return left
    
    def getOffset(self, index):
        # print(self.getTotalPieces())
        numberOffset= int(math.ceil(self.getPieceLength()/2**14))
        blockSize = int(self.getPieceLength()/numberOffset)

        # intPeiceLengt = self.getPieceLength()
        print(numberOffset, "heey!")

        listOffets = []
        for index, pieces in enumerate(range(numberOffset)):
            listOffets.append(index * blockSize)
            # listOffets.append(2**14)

        return listOffets

    def createFile(self):
        file_name = self.getTorrentName()
        file_size = self.getFileLength()

        with open(file_name, "wb") as f:
            f.write(os.urandom(file_size))
            f.close()

    def readFromFile(self, pieceId):
        num_pieces=self.getTotalPieces()
        with open(self.getTorrentName(), "rb") as f:
            for piece in range(num_pieces):
                data = (f.read(self.getPieceLength()))
            
                if(piece == pieceId):
                    print(data)
                    break
        return data
   
    def writeFile(self, data, buf, pieceIndex, offset):
        print(pieceIndex, offset)
        with open(self.getTorrentName(), "r+b") as f:
            pieceLocation= (self.piece_length * pieceIndex) + offset
            f.seek(pieceLocation)
            f.write(data)
            f.close()
