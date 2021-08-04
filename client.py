import socket
from struct import *
import utils

BUFSZ = 2**16
FRAME_LENGTH = 2**16 - 1
STD_FLAG = 0x3f


class Client:
    def __init__(self, host, port, input, output, sync):
        self.host = host
        self.port = int(port)
        self.input = input
        self.output = output
        self.sync = sync
        self.frameID = 0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def get_nxt_msg(self, file_len):
        start = FRAME_LENGTH * self.frameID
        end_aux = FRAME_LENGTH * (self.frameID + 1)
        end = file_len if end_aux > file_len else end_aux
        return (start, end)

    def end(self):
        frame = utils.generate_frame(
            "", self.sync, self.frameID % 2, utils.END_FLAG)
        self.sock.sendall(frame)

    def run(self):
        with open(self.input, "rb") as reader:
            file_data = reader.read()
        # total_frames = all data per frame + end frame
        total_frames = (len(file_data) // FRAME_LENGTH) + 1

        with self.sock as s:
            try:
                s.connect((self.host, self.port))
                msg = file_data[:FRAME_LENGTH]

                while self.frameID < total_frames:
                    frame = utils.generate_frame(
                        msg, self.sync, self.frameID % 2, STD_FLAG)

                    print(f"sending frame {self.frameID}")
                    s.sendall(frame)

                    msg, f_id, flag = utils.receive_frame(s, self.sync)

                    while f_id == None:
                        print("ack not received (timeout)")
                        print(f"sending frame {self.frameID} again")
                        s.sendall(frame)
                        msg, f_id, flag = utils.receive_frame(s, self.sync)

                    if flag == utils.ACK_FLAG:
                        print(f"ack received for frame {f_id}")
                        self.frameID += 1
                        start, end = self.get_nxt_msg(len(file_data))
                        msg = file_data[start:end]
                    else:
                        raise "Invalid flag received"

                self.end()
                print("frames successfully sent to server")
            except:
                print("connection closed")
                s.close()
