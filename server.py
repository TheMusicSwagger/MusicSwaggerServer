import socket,threading
import config as cfg


class Communicator(object,threading.Thread):
    communication_uid=None
    # uid court donne par le server
    server_ip=None
    # chaine de caractere representant l'adrese ip du server
    sock=None
    # socket udp permettant l'envoi et la reception de donnees
    global_uid=None
    # voir 'Brain.global_uid'
    server_precision=None
    # correspond a la precision attendue par le server
    def __init__(self,global_uid):
        self.global_uid=global_uid
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(5)
        # maximum d'attente pour recevoir des donnees (en secondes)
        try:
            self.server_ip=socket.gethostbyname(cfg.SERVER_HOSTNAME)
            # recuperation de l'ip du server
        except socket.gaierror:
            self.server_ip="127.0.0.1"
            cfg.log("Can't find server !!!")
        self.ask_for_cuid()
        self.ask_for_precision()


    def send(self,dest,fid,data=b''):
        """
        Contruit et envoie un packet au server.
        :param dest: entier representant le cuid du destinataire
        :param fid: entier representant la fonction demandee
        :param data: bytes correspondants aux donnees formates pour la fonction (pas de verification avant envoi)
        :return: la reponse du server (peut prendre du temps)
        """
        if self.get_server_ip()==None:
            raise Exception("Must get server IP first !")
        packet=dest.to_bytes(1,byteorder="big")+fid.to_bytes(1,byteorder="big")+len(data).to_bytes(2,byteorder="big")+data
        packet+=self.calculate_crc(packet)
        self.send_raw(packet)

    def send_raw(self,data):
        self.sock.sendto(data,(self.server_ip,cfg.SERVER_PORT))

    def calculate_crc(self,data):
        return b''

    def check_packet(self,packet,alert=True):
        parsed=self.parse_packet(packet)
        if parsed:
            if parsed[0] == 0xff:
                return True
            if parsed[0]==self.get_cuid():
                return True
            elif alert:
                self.tell_invalid_cuid()
                return False
        elif alert:
            self.tell_invalid_packet()
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

    def ask_for_cuid(self):
        if self.communication_uid==None:
            self.communication_uid=self.parse_packet(self.send(0,1,binascii.unhexlify(self.get_guid())))[2]
            cfg.log(self.communication_uid)


    def ask_for_precision(self):
        if self.server_precision==None:
            self.server_precision=self.parse_packet(self.send(0,1))[2]
            cfg.log(self.server_precision)


    def tell_invalid_cuid(self):
        self.send(0,0,(2).to_bytes(1,byteorder="big"))

    def tell_invalid_packet(self):
        self.send(0,0,(1).to_bytes(1,byteorder="big"))

    def get_guid(self):
        """
        :return: 'self.global_uid'
        """
        return self.global_uid

    def get_cuid(self):
        """
        :return: 'self.communication_uid'
        """
        return self.communication_uid

    def get_server_ip(self):
        """
        :return: 'self.server_ip'
        """
        return self.server_ip

    def get_precision(self):
        """
        :return: 'self.server_precision'
        """
        return self.server_precision

