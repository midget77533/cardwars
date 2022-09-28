import socket
import threading

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connections = []
    def start(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        self.s.listen(2)
        while True:
            conn, addr = self.s.accept()
            CT = threading.Thread(target=self.handle_clients, args=(conn, addr))
            CT.daemon = True
            CT.start()
            self.connections.append(conn)
    def handle_clients(self, c, a):
        while True:   
            data = c.recv(1024)
            for conn in self.connections:
                conn.send(bytes(data))
            if not data:
                self.connections.remove(conn)
                conn.close()
                break


