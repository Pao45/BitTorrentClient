from threading import Thread, Condition
from urllib.parse import urlparse
import threading
import time
import sys, hashlib, os
import socket
import struct
from Torrent import Torrent
from UDPTracker import UDPTracker
from Protocol import Protocol

class Downloader(Thread): 
    def __init__(self, buf):
        Thread.__init__(self)
        self.buf = buf
        self.metainfo = Torrent().getTrackerList()
        self.torrent = Torrent()
        self.uDPTracker = UDPTracker()
        self.protocol = Protocol()

    def run(self):
        announce_list = self.metainfo
        self.torrent.createFile()

        for tracker in announce_list:
            formatUrl = b''.join(tracker)
            url = formatUrl.decode('utf-8')
            
            if(str(url)[:3] == "udp"):
                url = urlparse(url)
        
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                        s.settimeout(2)
                        s.connect((url.hostname, url.port))
                        s.send(self.uDPTracker.create_connection_request())
                        msg = s.recv(4096)
                        s.close()
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    continue

                try: 
                    msg=self.uDPTracker.parse_connection_reply(msg)
                    msg=self.uDPTracker.create_announce(msg)
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                        s.settimeout(2)
                        s.connect((url.hostname, url.port))
                        s.send(msg)
                        data = s.recv(4096)
                        peer_list = self.uDPTracker.parse_announce_reply(data)
                        s.close()
                except BaseException as e: 
                    print('Failed to do something: ' + str(e))
                    continue

                handshake = self.protocol.create_msg_handshake()
                # peer_list = [("10.0.0.13", 14082)]
                for peer in peer_list:
                    host= peer[0]
                    port= peer[1]

                    try: 
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.settimeout(2)
                            s.connect((host, port))
                            s.send(handshake)
                            recv = s.recv(68)
                            
                            handshakemsg=self.protocol.decode_msg_handshake(recv)

                            if (handshakemsg):
                                length = s.recv(4)
                                id = ord(s.recv(1))
                                recv2 = s.recv(4096)
                                havePieces=self.protocol.decode_msg_bitfield(recv2)
                                msg= self.protocol.create_msg_interested()
                                s.send(msg)
                                length = s.recv(4)
                                id = ord(s.recv(1))
                                
                                if (id == 1):
                                    piece_length = self.torrent.getPieceLength()
                                    number_pieces = self.torrent.getTotalPieces()
                                    
                                    for index, pieces in enumerate(havePieces):
                                        # print(index, pieces)
                                        # print(self.torrent.getOffset(index), "OFFSEEEEET")
                                        if(pieces):
                                            for offset in self.torrent.getOffset(index):
                                                # print("Offset", offset)
                                                if(not self.protocol.getIndexOcurrence(index, self.buf)):
                                                    # print("entro")
                                                    # msg= self.protocol.create_msg_request(index, piece_length, offset)
                                                    msg= self.protocol.generateRequestPayload(index, offset, 2**14)
                                                    s.send(msg)
                                                    payloadlength = struct.unpack(">I", s.recv(4))[0]
                                                    idDownload = ord(s.recv(1))
                                                    # print("entro2")
                                                    if idDownload == 7:
                                                        pieceIndex = struct.unpack(">I",s.recv(4))[0]
                                                        pieceOffset = struct.unpack(">I",s.recv(4))[0]
                                                        # print("pieceIndex", pieceIndex)
                                                        # print("pieceOffset", pieceOffset)
                                                        data = b''

                                                        while(len(data) < payloadlength - 9):
                                                            response = s.recv(4096)
                                                            data += response
                                                        
                                                        self.torrent.writeFile(data, self.buf, pieceIndex, pieceOffset)
                                            self.buf.insert(index, 1)
                                            print(self.buf, "Downloaded Pieces")
                            else: 
                                continue
                    
                    except BaseException as e: 
                        print('Failed to do something: ' + str(e))
                        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
                        continue