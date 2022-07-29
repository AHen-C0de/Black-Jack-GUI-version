## Black Jack - GUI Version
# GUI

from bj_deck_hand import *
from bj_constants import *
from pygame.math import Vector2
import pygame as pg
import os
from time import sleep

    
os.environ['SDL_VIDEO_CENTERED'] = '1'


class Mouse():
    def __init__(self):
        self.click = False
        self.pos = (0,0)


class GameState():
    def __init__(self):
        self.running = True
        
        # Button status (enabled/disabled)
        self.shuffle_ac = True
        self.deal_ac    = False
        self.draw_ac    = False
        self.stand_ac   = False
        
        # Render status
        ## stop rendering cards, when "Deal" was pressed
        self.clear_table     = False
        ## hide Dealer cards, when "Deal" was pressed but it's still Players turn
        self.hideDealerCards = False
        
        # Initiate Game Objects
        self.deck   = Deck()
        self.player = Hand()
        self.dealer = Hand()
        
        # Game States
        self.gameState = "new game"
         # "new game"   (player presses "Shuffle Deck" button and
         #               thus starting a new game)
         # "bet"        (betting phase, waiting for player to approve 
         #               input),
         # "play"       (drawing cards)
         # "result"     (round finished, results are obtained)
         # "game over"  (current deck is done due to Zero balance or 
         #               because deck is empty. clicking button 
         #               "Shuffle Deck" will reset everything.")
        self.playerScore = 0
        self.dealerScore = 0
        self.balance     = 0
        self.bet         = None
        self.result      = None
          # None, 0 (loose), 1 (win), 2 (draw), 3 (21 - Black Jack!),
          # "broke" (Balance is Zero), "empty" (deck is empty)
        
        # Game status
        self.dealer_go     = False
        self.stand_ongoing = False
        
    def update(self, button, bet):
        #print(self.gameState)
        self.processButtons(button)
        if self.gameState == "bet":
            self.processBet(bet, button)
        if self.gameState == "play":
            self.check_winner()
        self.check_gameOver()
        
    def processBet(self, bet, button):
        if bet != "":
            bet = int(bet)
            
            if button in ["Hit","Stand"]:
            # Note: if Player places a bet > GameState.balance, Hit and Stand
            # button will be disabled
                self.bet = bet
                self.balance -= bet
                self.gameState = "play"
            else:
                # enable Hit & Stand buttons only, if Player bet <= GameState.balance, 
                # otherwise disable
                if bet > self.balance:
                    self.draw_ac  = False
                    self.stand_ac = False
                else:
                    self.draw_ac  = True
                    self.stand_ac = True
        
    def check_gameOver(self):
        if self.gameState != "new game":
            end = False
            if self.deck.cards == []:                   
                end = True
                self.result = "empty"
                
            if self.gameState == "result":
                if self.balance == 0:
                    end = True
                    self.result = "broke"
            elif self.gameState == "bet":
                if len(self.player.cards) < 2 or len(self.dealer.cards) < 2:
                    end = True
                    self.result = "empty"
                    
            if end:
                self.gameState     = "game over"
                self.stand_ongoing = False
                self.shuffle_ac = True
                self.deal_ac    = False
                self.draw_ac    = False
                self.stand_ac   = False
                
    def check_winner(self):
        self.player.calc_hand()
        if self.player.value == 21:
            self.end_round(3)
        elif self.dealer.value > 21:
            self.end_round(1)
        elif self.player.value > 21:
            self.end_round(0)
        # if round is still running (self.player.value < 21), 
        # only check winner, if stand button was clicked -> dealer_go = True
        elif self.dealer_go:
            if self.player.value < self.dealer.value:
                self.end_round(0)
            elif self.player.value > self.dealer.value:
                self.end_round(1)
            elif self.player.value == self.dealer.value:
                self.end_round(2)
        
    def end_round(self, result):
        self.gameState = "result"
        self.result    = result
        # add Score to agents & credit current bet to player
        if result == 0: # player looses
            self.dealerScore += 1
        elif result in [1,3]: # player wins
            self.playerScore += 1
            self.balance += (2 * self.bet)
        elif result == 2: # draw
            self.balance += self.bet
            
        # reset values
        self.bal_valid = False
        self.player.value = 0
        self.dealer.value = 0
        self.dealer_go = False

    def processButtons(self, button):   
        if button == "QUIT":
            self.running = False
            
        elif button == "Shuffle Deck":
            self.shuffleDeck()
            
        elif button == "Deal":
            self.deal_ac = False
            self.gameState       = "bet"
            self.clear_table     = True
            self.hideDealerCards = True
            self.bet             = None
            self.deal()
        
        elif button == "Hit":
            # after pressing Hit or Stand, set self.result from "bet" to 
            # None, to get rid of "Place your bet!" call inside 
            # userInterface.render.betBox()
            self.draw()
            
        elif button == "Stand":
            self.draw_ac  = False
            self.stand_ac = False
            self.deal_ac  = True
            self.stand_ongoing   = True # to run stand() in the next Interface.run() loop
            self.hideDealerCards = False
            
        elif self.stand_ongoing and self.gameState == "play":
        # 'stand_ongoing' to activate stand() as long as dealer still
        # draws cards
            self.stand()
   
        if self.gameState == "result":
            self.draw_ac  = False
            self.stand_ac = False
            self.deal_ac  = True
    
    def shuffleDeck(self):
        self.gameState   = "new game"
        self.clear_table = True
        # reset values
        self.playerScore = 0
        self.dealerScore = 0
        self.balance     = 1000
        self.player.cards = []
        self.dealer.cards = []
        self.result      = None
        self.bet         = None
        self.shuffle_ac = False
        self.deal_ac    = True
        # build new deck
        self.deck.build()
        self.deck.shuffle()
    
    def deal(self):
        # reset hand of Player and Dealer
        self.player.cards = []
        self.dealer.cards = []

        for i in range(2):
            # self.deck is inst. of Deck() class from 'bj_deck_hand' module
            self.player.add_card(self.deck.draw_card())
            self.dealer.add_card(self.deck.draw_card())
            
    def draw(self):
        self.player.add_card(self.deck.draw_card())
        
    def stand(self):
        self.dealer.calc_hand()
        self.player.calc_hand()
        if self.dealer.value < self.player.value:
            sleep(1.5)
            self.dealer.add_card(self.deck.draw_card())
        elif self.dealer.value == self.player.value and \
             self.dealer.value < 17:
            sleep(1.5)
            self.dealer.add_card(self.deck.draw_card())
        else:
            self.stand_ongoing = False
            self.dealer_go = True # to enable value check between Player & Dealer
           

