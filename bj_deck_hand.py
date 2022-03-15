## Black Jack - GUI version
# Create Deck & Hand Object

from enum import Enum
from typing import NamedTuple
import random
import itertools as itt


class Type(Enum):
    Ace = 1
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7
    Eight = 8
    Nine = 9
    Ten = 10
    Jack = 11
    Queen = 12
    King = 13
    
class Color(Enum):
    D = 1
    C = 2
    H = 3
    S = 4

class Card(NamedTuple):
    type: Type
    color: Color
    

class Deck:
    def __init__(self):
        self.cards = []
        self.build()
        self.shuffle()
        
    def build(self):
        for type in Type:
            for color in Color:
                self.cards.append(Card(type,color))
                
    def shuffle(self):
        random.shuffle(self.cards)
                  
    def draw_card(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        
        
class Hand():
    def __init__(self):
        self.cards = []
        self.value = 0
        
    def add_card(self, card):
        self.cards.append(card)
        
    def calc_hand(self):
        for card in self.cards:
            if card.type.name in {'Jack','Queen','King'}:
                self.value += 10
            elif card.type.name in 'Ace':
                if self.value < 11:
                    self.value += 11
                else:
                    self.value += 1
            else:
                self.value += card.type.value