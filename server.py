import socket,threading
import config as cfg


class CommunicatorServer(object,threading.Thread):
    is_running=None
    # etat du server
    sock=None
    # socket udp permettant l'envoi et la reception de donnees
    server_precision=None
    # correspond a la precision attendue
    def __init__(self,global_uid):
        self.global_uid=global_uid
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.start()

    def run(self):
        while self.is_running:
            packet,address=self.sock.recv(cfg.MAX_PACKET_SIZE)
            ppacket=self.check_packet(packet)
            if ppacket:
                pass


    def send(self,dest,fid,other_ip,data=b''):
        """
        Contruit et envoie un packet au server.
        :param dest: entier representant le cuid du destinataire
        :param fid: entier representant la fonction demandee
        :param data: bytes correspondants aux donnees formates pour la fonction (pas de verification avant envoi)
        :return: la reponse du server (peut prendre du temps)
        """
        packet=dest.to_bytes(1,byteorder="big")+fid.to_bytes(1,byteorder="big")+len(data).to_bytes(2,byteorder="big")+data
        packet+=self.calculate_crc(packet)
        self.send_raw(packet,other_ip)

    def send_raw(self,data,other_ip):
        self.sock.sendto(data,(other_ip,cfg.SERVER_PORT))

    def calculate_crc(self,data):
        return b''

    def check_packet(self,packet,other_ip=None,alert=True):
        parsed=self.parse_packet(packet)
        if parsed:
            if parsed[0] == 0xff:
                return parsed
            if parsed[0]==self.get_cuid():
                return parsed
            elif alert and other_ip:
                self.tell_invalid_cuid(other_ip)
                return False
        elif alert and other_ip:
            self.tell_invalid_packet(other_ip)
        return False

    def parse_packet(self,packet):
        try:
            cuid=int.from_bytes(packet[:1],byteorder="big")
            fid=int.from_bytes(packet[1:2],byteorder="big")
            datlen=int.from_bytes(packet[2:3],byteorder="big")
            dat=packet[3:3+datlen]
            crc=packet[3+datlen:]
            return [cuid,fid,dat,crc]
        except:
            cfg.log("Parse error...")
            return None

    def tell_invalid_cuid(self,other_ip):
        self.send(0,0,(2).to_bytes(1,byteorder="big"),other_ip)

    def tell_invalid_packet(self,other_ip):
        self.send(0,0,(1).to_bytes(1,byteorder="big"),other_ip)

    def get_precision(self):
        """
        :return: 'self.server_precision'
        """
        return self.server_precision

