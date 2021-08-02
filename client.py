import socket
import base64


class Client:
    def __init__(self, host, port, input, output):
        self.host = host
        self.port = int(port)
        self.input = input
        self.output = output

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
            c.connect((self.host, self.port))

            with open(self.input, "r") as reader:
                line = reader.readline()
                while line != '':
                    bline = base64.b16encode(line.encode('ascii'))
                    c.sendall(bline)
                    line = reader.readline()

            data = c.recv(1024)

        print('Received', repr(data))
        print(base64.b16decode(data))
