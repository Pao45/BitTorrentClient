from threading import Thread, Condition
import threading
import time
from Protocol import Protocol
import socket


class Uploader(Thread):
    def __init__(self, buf):
        Thread.__init__(self)
        self.protocol = Protocol()
        self.buf = buf

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", 14045))
            s.listen(2)
            while True:
                conn, addr = s.accept()
                with conn:
                    print("Connected -------------------")
                    
                    data = conn.recv(68)
                    validHandshake = self.protocol.decode_msg_handshake(data)

                    if (validHandshake):
                        conn.send(self.protocol.create_msg_handshake())
                        conn.send(self.protocol.create_msg_bitfield(self.buf))
                        length = conn.recv(4)
                        idmessage = ord(conn.recv(1))
                        if (idmessage == 2):
                            conn.send(self.protocol.create_msg_unchoke)
                            length = conn.recv(4)
                            idmessage = ord(conn.recv(1))
                            if(idmessage == 6):
                                pieceIndex = struct.unpack(">I", conn.recv(4))[0]
                                pieceOfset = struct.unpack(">I", conn.recv(4))[0]
                                pieceLength = struct.unpack(">I", conn.recv(4))[0]
                                piece = self.protocol.create_msg_piece(
                                    piece_index, pieceOffset)
                                conn.send(piece)
                            conn.close()
                        conn.close()
                    conn.close()
