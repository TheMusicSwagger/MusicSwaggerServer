SERVER_HOSTNAME="musicswagger_server"
# hostname du server
SERVER_PORT=55666
# port du server
DEBUG_MODE=True
# mode debug
MAX_PACKET_SIZE=512
# taille maximum d'un packet en bytes
def log(*args):
    if DEBUG_MODE:
        print(*args)