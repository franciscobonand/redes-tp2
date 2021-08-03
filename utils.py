import base64
from struct import *
import select

BUFSZ = 2**16
HEADER_SIZE = 14
ACK_FLAG = 0x80
END_FLAG = 0x40


def generate_frame(word, sync, id, flag):
    if len(word) > 0:
        fformat = f"!IIHHBB{len(word)}s"
        frame = pack(fformat, sync,
                     sync, len(word), 0, id, flag, word)
    else:
        fformat = f"!IIHHBB"
        frame = pack(fformat, sync,
                     sync, 0, 0, id, flag)

    return base64.b16encode(frame)


def receive_frame(sock, sync):
    ready = select.select([sock], [], [], 1.0)
    if not ready[0]:
        return (None, None, None)

    start_b = pack("!I", sync)
    frame = base64.b16decode(sock.recv(BUFSZ))
    frame_start = frame.find(start_b * 2)

    # reads requests contents to find frame start
    while frame_start == -1:
        frame = base64.b16decode(sock.recv(BUFSZ))
        if not frame:
            return (None, None, None)
        frame_start = frame.find(start_b * 2)

    frame = frame[frame_start:]
    _, _, length, chksum, f_id, flag = unpack("!IIHHBB", frame[:HEADER_SIZE])

    while len(frame[HEADER_SIZE:]) < length:
        msg = sock.recv(BUFSZ)
        if not msg:
            return (None, None, None)
        frame += base64.b16decode(msg)

    # returns frame (message, id, flag)
    msg = frame[:HEADER_SIZE + length] if length > 0 else ""
    return (msg, f_id, flag)
