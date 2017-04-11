import binascii
import socket
import threading

import pymysql as psql

import config as cfg

db = psql.connect("localhost", "root", "thomas", "musicswagger_config")


class CommunicatorServer(threading.Thread):
    is_running = None
    # etat du server
    sock = None
    # socket udp permettant l'envoi et la reception de donnees
    server_precision = None

    # correspond a la precision attendue
    def __init__(self):
        super(CommunicatorServer, self).__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', cfg.SERVER_PORT))
        cfg.log("Listening on", cfg.SERVER_PORT)
        self.daemon = True
        self.is_running = True
        self.start()

    def run(self):
        while self.is_running:
            packet, address = self.sock.recvfrom(cfg.MAX_PACKET_SIZE)
            ppacket = self.check_packet(packet)
            if ppacket:
                if ppacket[1] == 0x00:
                    cfg.log("Info :", ppacket[2])
                elif ppacket[1] == 0x01:
                    cfg.log("Ask for CUID :", ppacket[2])
                    cursor = db.cursor()
                    cursor.execute("SELECT CUID from connections")
                    dat = cursor.fetchall()
                    cursor.close()
                    for i in range(0x01, 0xFF):
                        if not i in dat:
                            cursor = db.cursor()
                            cursor.execute("SELECT CUID from connections")
                            cursor.execute(
                                "INSERT INTO connections (GUID,CUID) VALUES ('" + binascii.hexlify(ppacket[2]).decode(
                                    "ascii") + "'," + str(i) + ")")
                            cursor.close()
                            self.send(0xff, 0x02, address[0], i.to_bytes(1, "big"))
                            break
                elif ppacket[1] == 0x03:
                    cfg.log("Ask for SPEC")
                    self.send(ppacket[0], 0x04, address[0], b'')
                elif ppacket[1] == 0x04:
                    cfg.log("Give SPEC :", ppacket[2])
                elif ppacket[1] == 0x10:
                    cfg.log("Ask PREC")
                    self.send(ppacket[0], 0x11, address[0], b'\x0f')
                elif ppacket[1] == 0x11:
                    cfg.log("Give PREC :", ppacket[2])
                elif ppacket[1] == 0x20:
                    cfg.log("Ask DATA")
                elif ppacket[1] == 0x21:
                    cfg.log("Give DATA :", ppacket[2])
                    prec = (int.from_bytes(ppacket[2][:1], "big") + 1) // 8
                    vals = []
                    for i in range(2):
                        # suppose qu'il y a 2 chanels : besoin de db pour stocker les specs
                        vals.append(int.from_bytes(ppacket[2][1 + (i * prec):1 + ((i + 1) * prec)], "big"))
                    print(prec, vals)

    def send(self, dest, fid, other_ip, data=b''):
        """
        Contruit et envoie un packet au server.
        :param dest: entier representant le cuid du destinataire
        :param fid: entier representant la fonction demandee
        :param data: bytes correspondants aux donnees formates pour la fonction (pas de verification avant envoi)
        :return: la reponse du server (peut prendre du temps)
        """
        packet = dest.to_bytes(1, "big") + (0).to_bytes(1, "big") + fid.to_bytes(1, "big") + len(data).to_bytes(1,
                                                                                                                "big") + data
        packet += self.calculate_crc(packet)
        self.send_raw(packet, other_ip)

    def send_raw(self, data, other_ip):
        self.sock.sendto(data, (other_ip, cfg.SERVER_PORT + 1))

    def calculate_crc(self, data):
        return b''

    def check_packet(self, packet, other_ip=None, alert=True):
        parsed = self.parse_packet(packet)
        if parsed:
            if parsed[0] == 0xff or parsed[0] == 0x00:
                return parsed[1:-1]
            self.tell_invalid_cuid(other_ip)
            return False
        elif alert and other_ip:
            self.tell_invalid_packet(other_ip)
        return False

    def parse_packet(self, packet):
        try:
            tocuid = int.from_bytes(packet[:1], "big")
            fromcuid = int.from_bytes(packet[1:2], "big")
            fid = int.from_bytes(packet[2:3], "big")
            datlen = int.from_bytes(packet[3:4], "big")
            dat = packet[4:4 + datlen]
            crc = packet[4 + datlen:]
            final = [tocuid, fromcuid, fid, dat, crc]
            cfg.log(final)
            return final
        except:
            cfg.log("Parse error...")
            return Noned(0, 0x21, data)

    def tell_invalid_cuid(self, other_ip):
        self.send(0, 0, (2).to_bytes(1, "big"), other_ip)

    def tell_invalid_packet(self, other_ip):
        self.send(0, 0, (1).to_bytes(1, "big"), other_ip)

    def get_precision(self):
        """
        :return: 'self.server_precision'
        """
        return self.server_precision

    def stop(self):
        """
        Stoppe le thread du server.
        """
        self.is_running = False


server = CommunicatorServer()
try:
    server.join()
except KeyboardInterrupt:
    server.stop()
