## Black Jack - GUI Version
# GUI

from bj_deck_hand import *
from bj_constants import *
from pygame.math import Vector2
import pygame
import os

    
os.environ['SDL_VIDEO_CENTERED'] = '1'


class GameState():
    def __init__(self):
        self.deal  = True
        self.draw  = False
        self.stand = False
        self.clear_table = False
        
    def update(self, button):
        if button == "deal":
            self.clear_table = True
            self.deal  = False
            self.draw  = True
            self.stand = True            
        elif button == "stand":
            self.draw = False
            self.deal = True
    
    
class Mouse():
    def __init__(self):
        self.click = False
        self.pos = (0,0)


class Play():
    def __init__(self):
        self.deck   = Deck()
        self.player = Hand()
        self.dealer = Hand()
        
        self.dealer_go = False
        self.win_result = []
        self.clear_hand = False
        
    def end_round(self, win):
#.....................................................
        print("dealer", self.dealer.value)
        print("player", self.player.value)
#..........................................................       
        self.win_result.append(win)
        self.player.value = 0
        self.dealer.value = 0
#.......................................................     
        print("win", self.win_result)
#...............................................    
    def check_winner(self):
        self.player.calc_hand()
        
        if self.player.value == 21 or self.dealer.value > 21:
            self.end_round(1)
        elif self.player.value > 21:
            self.end_round(0)
        elif self.player.value < 21 and self.dealer_go:
            if self.player.value <= self.dealer.value:
                self.end_round(0)
            elif self.player.value > self.dealer.value:
                self.end_round(1)
# WHEN PLAYER LOSES WITH >21, THEN DEALER BUTTON IS STILL DEACTIVATED, BECAUSE
# IT ACTIVATES ONLY AFTER PERSSING STAND :(
    
    def deal(self):
        self.player.cards = []
        self.dealer.cards = []

        for i in range(2):
            self.player.add_card(self.deck.draw_card())
            self.dealer.add_card(self.deck.draw_card())
            
    def draw(self):
        self.player.add_card(self.deck.draw_card())
        self.check_winner()
        
    def stand(self):
        self.dealer_go = True
        while True:
            self.dealer.calc_hand()
            if self.dealer.value <= 16:
               self.dealer.add_card(self.deck.draw_card())
            elif self.dealer.value >= 17:
                self.check_winner()
                break


class Interface():
    def __init__(self):
        self.state = GameState()
        self.mouse = Mouse()
        self.game = Play()
        
        self.window = []
        self.running = True
        self.window_size = window_size
        self.clock = pygame.time.Clock()
        
        self.buttonArea = {'pos':  Vector2(0,0),
                           'size': Vector2(self.window_size[0] * 0.25, self.window_size[1])}
        self.table      = {'pos':  Vector2(self.window_size[0] * 0.25, 0),
                           'size': Vector2(self.window_size[0] * 0.75, self.window_size[1])}
        self.initialize()        

    def initialize(self):
        pygame.init()
        
        # ...for Full Screen...
        # x = pygame.display.get_desktop_sizes()[display][0]
        # y = pygame.display.get_desktop_sizes()[display][1]
        # window_size = (x,y-60) # -60 to display Caption
        
        self.window = pygame.display.set_mode(window_size, display=display)
        pygame.display.set_caption("Black Jack")
        self.window.fill(window_color)
    
    def process_input(self):  
        self.mouse.click = False
        self.mouse.pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse.click = True
                
            
                # else:
                #     if state.state == 1:
                #         if event.key == pygame.K_RETURN:
                #             print("RETURN")
                #             state.state = 2
                #         elif event.key == pygame.K_BACKSPACE:
                #             print("BACKSPACE")
                #             state.text_input = state.text_input[:-1]
                #         else:
                #             state.text_input += event.unicode
                #             print("Text", state.text_input)

    
    def exit(self):
        self.running = False

    def showCards(self, hand, agent):
        cardID = []
        for card in hand:
            cardID.append(str(card.type.value) + str(card.color.name))
        
        if agent == "player":
            start_pos = Vector2(self.table['pos'].x + 20,
                                self.table['pos'].y + 20) 
        elif agent == "dealer":
            start_pos = Vector2(self.table['pos'].x + 20,
                                self.table['pos'].y + window_size[1]/2 + 20) 
            
        for i,ID in enumerate(cardID):
            path = Path(cards_path, ID + ".png")
            card_img = pygame.image.load(path)
            #card_img = pygame.transform.scale(card_img, (150,150))
            card_rect = card_img.get_rect()
            card_width  = card_rect[2]
            card_height = card_rect[3]
            pos = (int(start_pos.x + card_width * i), int(start_pos.y))
            
            self.window.blit(card_img, pos, card_rect)
            
    def button(self, text, pos_y, active, action=None, button=None):
        # Button Rect
        w = self.buttonArea['size'].x * 0.75
        h = self.buttonArea['size'].y * 0.1
        button_rect = pygame.Rect((0,0), (w,h))
        button_rect.centerx = self.buttonArea['size'].x / 2
        button_rect.centery = pos_y
        x = button_rect.x
        y = button_rect.y
        
        # Text
        button_font = pygame.font.SysFont(font,35)
        button_text = button_font.render(text, True, black)
        text_rect = button_text.get_rect(center = button_rect.center)
        
        # Status (Used vs. Unused)
        if x < self.mouse.pos[0] < x + w and y < self.mouse.pos[1] < y + h:
            pygame.draw.rect(self.window, color_active, button_rect)
            self.window.blit(button_text, text_rect)
            if self.mouse.click and active:
                if action != None:
                    action()
                if button != None:
# .............................CHANGE HERE !!!!............................
# state shall not be called within button()
                    self.state.update(button)
# .............................CHANGE HERE !!!!............................
        else:
            pygame.draw.rect(self.window, color_inactive, button_rect)
            self.window.blit(button_text, text_rect)
    
    def update(self):
        pass
        #self.state.update()
        
    def render(self):
        # Background (table)
        self.window.fill(window_color)
        
        # Button Area
        pygame.draw.rect(self.window, 
                         buttonArea_color, 
                         pygame.Rect(self.buttonArea['pos'], 
                                     self.buttonArea['size'])
                         )
        
        # Buttons
        self.button("Deal", 
                    50, 
                    self.state.deal, 
                    self.game.deal, 
                    "deal")
        self.button("Hit", 
                    150, 
                    self.state.draw,
                    self.game.draw,
                    )
        self.button("Stand",
                    250,
                    self.state.stand,
                    self.game.stand,
                    "stand")
        self.button("QUIT", 
                    500,
                    True,
                    self.exit)
        
        # Cards
        if self.state.clear_table:
            self.state.clear_table = False
        else:
            self.showCards(self.game.player.cards, "player")
            self.showCards(self.game.dealer.cards, "dealer")
        
        pygame.display.update()
        
    def run(self):
        while self.running == True:
            self.process_input()
            self.update()
            self.render()
            self.clock.tick(FPS)
        pygame.quit()
            

userInterface = Interface()
userInterface.run()
