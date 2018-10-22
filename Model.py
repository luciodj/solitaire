'''
    Model for game of solitaire
'''
import random

RANKS = 'A23456789XJQK' # internal representation of a card uses three chars: rank, suit, face
SUITS = 'HSDC'          # define the four suits:  H = Hearts D = Diamonds S = Spades  C = Clubs

class Card(object):
    'models a card'
    def __init__(self, rank, suit):  #initialize with 2 integers
        self.rank = RANKS[rank]
        self.suit = SUITS[suit]
        self.face = 'U'     # face up by default

    def __repr__(self):
        return '%s, %s, %s' % (self.rank, self.suit, self.face)

    def is_red(self):
        'hearts and diamonds are red'
        return self.suit in 'HD'

    def precedes(self, card):
        'check if self.precedes(card) in rank'
        return RANKS.index(self.rank) == (RANKS.index(card.rank)-1)

    def match_foundation(self):
        'find if the card is compatible with any of the foundations'
        suit = SUITS.index(self.suit)
        foundation = FOUNDATIONS[suit]
        if foundation.takes_card(self):
            return foundation
        else:
            return None   # no match

    def match_pile(self):
        'find if the card on deck is compatible with any of the piles'
        for pile in PILES:
            if pile.takes_card(self):
                return pile
        return None   # no match


class Stack(object):
    'models a stack of cards'
    def __init__(self, name):
        self.name = name
        self.cards = []
        self.xy = (0, 0)

    def top(self):
        'return top of stack'
        return self.cards[-1]

    def coords(self):
        'return coordinates of stack of cards'
        if not self.cards:      # if stack is empty
            return self.xy
        else:
            return (self.cards[-1].rect[0], self.cards[-1].rect[1])

    def set_coords(self, coords):
        'assign new coordinates to stack'
        self.xy = coords
        
    def takes_card(self, card):
        'check if card/tail compatible with destination stack'
        if self.name == 'pile':
            if not self.cards:                  # empty pile
                return card.rank == 'K'         # can only take Kings
            else:                               # non empty
                top = self.top()
                # ensure that the seed is alternate RED/Black
                if top.is_red() == card.is_red():
                    return False
                # and the card is sequential
                return  card.precedes(top)
        else:    # foundation
            if not self.cards:                  # empty foundation
                return card.rank == 'A'         # can only take Aces
            else:                               # non empty
                top = self.cards[-1]
                return top.precedes(card)

savedDeck = []
countSteps = 0
DECK = []
WASTE = []
FOUNDATIONS = []
PILES = []

def init():
    'define the deck as a list of cards'
    global DECK, WASTE, FOUNDATIONS, PILES
    DECK = Stack('deck')
    WASTE = Stack('waste')
    # foundations = map(lambda x: Stack('foundation', [], (0, 0)), range(4))
    FOUNDATIONS = [Stack('foundation')  for x in range(4)]
    # piles = map(lambda x: Stack('pile', [], (0, 0)), range(7))    # all piles are empty lists
    PILES = [Stack('pile') for x in range(7)]
    for rank in range(13):
        for suit in range(4):
            DECK.cards.append(Card(rank=rank, suit=suit))

def shuffle():
    'shuffle deck to deal a new game'
    global savedDeck
    random.shuffle(DECK.cards)
    savedDeck = DECK.cards[:]   # make a copy for later use in restart

# deal cards
def deal():
    'distribute in a diagonal pattern 1, 2, 3, 4, 5, 6, 7'
    for pile in range(6):
        for length in range(6-pile):
            card = DECK.cards.pop()
            card.face = 'D'
            PILES[6-length].cards.append(card)
        card = DECK.cards.pop()
        card.face = 'U'
        PILES[pile].cards.append(card)
    card = DECK.cards.pop()
    card.face = 'U'
    PILES[6].cards.append(card)

def restart():
    'restart game'
    init()
    DECK.cards = savedDeck[:]
    deal()

def count_hidden():
    'count all the hidden cards left'
    count = 0
    for pile in PILES:
        for card in pile.cards:
            if card.face == 'D':
                count += 1
    # including those in the waste
    if WASTE:
        return count + len(DECK.cards) + len(WASTE.cards) -1
    else:
        return count + len(DECK.cards)

def check_finished():
    'verify that all piles are empty'
    for pile in PILES:
        if pile.cards:
            return False
    # verify that deck and waste are empty too
    return not(DECK.cards or WASTE.cards)

def recycle():
    'recycle the deck from the waste'
    if WASTE.cards:
        DECK.cards = WASTE.cards[:]
        DECK.cards.reverse()
        WASTE.cards = []

def undo_recycle():
    'undo recycle'
    WASTE.cards = DECK.cards[:]
    WASTE.cards.reverse()
    DECK.cards = []

def get_cards_from(source, index):
    'remove cards from a pile'
    tail = source.cards[index:]
    del source.cards[index:]
    return tail

def get_count():
    'pass the current value of the step counter'
    return countSteps