class Interface():
    def __init__(self):
        self.window_size = window_size
        self.clock       = pg.time.Clock()
        
        self.state = GameState()
        self.mouse = Mouse()
        self.bet_input     = ""
        self.buttonClicked = None
        
        # Define size of Button and Table Area
        ## as percentages of window size
        ## button area 25% width + table area 75% width
                           # Start position: x=0, y=0
        self.buttonArea = {'pos':  Vector2(0,0),
                           # length = 25% of window width, height = window height
                           'size': Vector2(self.window_size[0] * 0.25, \
                                           self.window_size[1]), \
                           # width of elements within buttonArea
                           ## *0.75 = 75% of buttonArea width
                           'elementWidth': (self.window_size[0] * 0.25) * 0.75}
        # define size of right table area
                           # Start position: x = 25% of window width (right of 
                           # buttonArea), y=0
        self.table      = {'pos':  Vector2(self.window_size[0] * 0.25, 0),
                           # length = 75% of window width, height = window height
                           'size': Vector2(self.window_size[0] * 0.75, \
                                           self.window_size[1])}
        self.initialize()        

    def initialize(self):
        pg.init()
        
        # ...for Full Screen...
        # x = pg.display.get_desktop_sizes()[display][0]
        # y = pg.display.get_desktop_sizes()[display][1]
        # window_size = (x,y-60) # -60 to display Caption
        
        self.window = pg.display.set_mode(window_size, display=display)
        pg.display.set_caption("Black Jack")
        pg.display.set_icon(pg.image.load(Path(images_path, "icon.png")))
        self.window.fill(window_color)
    
    def process_input(self):  
        self.mouse.click = False
        self.mouse.pos = pg.mouse.get_pos()
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.state.running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                    self.mouse.click = True
            elif event.type == pg.KEYDOWN: # get player keyboard input (bet)
                if self.state.gameState == "bet":
                # enable keyboard input only during betting phase
                    if event.key == pg.K_BACKSPACE: # delete last char
                        self.bet_input = self.bet_input[:-1]
                    else:
                        try: # only allow integers for the bet
                            num = int(event.unicode)
                            if self.bet_input == "":
                                if num > 0:
                                # do not allow Zero for the first number
                                    self.bet_input += event.unicode
                            else:
                                self.bet_input += event.unicode
                        except ValueError:
                            pass

    ###########    Render functions begin    ###########  

    def showCards(self, agent):
        cardID = []
        
        if agent == "player":
            hand = self.state.player.cards
            start_pos = Vector2(self.table['pos'].x + 20,
                                self.table['pos'].y + 20) 
        elif agent == "dealer":
            # until player didn't hit Stand button, don't show dealer cards
            if self.state.gameState != "new game" and self.state.hideDealerCards:
                hand = []
                # 2x back cover
                cardID = ["yellow_back" for i in range(2)]
            else:
                hand = self.state.dealer.cards
            start_pos = Vector2(self.table['pos'].x + 20,
                                self.table['pos'].y + window_size[1]/2 + 20) 
        
        for card in hand:
            cardID.append(str(card.type.value) + str(card.color.name))    
            
        for i,ID in enumerate(cardID):
            path = Path(images_path, "cards", ID + ".png")
            card_img = pg.image.load(path)
            #card_img = pg.transform.scale(card_img, (150,150))
            card_rect = card_img.get_rect()
            card_width  = card_rect[2]
            card_height = card_rect[3]
            pos = (int(start_pos.x + card_width * i), int(start_pos.y))
            
            self.window.blit(card_img, pos, card_rect)
            
    def button(self, button, y_center, hight, enabled):
        # Button Rect
        w = self.buttonArea['elementWidth']
        h = hight
        button_rect = pg.Rect((0,0), (w,h))  # Rect((left,top), (width,height))
        # center buttons with the buttonArea
        button_rect.centerx = self.buttonArea['size'].x / 2
        button_rect.centery = y_center
        x = button_rect.x
        y = button_rect.y
        font = pg.font.SysFont(name=textFont,size=35)
        
        # Text Rect (Button name)
        if enabled:
        # button is enabled by GameStatus.processButtons()
            text = font.render(button, True, black)
            text_rect = text.get_rect(center = button_rect.center)
            
            if x < self.mouse.pos[0] < x + w and y < self.mouse.pos[1] < y + h:
            # mouse is in area of the button
                pg.draw.rect(self.window, color_active, button_rect)
                if self.mouse.click:
                # only allow to click button, when mouse was activated and button 
                # is enabled by GameState()
                    self.buttonClicked = button
            else:
                pg.draw.rect(self.window, color_inactive, button_rect)
        else:
        # button is disabled by GameStatus.processButtons()
            text = font.render(button, True, color_disabled)
            text_rect = text.get_rect(center = button_rect.center)
            pg.draw.rect(self.window, color_inactive, button_rect)
            
        self.window.blit(text, text_rect)
            
         
    def resBox(self): # Result Box
        # Result Rect
        w = self.buttonArea['elementWidth']
        h = 140
        resBox_rect = pg.Rect((0,310), (w,h)) # Rect((left,top), (width,height))
        # center res_box within buttonArea
        resBox_rect.centerx = self.buttonArea['size'].x / 2        

        # Text Rects
        header_font = pg.font.SysFont(name=textFont, size=25, bold=False)
        score_font  = pg.font.SysFont(name=textFont, size=20, bold=False)
        bal_font    = pg.font.SysFont(name=textFont, size=30, bold=False)
        res_font    = pg.font.SysFont(name=textFont, size=20, bold=True)
        dist = 10 # distance between elements
        # left x coord. of left sided text rects
        left_x  = resBox_rect.left  + dist
        # right x coord. of right sided text rects
        right_x = resBox_rect.right - dist
        y       = resBox_rect.top   + dist # y coord. of text rects
        
         ## Header
         ### "SCORE"
        score_text = header_font.render("SCORE", True, black)
        score_rect = score_text.get_rect(x = left_x,
                                         y = y)
        
         ### "BALANCE"
        balHeader_text = header_font.render("BALANCE", True, black)
        balHeader_rect = balHeader_text.get_rect(right = right_x,
                                                 y = y)
        
         ## balance
        bal      = str(self.state.balance)
        bal_text = bal_font.render(bal, True, black)
        # redefine y pos. as bottom of score_rect + 1.25x line distance
        y = score_rect.bottom + (dist * 1.25)
        bal_rect = bal_text.get_rect(right = right_x,
                                     y = y) 
         ## Player Result
        playerScore = "Player: " + str(self.state.playerScore)
        player_text = score_font.render(playerScore, True, black)
        player_rect = player_text.get_rect(x = left_x,
                                           y = y)
         ## Dealer Result
        dealerScore = "Dealer: " + str(self.state.dealerScore)
        dealer_text = score_font.render(dealerScore, True, black)
        # redefine y pos. as bottom of player_rect + line distance
        y = player_rect.bottom + dist
        dealer_rect  = dealer_text.get_rect(x = left_x,
                                            y = y)
        
        ## Result line
        res_color = black
        if self.state.gameState in ["new game","play"]:
            Result = ""
        elif self.state.gameState == "bet":
            Result = "Place your bet."
        elif self.state.gameState == "game over":
            if self.state.result == "broke":
                Result = "You are broke."
            elif self.state.result == "empty":
                Result = "Cards are out."
        elif self.state.gameState == "result":
            # Round results
            if self.state.result == 0:
                Result = "Dealer wins!"
                res_color = (204,0,0) # red
            elif self.state.result == 1:
                Result = "You win!  +" + str(2*self.state.bet)
                res_color = (0,204,102) # green
            elif self.state.result == 2:
                Result = "Draw!  +" + str(self.state.bet)
                res_color = (0,204,204) # blue
            elif self.state.result == 3:
                Result = "BLACK JACK!  +" + str(2*self.state.bet)
                res_color = (0,204,102) # green

                
        res_text  = res_font.render(Result, True, res_color)
        # redefine y pos. as bottom of dealer_rect + 1.25x line distance
        y = dealer_rect.bottom + (dist * 1.25)
        res_rect  = res_text.get_rect(x = left_x,
                                      y = y)
        
        # draw
        pg.draw.rect(self.window, color_resultsBox, resBox_rect) # yellow Rect
        pg.draw.rect(self.window, res_color, resBox_rect, 1)     # black Border
        # left sided
        self.window.blit(score_text,  score_rect)  # "SCORE" Header
        self.window.blit(player_text, player_rect) # Player Results Text
        self.window.blit(dealer_text, dealer_rect) # Dealer Results Text
        self.window.blit(res_text,    res_rect)    # Round Result
        # right sided
        self.window.blit(balHeader_text, balHeader_rect) # "BALANCE" Header
        self.window.blit(bal_text      , bal_rect)       # current balance
    
    def betBox(self):
        # Bet Rect
        w = self.buttonArea['elementWidth']
        h = 45
        box_rect = pg.Rect((0,455), (w,h)) # Rect((left,top), (width,height))
        # center res_box within buttonArea
        box_rect.centerx = self.buttonArea['size'].x / 2

        # Text Rect
        if self.state.gameState == "bet":
            if not self.bet_input: # waiting for player keyboard input
                font = pg.font.SysFont(name=textFont, size=20, bold=False, italic=True)
                text = font.render("Type", True, color_resultsBoxFont)
            else: # displaying player keayboard input
                font = pg.font.SysFont(name=textFont, size=25, bold=False)
                text = font.render(self.bet_input, True, black)
                y = box_rect.y + 10
        elif self.state.gameState == "game over":
            font = pg.font.SysFont(name=textFont, size=25, bold=True)
            text = font.render("GAME OVER", True, black)
        elif self.state.gameState in ["play","result"]:
            font = pg.font.SysFont(name=textFont, size=25, bold=True)
            bet = str(self.state.bet)
            text = font.render(bet, True, color_resultsBoxFont) 
        elif self.state.gameState in ["new game"]:
            font = pg.font.SysFont(name=textFont, size=25, bold=True)
            text = font.render("", True, color_resultsBoxFont) 

            
        text_rect = text.get_rect(centerx = box_rect.centerx,
                                  centery = box_rect.centery)
        pg.draw.rect(self.window, color_resultsBox, box_rect)
        pg.draw.rect(self.window, black, box_rect, 1) # black Border
        self.window.blit(text, text_rect)
        
    def render(self):
        # Background (table)
        self.window.fill(window_color)
        
        # Button Area
        pg.draw.rect(self.window, 
                     buttonArea_color, 
                     pg.Rect(self.buttonArea['pos'], 
                             self.buttonArea['size']
                             )
        )
        
        # Buttons
        self.button("Shuffle Deck",
                    50,
                    60,
                    self.state.shuffle_ac) 
        self.button("Deal", 
                    140,
                    50,
                    self.state.deal_ac)
        self.button("Hit", 
                    200,
                    50,
                    self.state.draw_ac)
        self.button("Stand",
                    260,
                    50,
                    self.state.stand_ac)
        self.button("QUIT",
                    550,
                    60,
                    True)
            
        # Result Box
        self.resBox()
        
        # Bet Box
        self.betBox()
        
        # Cards
        if self.state.clear_table:
            self.state.clear_table = False
        else:
            self.showCards("player")
            self.showCards("dealer")
        
        # update display
        pg.display.update()
        
    ###########    Render functions end    ###########
        
    def update(self):
        self.state.update(self.buttonClicked, self.bet_input)
        self.buttonClicked = None # reset after button was processed
        if self.state.bet != None:
        # reset keyboard input when bet was approved by player
            self.bet_input = ""

        
    def run(self):
        while self.state.running:
        # turned False eigther in self.processInput() or 
        # in GameState.processButtons()
            self.process_input()
            self.update()
            self.render()
            self.clock.tick(FPS)
        pg.quit()
            

userInterface = Interface()
userInterface.run()