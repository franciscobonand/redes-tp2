import socket
import base64


class Server:
    def __init__(self, port, input, output):
        self.host = '127.0.0.1'
        self.port = int(port)
        self.input = input
        self.output = output

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            print(f"server listening in {self.host} on port {self.port}")
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('connected by', addr)
                while True:
                    data = conn.recv(1024)
                    print(base64.b16decode(data))
                    if not data:
                        break
                    conn.sendall(data)
