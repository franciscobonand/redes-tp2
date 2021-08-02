import socket
import base64
from struct import *
# SYNC | SYNC | length | chksum | ID |flags| dados

BUFSZ = 2**16
FRAME_LENGTH = 2**16 - 1


def generateFrame(word, sync, id):
    fformat = f"!IIHHBB{len(word)}s"
    frame = pack(fformat, sync,
                 sync, len(word), 0, id, 0x3f, word)

    return base64.b16encode(frame)


class Client:
    def __init__(self, host, port, input, output):
        self.host = host
        self.port = int(port)
        self.input = input
        self.output = output
        self.sync = 0xdcc023c2
        self.frameID = 0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        with open(self.input, 'rb') as reader:
            file_data = reader.read()
        # total_frames = all data per frame + end frame
        total_frames = (len(file_data) // FRAME_LENGTH) + 1

        with self.sock as c:
            c.connect((self.host, self.port))
            msg = file_data[:FRAME_LENGTH]

            while self.frameID < total_frames:
                frame = generateFrame(msg, self.sync, self.frameID % 2)
                c.sendall(frame)
                self.frameID += 1

            data = c.recv(1024)

        print('Received', repr(data))
        print(base64.b16decode(data))
