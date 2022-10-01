import socket
import threading
import random
class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connections = []
        self.started_game = False
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
            if len(self.connections) > 1 and not self.started_game:
                r = random.randint(0,1)
                msg = "[STARTGAME]"
                first_player = self.connections[r]
                first_player.send(msg.encode('utf-8'))
                self.started_game = True
    def handle_clients(self, c, a):
        while True:   
            data = c.recv(1024)
            for conn in self.connections:
                conn.send(bytes(data))
            if not data:
                self.connections.remove(conn)
                conn.close()
                break


