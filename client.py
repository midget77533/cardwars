from logging import error
import socket
import threading
import time
from kivy.clock import mainthread

class Entity:
    def __init__(self, slot, num, health, attack):
        self.slot = slot
        self.num = num
        self.health = health
        self.attack = attack
        self.drawn = False
        self.active = False
        self.just_placed = True
        self.alpha = 0.5
        if self.num == 8 or self.num == 12 or self.num == 15 or self.num == 18 or self.num == 19 or self.num == 20:
            self.active = True
            self.alpha = 1
            self.just_placed = False
class Client:
    def __init__(self, host, port, msg, connections, name, is_hosting, sm):
        self.host = host
        self.port = port
        self.msg = msg
        self.connections = connections
        self.c = None
        self.name = name
        self.is_hosting = is_hosting
        self.format = 'utf-8'
        self.received_msg = ""
        self.sm = sm
        self.opponent_name = ""
        self.ob = []
        self.board = []
        self.this_turn = is_hosting
        self.hp = 30
        self.opp_hp = 30
        self.magic = 50
        self.opp_magic = 50
        self.game_over = False
        self.victor = False
    def run(self):
        self.c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.c.connect((self.host,self.port))
    def send_msg(self):
        sent_name = False
        while True:
            if not sent_name :
                if self.is_hosting and len(self.connections) == 2:
                    self.msg = "[NAME]:" + self.name
                    self.c.send(self.msg.encode(self.format))
                    sent_name = True
                elif not self.is_hosting:
                    time.sleep(2)
                    self.msg = "[NAME]:" + self.name
                    self.c.send(self.msg.encode(self.format))
                    sent_name = True
                    print(self.connections)
            else:
                if self.msg == "[START]":
                    self.c.send(self.msg.encode(self.format))
                    self.msg = ""
                elif self.msg.split("/")[0] == f"[{self.name}]":
                    self.c.send(self.msg.encode(self.format))
                    self.msg = ""
    def receive_msg(self):
        while True:
            received_msg = self.c.recv(1028).decode(self.format)
            msg = received_msg.split(":")

            if received_msg == "[START]":
                self.game_screen()

            if msg[0] != "[NAME]":
                m1 = received_msg.split("/")
                if m1[0] == f"[{self.opponent_name}]":
                    if m1[1] == "[PLACED]":
                        m2 = m1[2].split("|")
                        if int(m2[1]) == 20:
                                self.board = []
                                self.ob = []
                        if int(m2[1]) != 12 and int(m2[1] != 18):
                            oe = Entity(int(m2[0]), int(m2[1]), int(m2[2]), int(m2[3]))
                            self.ob.append(oe)
                        
                        if int(m2[1]) == 12:
                            for c in self.ob:
                                if c.slot == int(m2[0]):
                                    c.health += 4
                                    print("4 health added to oppponent")
                        if int(m2[1]) == 18:
                            for c in self.ob:
                                if c.slot == int(m2[0]):
                                    c.attack += 5
                                    print("5 attack added to oppponent")
                            
                        
                    if m1[1] == "[TURNCHANGE]":
                        self.this_turn = True
                        self.opp_magic = int(m1[2])
                        self.update_board()
            else:
                if self.opponent_name == "" and msg[1] != self.name:
                    self.opponent_name = msg[1]
                    print("OPPONENT: " + self.opponent_name)

    def update_board(self):
        for MC in self.board:
            for OC in self.ob:   
                if ((MC.slot == 0 and OC.slot == 2) or (MC.slot == 2 and OC.slot == 0) or (MC.slot == 1 and OC.slot == 1)) and MC.active and OC.active:
                    if self.this_turn:
                        OC.health -= MC.attack
                        MC.health -= OC.attack
                        if OC.health <= 0:
                            self.magic += 2
                            # self.msg = f"[{self.name}]/[MAGIC]/{self.magic}"
                    else:
                        MC.health -= OC.attack
                        OC.health -= MC.attack
                        if OC.health <= 0:
                            self.magic += 2
                            # self.msg = f"[{self.name}]/[MAGIC]/{self.magic}"

        for MC in self.board:
            if MC.health <= 0:
                self.board.remove(MC)
                time.sleep(1)
        for OC in self.ob:
            if OC.health <= 0:
                self.ob.remove(OC)
                time.sleep(1)
        s1t = False
        s2t = False
        s3t = False
        for OC in self.ob:
            if not OC.just_placed and not OC.active:
                OC.active = True
                OC.alpha = 1
            if OC.active:
                if OC.slot == 0:
                    s3t = True
                if OC.slot == 1:
                    s2t = True
                if OC.slot == 2:
                    s1t = True
            if OC.just_placed:
                OC.just_placed = False
        for MC in self.board:
            if not MC.just_placed and not MC.active:
                MC.active = True
                MC.alpha = 1
            
            if MC.slot == 0:
                s1t = False
            if MC.slot == 1:
                s2t = False
            if MC.slot == 2:
                s3t = False
            if MC.just_placed:
                MC.just_placed = False
        if s1t:
            self.hp -= 1
        if s2t:
            self.hp -= 1
        if s3t:
            self.hp -= 1
        if not self.is_hosting:
            time.sleep(1)
        #self.msg = f"[{self.name}]/[HEALTH]|{self.hp}"
        s1t = False
        s2t = False
        s3t = False
        for MC in self.board:
            if MC.active:
                if MC.slot == 0:
                    s1t = True
                if MC.slot == 1:
                    s2t = True
                if MC.slot == 2:
                    s3t = True
        for OC in self.ob:
            if OC.slot == 0:
                s3t = False
            if OC.slot == 1:
                s2t = False
            if OC.slot == 2:
                s1t = False
        if s1t:
            self.opp_hp -= 1
        if s2t:
            self.opp_hp -= 1
        if s3t:
            self.opp_hp -= 1

        if self.opp_hp <= 0 and self.hp > 0:
            self.game_over = True
            self.victor = True
            print("WON")
        if self.opp_hp > 0 and self.hp <= 0:
            self.game_over = True
            self.victor = False
            print("LOST")






    @mainthread
    def game_screen(self):
        self.sm.current = "game_page"




