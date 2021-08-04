import socket
import utils
from struct import *


def socket_is_closed(sock):
    try:
        # this will try to read bytes without blocking and also without removing them from buffer (peek only)
        data = sock.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
        if len(data) == 0:
            return True
    except BlockingIOError:
        return False  # socket is open and reading from it would block
    except ConnectionResetError:
        return True  # socket was closed for some other reason
    except Exception as e:
        print("unexpected exception when checking if a socket is closed")
        return False
    return False


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
            try:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("", self.port))

                print(f"server listening on port {self.port}")
                print("use ctrl+C to close the server")

                s.listen()
                while True:
                    conn, addr = s.accept()
                    with conn:
                        print("connected by", addr)

                        while True:
                            msg, f_id, flag = utils.receive_frame(
                                conn, self.sync)

                            if f_id == None:
                                if socket_is_closed(conn):
                                    print("connection with client was closed")
                                    conn.close()
                                    break
                                else:
                                    print("invalid frame received")
                                    continue
                            elif flag == utils.END_FLAG:
                                print(
                                    f"communication with {addr} concluded successfully")
                                conn.close()
                                break
                            elif self.f_id != f_id:
                                print(f"received frame {f_id}")
                                self.f_id = f_id
                                self.output_data += msg
                                print(f"sending ack of frame {f_id}")
                                self.ack(conn)

                        with open(self.output_file, "ab") as output:
                            output.write(self.output_data + b'\n')
                        self.f_id = 1
                        self.output_data = b""
            except:
                print("connection closed")
                s.close()
