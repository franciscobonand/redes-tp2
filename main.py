#!/usr/bin/env python3
import sys
from server import Server
from client import Client

# server: ./dcc023c2 -s <port> <input> <output>
# client: ./dcc023c2 -c <IP> <port> <input> <output>
if __name__ == "__main__":
    if len(sys.argv) == 5:
        kind = "s"
        port = sys.argv[2]
        input = sys.argv[3]
        output = sys.argv[4]
    elif len(sys.argv) == 6:
        kind = "c"
        host = sys.argv[2]
        port = sys.argv[3]
        input = sys.argv[4]
        output = sys.argv[5]
    else:
        print("invalid command, should be one of the following:")
        print("./dcc023c2 -s <port> <input> <output>")
        print("./dcc023c2 -c <IP> <port> <input> <output>")
        sys.exit(1)

    if kind == "s":
        s = Server(port, input, output)
        s.run()
    else:
        c = Client(host, port, input, output)
        c.run()