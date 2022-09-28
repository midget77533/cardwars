from turtle import color, onrelease
import kivy
from kivymd.uix.label import MDLabel
from random import random
from tkinter import CURRENT
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock, mainthread
import time, sys, random, os
from kivy.graphics import Rectangle
from client import Client, Entity
from server import Server
from kivy.uix.behaviors.drag import DragBehavior
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton
from kivy.graphics import Color



Window.size = (700, 380)

#----------SERVER----------#

import socket
import threading

#----------CLIENT----------#

opponent_name = ""
game_started = False
c = None

THIS_HOSTING = False
THIS_CLIENT_MESSAGE = ""
GAME_STATE = ""
        
#----------APP----------#

sm = ScreenManager()
CLIENT = None
SEVER = None
CARDS = [
    #common
    [3,3],[2,2],[1,4],[2,1],[2,1],[2,3],[1,2],
    #uncommon
    [0,5],[4,3],[3,4],[4,4],[0,0],[3,4],[5,4],
    #rare
    [0,8], [6,6],[5,5],[0,0],[0,8],
    #legendary
    [1,0]
    ]
# NUMS = [0,0,0,0,0, 1,1,1,1,1, 2,2,2,2,2, 3,3,3,3,3, 4,4,4,4]
NUMS = [1,1,1,1 ,2,2,2,2, 3,3,3,3, 4,4,4,4, 5,5,5,5, 6,6,6,6, 7,7,7,7, 8,8,8, 9,9,9, 10,10,10, 11,11,11, 12,12,12, 13,13,13, 14,14,14, 15,15, 16,16, 17,17, 18,18, 19,19, 20]
class GameCard(Widget):
    def __init__(self, type, num, lpos):
        self.type = type
        self.lpos = lpos
        self.num = num
        self.c = CARDS[self.num -1]
        
        self.og_pos = (100 + (103 * (self.lpos -1)), 35)
        self.health = self.c[0]
        self.attack = self.c[1]
        self.dx = self.og_pos[0]
        self.dy = self.og_pos[1]
        self.picture = None
        self.rect = Rectangle(pos=(self.dx,self.dy), size=(60,80))
        self.alpha = 1

        self.picture = f"cards/{self.num}.png"
        self.rect.source = self.picture


    def draw(self):

        Color(1,1,1,1, mode="rgba")
        self.rect = Rectangle(pos=(self.dx,self.dy), size=(98, 140))
        self.rarity = 0
        self.picture = f"cards/{self.num}.png"
        self.rect.source = self.picture

class CreateRoomPage(Screen):
    def make_room(self):
        global connections, CLIENT, sm, SERVER
        nt = self.manager.get_screen("create_room_page").ids.network.text
        pt = self.manager.get_screen("create_room_page").ids.port.text
        name = self.manager.get_screen("create_room_page").ids.name_prompt.text
        host = nt
        port = int(pt)

        SERVER = Server(host, port)
        ST = threading.Thread(target=SERVER.start)
        ST.daemon = True
        ST.start()

        CLIENT = Client(host, port, "", [], name, True, sm)
        CLIENT.run()

        CST = threading.Thread(target=CLIENT.send_msg)
        CST.daemon = True
        CST.start()

        CSR = threading.Thread(target=CLIENT.receive_msg)
        CSR.daemon = True
        CSR.start()        

        self.manager.current = "gameroom_page"
            
