import base64
from struct import *
import select
import binascii
# SYNC | SYNC | length | chksum | ID |flags| dados

BUFSZ = 2**16
HEADER_SIZE = 14
ACK_FLAG = 0x80
END_FLAG = 0x40


def generate_frame(word, sync, f_id, flag):
    if len(word) > 0:
        fformat = f"!IIHHBB{len(word)}s"
        frame = pack(fformat, sync,
                     sync, len(word), 0, f_id, flag, word)
        chksum = checksum(frame)
        frame = pack(fformat, sync,
                     sync, len(word), chksum, f_id, flag, word)
    else:
        fformat = f"!IIHHBB"
        frame = pack(fformat, sync,
                     sync, 0, 0, f_id, flag)
        chksum = checksum(frame)
        frame = pack(fformat, sync,
                     sync, 0, chksum, f_id, flag)

    return base64.b16encode(frame)


def receive_frame(sock, sync):
    ready_for_reading, _, _ = select.select([sock], [], [], 5.0)
    if not ready_for_reading:
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

    msg = frame[HEADER_SIZE:HEADER_SIZE + length] if length > 0 else ""

    if validChecksum(sync, chksum, f_id, flag, msg):
        return (msg, f_id, flag)

    return (None, None, None)


def validChecksum(sync, rec_chksum, f_id, flag, word):
    if len(word) > 0:
        fformat = f"!IIHHBB{len(word)}s"
        frame = pack(fformat, sync,
                     sync, len(word), 0, f_id, flag, word)
        chksum = checksum(frame)
    else:
        fformat = f"!IIHHBB"
        frame = pack(fformat, sync,
                     sync, 0, 0, f_id, flag)
        chksum = checksum(frame)

    if chksum == rec_chksum:
        return True

    return False


def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)


def checksum(frame):
    s = 0
    msg = bytes.hex(frame)

    # loop taking 2 characters at a time
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i+1]) << 8)
        s = carry_around_add(s, w)

    return ~s & 0xffff
