import socket
import utils
from struct import *


class Server:
    def __init__(self, port, input, output, sync):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = int(port)
        self.input = input
        self.output_file = output
        self.output_data = b""
        self.sync = sync
        self.f_id = 1

    def ack(self, conn):
        frame = utils.generate_frame("", self.sync, self.f_id, utils.ACK_FLAG)
        conn.sendall(frame)

    def run(self):
        with self.sock as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("", self.port))

            print(f"server listening on port {self.port}")
            s.listen()

            conn, addr = s.accept()
            with conn:
                print("connected by", addr)

                while True:
                    msg, f_id, flag = utils.receive_frame(conn, self.sync)

                    if f_id == None:
                        print("transmission error (timeout)")
                        continue
                    elif flag == utils.END_FLAG:
                        print(
                            f"communication with {addr} concluded successfully")
                        break
                    elif self.f_id != f_id:
                        self.f_id = f_id
                        self.output_data += msg
                        self.ack(conn)

        with open(self.output_file, "wb") as output:
            output.write(self.output_data[utils.HEADER_SIZE:])