class GameRoomPage(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
    def on_pre_enter(self, *args):
        GNT = threading.Thread(target=self.get_name)
        GNT.daemon = True
        GNT.start()
        self.start_btn = MDRaisedButton(text="START GAME", font_style="Button", font_size=20, pos_hint={"x":.7,"y":.1},on_release=self.start_game)
        # self.start_btn.on_release = self.start_game()
        

        return super().on_pre_enter(*args)
    def get_name(self):
        global CLIENT, SEVER
        self.ids.this_name_txt.text = CLIENT.name
        self.ids.heading_txt.text = "WAITING"
        self.add_start_btn()
        while CLIENT.opponent_name == "":
            pass
        if CLIENT.is_hosting:
            CLIENT.connections = SERVER.connections
            #self.add_start_btn()
        self.ids.opponent_name_txt.text = CLIENT.opponent_name
        self.ids.heading_txt.text = "READY"
        
        return CLIENT.opponent_name
    @mainthread
    def add_start_btn(self):
        self.add_widget(self.start_btn)
    @mainthread
    def start_game(self, *args) -> None:   
        global CLIENT
        CLIENT.msg = "[START]"
        self.manager.current = "game_page"

class GamePage(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)   
    def on_pre_enter(self, *args):
        
        self.hand = [GameCard(1,1,1), GameCard(2,2,2), GameCard(3,3,3), GameCard(4,4,4), GameCard(5,5,5)]
        for i in range(len(self.hand)):
            r = random.randint(0,len(NUMS) -1)
            s = NUMS[r]
            self.hand[i] = (GameCard(s,s, i + 1))
            self.hand[i].num = s 
            self.hand[i].type = s 

        self.SC = None
        self.hovererd_land_plot = 0
        self.land = []
        self.opponent_land = []
        self.cb_pos = (105, 25)
        with self.canvas:
            self.end_turn_btn = Rectangle(pos=(650, 100),size=(40, 40))
        #MDRaisedButton(id="btng", halign="center", text="2", font_size=30, pos_hint={"center_x":.95, "center_y":.2}, on_release=self.end_turn)
        self.tnt = MDLabel(id="this_name_txt", halign="center", text="1", font_size=30, pos_hint={"center_x":.15, "center_y":.8})
        self.ont = MDLabel(id="opponent_name_txt", halign="center", text="2", font_size=30, pos_hint={"center_x":.85, "center_y":.8})
        self.tmt = MDLabel(halign="center", text="1", font_size=30, pos_hint={"center_x":.15, "center_y":.7})
        self.omt = MDLabel(halign="center", text="2", font_size=30, pos_hint={"center_x":.85, "center_y":.7})
        self.draw()
        
        Clock.schedule_interval(self.update, 1/10)
        return super().on_pre_enter(*args)
    def manage_screen(self, *args):
        global CLIENT
        if not CLIENT.this_turn:

            for card in self.hand:
                if card != self.SC:
                    card.rect.pos = (card.rect.pos[0], -125)
        elif self.SC == None:
            for card in self.hand:
                if card != self.SC:
                    card.rect.pos = card.og_pos
    def end_turn(self):
        global CLIENT
        CLIENT.msg = f"[{CLIENT.name}]/[TURNCHANGE]/{CLIENT.magic}"
        CLIENT.this_turn = False
    def draw(self, *args):
        global CLIENT, s1c, s2c, s3c
        s1c = 0
        s2c = 0
        s3c = 0

        self.tnt.text = CLIENT.name + f": {str(CLIENT.hp)}"
        self.ont.text = CLIENT.opponent_name + f": {str(CLIENT.opp_hp)}"
        self.tmt.text = str(CLIENT.magic)
        self.omt.text = str(CLIENT.opp_magic)
        with self.canvas:
            if not CLIENT.is_hosting:
                Rectangle(source="arena card-wars_p2.png", pos=(0,0), size=(700,380 )) 
            if CLIENT.is_hosting:
                Rectangle(source="arena card-wars_p1.png", pos=(0, 0), size=(700,380)) 
            Color(1,0,0,1, mode="rgba")
            self.deck_pile = Rectangle(pos=(700 - 98 - 30, 100), size=(98, 140))
            Color(0,0,1,1, mode="rgba")
            self.dump_pile = Rectangle(pos=(30, 100), size=(98, 140))
            Color(0,1,1,1, mode="rgba")
            self.end_turn_btn = Rectangle(pos=(650, 20),size=(40, 40))
            Color(1,1,1,1, mode="rgba")
            for card in CLIENT.board:
                s = f'entity_view/{card.num}.png'
                Color(1,1,1,card.alpha)
                if card.slot == 0:
                    self.r = Rectangle(pos=(220.5, 100 + s1c * 80), size=(73.5 / 1.5, 105/ 1.5), source=(s))
                    s1c += 1
                if card.slot == 1:
                    self.r = Rectangle(pos=(330.5, 100 + s2c * 80), size=(73.5 / 1.5, 105 / 1.5), source=(s))
                    s2c += 1
                if card.slot == 2:
                    self.r = Rectangle(pos=(440.5, 100 + s3c * 80), size=(73.5 / 1.5, 105 / 1.5), source=(s))
                    s3c += 1
            es1c = 0
            es2c = 0
            es3c = 0
            for card in CLIENT.ob:
                Color(1,1,1,card.alpha)
                s = f"enemy_entity_view/{card.num}.png"
                if card.slot == 2:
                    self.r = Rectangle(pos=(220.5, 320 - es1c * 80), size=(73.5 / 1.5, 105 / 1.5), source=(s))
                    es1c += 1
                if card.slot == 1:
                    self.r = Rectangle(pos=(330.5, 320 - es2c * 80), size=(73.5 / 1.5, 105 / 1.5), source=(s))
                    es2c += 1
                if card.slot == 0:
                    self.r = Rectangle(pos=(440.5, 320 - es3c * 80), size=(73.5 / 1.5, 105 / 1.5), source=(s))
                    es3c += 1
            Color(0,0,0,.4, mode='rgba')
            for c in self.hand:
                c.draw()
    def update(self, *args):
        self.remove_widget(self.tnt)
        self.remove_widget(self.ont)
        self.remove_widget(self.tmt)
        self.remove_widget(self.omt)
        self.canvas.clear()
        self.draw()
        self.manage_screen()
        self.add_widget(self.tnt)
        self.add_widget(self.ont)
        self.add_widget(self.tmt)
        self.add_widget(self.omt)
    def on_touch_down(self, touch):
        global CLIENT
        pos = touch.pos
        
        if CLIENT.this_turn:
            for card in self.hand:
                self.current_card = card
                if pos[0] > self.current_card.rect.pos[0] and pos[0] < self.current_card.rect.pos[0] + 98 and pos[1] > self.current_card.rect.pos[1] and pos[1] < self.current_card.rect.pos[1] + 140:
                    card_pos = (touch.pos[0] - 30, touch.pos[1] - 40)
                    self.current_card.dx = pos[0] - 30
                    self.current_card.dy = pos[1] - 40
                    self.current_card.rect.pos = card_pos
                    self.SC = self.current_card
                    break
            if pos[0] > self.end_turn_btn.pos[0] and pos[0] < self.end_turn_btn.pos[0] + self.end_turn_btn.size[0] and pos[1] > self.end_turn_btn.pos[1] and pos[1] < self.end_turn_btn.pos[1] + self.end_turn_btn.size[1]:
                self.end_turn()
            btn = self.deck_pile
            if pos[0] > btn.pos[0] and pos[0] < btn.pos[0] + btn.size[0] and pos[1] > btn.pos[1] and pos[1] < btn.pos[1] + btn.size[1]:
                if len(self.hand) < 5 and CLIENT.magic >= 5:
                    r = random.randint(0,len(NUMS) -1)
                    s = NUMS[r]
                    c = GameCard(s, s, len(self.hand) + 1)
                    self.SC = c
                    self.hand.append(c)
                    CLIENT.magic -= 5
                    # CLIENT.msg = f"[{CLIENT.name}]/[MAGIC]/{CLIENT.magic}"
                    print('added card')
                elif CLIENT.magic >= 5:
                    print("too many card in your hand")
                elif len(self.hand) < 5:
                    print("not enough magic")

  

    def on_touch_move(self, touch):
        global CLIENT
        pos = touch.pos
        if pos[0] > 190 and pos[0] < 300 and pos[1] > 50 and pos[1] < 215:
            self.hovererd_land_plot = 1
        elif pos[0] > 300 and pos[0] < 410 and pos[1] > 50 and pos[1] < 215:
            self.hovererd_land_plot = 2
        elif pos[0] > 410 and pos[0] < 520 and pos[1] > 50 and pos[1] < 215:
            self.hovererd_land_plot = 3
        else:
            self.hovererd_land_plot = 0
        if self.SC != None:
            card_pos = (touch.pos[0] - 30, touch.pos[1] - 40)
            self.SC.rect.pos = card_pos
            self.SC.dx = pos[0] - 30
            self.SC.dy = pos[1] - 40
        if pos[1] > 100 and self.SC != None:
            self.cb_pos = (105,-80)
            for card in self.hand:
                if card != self.SC:
                    card.dx, card.dy = card.og_pos
                    card.dy = -125
        else:
            for card in self.hand:
                if card != self.SC:
                    card.dx, card.dy = card.og_pos
            self.cb_pos = (105, 25)



    def on_touch_up(self, touch):
        global CLIENT, CARDS, NUMS, s1c, s2c, s3c
        pos = touch.pos
        for card in self.hand:
            if card != self.SC and CLIENT.this_turn:
                card.rect.pos = card.og_pos
        if self.hovererd_land_plot != 0 and self.SC != None:
            if ((self.hovererd_land_plot == 1 and s1c < 2) or (self.hovererd_land_plot == 2 and s2c < 2) or (self.hovererd_land_plot == 3 and s3c < 2)) or (self.SC.num == 8 or self.SC.num == 12 or self.SC.num == 18 or self.SC.num == 19):
                oe = Entity(self.hovererd_land_plot - 1, self.SC.type, self.SC.health, self.SC.attack)
                if self.SC.type == 12:
                    for c in CLIENT.board:
                        if c.slot == self.hovererd_land_plot - 1:
                            c.health += 4
                            print("4 health added to entity")
                if self.SC.type == 18:
                    for c in CLIENT.board:
                        if c.slot == self.hovererd_land_plot - 1:
                            c.attack += 5
                            print("4 attack added to entity")
                if self.SC.type == 20:
                    CLIENT.board = []
                    CLIENT.ob = []
                CLIENT.board.append(oe)
                msg = f"[{CLIENT.name}]/[PLACED]/{oe.slot}|{oe.num}|{oe.health}|{oe.attack}"
                CLIENT.msg = msg
                CLIENT.update_board()
                self.hand.remove(self.SC)
                for i in range(len(self.hand)):
                    self.hand[i].lpos = i
                    self.hand[i].og_pos = (100 + (103 * i), 35)
                self.hovererd_land_plot = 0
        btn = self.dump_pile
        if pos[0] > btn.pos[0] and pos[0] < btn.pos[0] + btn.size[0] and pos[1] > btn.pos[1] and pos[1] < btn.pos[1] + btn.size[1]:
            if self.SC != None:
                self.hand.remove(self.SC)
                for i in range(len(self.hand)):
                    self.hand[i].lpos = i
                    self.hand[i].og_pos = (100 + (103 * i), 35)
                CLIENT.magic += 2
        if self.SC != None:
            self.SC.rect.pos = self.current_card.og_pos
            self.SC.dx = self.SC.og_pos[0]
            self.SC.dy = self.SC.og_pos[1]
            self.SC = None


class JoinRoomPage(Screen):
    def join_room(self):
        global connections, CLIENT, sm, SERVER
        nt = self.manager.get_screen("join_room_page").ids.network.text
        pt = self.manager.get_screen("join_room_page").ids.port.text
        name = self.manager.get_screen("join_room_page").ids.name_prompt.text
        
        host = nt
        port = int(pt)


        CLIENT = Client(host, port, "", [], name, False, sm)
        CLIENT.run()

        CST = threading.Thread(target=CLIENT.send_msg)
        CST.daemon = True
        CST.start()

        CSR = threading.Thread(target=CLIENT.receive_msg)
        CSR.daemon = True
        CSR.start()  

        self.manager.current = "gameroom_page"
        

class StartUpPage(Screen):
    pass
class CardWarsApp(MDApp):
    def build(self):
        global sm
        Builder.load_file("CardWars.kv")
        sm.add_widget(StartUpPage(name="start_up_page"))
        sm.add_widget(CreateRoomPage(name="create_room_page"))
        sm.add_widget(JoinRoomPage(name="join_room_page"))
        sm.add_widget(GameRoomPage(name="gameroom_page"))
        sm.add_widget(GamePage(name="game_page"))
 
        return sm



if __name__ == "__main__":    
    CardWars_app = CardWarsApp()
    CardWars_app.run()

