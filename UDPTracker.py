from Torrent import Torrent
import random
import struct

class UDPTracker(): 
    def __init__(self):
        self.tracker_request = self.create_connection_request() 
        self.torrent = Torrent()    

    # Step 1: 
    #   Talk to the tracker 
    def create_connection_request(self):
        protocol_id = 0x41727101980 
        action = 0 	
        transaction_id = random.randrange(1,1000)
        msg = struct.pack("!q", protocol_id) 
        msg += struct.pack("!i", action) 
        msg += struct.pack("!i", transaction_id) 
        return msg

    def create_announce(self, data):
        connection_id = data[2]
        action= 1
        transaction_id= data[1] 
        info_hash= self.torrent.getInfoHash()
        peer_id= self.torrent.getPeerId()
        downloaded=0
        left= self.torrent.getLeft()
        uploaded= 0
        event= 0
        ip_address=0
        key=random.randrange(1,1000)
        num_want=-1
        port= 6889

        buf = struct.pack("!qii20s20sqqqiiiih", connection_id, action, transaction_id, 
        info_hash, str.encode(peer_id), downloaded, left, uploaded, event, ip_address, key, num_want, port)
        return buf
    
    def parse_connection_reply(self, response):
        response= struct.unpack("!iiq", response)
        return response
    
    def parse_announce_reply(self, response):
        peer_List= []
        response = [response[i:i+6] for i in range(20, len(response), 6)]
        for peer in response:
            ip='.'.join(str(i) for i in peer[:4])
            port = int.from_bytes(peer[4:], byteorder='big')
            peer_List.append((ip, port))
        return peer_List