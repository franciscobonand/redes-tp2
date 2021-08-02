import socket
import base64
from struct import *

HEADER_SIZE = 14


class Server:
    def __init__(self, port, input, output):
        self.port = int(port)
        self.input = input
        self.output = output

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('', self.port))

            print(f"server listening on port {self.port}")
            s.listen()

            conn, addr = s.accept()
            with conn:
                print('connected by', addr)
                while True:
                    data = conn.recv(1024)
                    if len(data) > 0:
                        decoded = base64.b16decode(data)
                        print(decoded)
                        sync1, sync2, length, chksum, id, flags = unpack(
                            '!IIHHBB', decoded[:HEADER_SIZE])

                        print(decoded[HEADER_SIZE:HEADER_SIZE + length])
                    if not data:
                        break
                    conn.sendall(data)
# test = base64.b16decode(frame)
#             print(test)
#             print(unpack("!IIHHBB", test[:14]))
