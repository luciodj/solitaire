#
# Model
#
import random

ranks = 'A23456789XJQK' # internal representation of a card uses three chars: rank, suit, face
suits = 'HSDC'          # define the four suits:  H = Hearts D = Diamonds S = Spades  C = Clubs

class Card( object):
    def __init__( self, rank, suit):  #initialize with 2 integers
        self.rank = ranks[ rank]
        self.suit = suits[ suit]
        self.face = 'U'     # face up by default

    def __repr__( self):
        return '%s, %s, %s' % (self.rank, self.suit, self.face)

    def isRed( self):
        return self.suit in 'HD'   # hearts and diamonds are red

    def precedes( self, card):    # check if self.precedes( card) in rank
        return ranks.index( self.rank) == ( ranks.index( card.rank)-1)

    def matchFoundation( self):
        'find if the card is compatible with any of the foundations'
        suit = suits.index( self.suit)
        foundation = foundations[ suit]
        if foundation.takesCard( self):
            return foundation
        else:
            return None   # no match

    def matchPile( self):
        'find if the card on deck is compatible with any of the piles'
        for pile in piles:
            if pile.takesCard( self):  
                return pile
        return None   # no match


class Stack( object):
    def __init__(self, name, cards, xy):
        self.name = name
        self.cards = cards
        self.xy = xy

    def top( self):
        return self.cards[-1]

    def coords( self):
        if not self.cards:      # if stack is empty 
            return ( self.xy)
        else:
            return (self.cards[-1].rect.x, self.cards[-1].rect.y)   

    def takesCard( self, card):
        'check if card/tail compatible with destination stack'
        if self.name == 'pile':
            if not(self.cards):                 # empty pile
                return ( card.rank == 'K')      # can only take Kings
            else:                               # non empty 
                top = self.top()
                # ensure that the seed is alternate RED/Black
                if top.isRed() == card.isRed(): 
                    return False
                # and the card is sequential
                return  card.precedes( top)
        else:    # foundation
            if not( self.cards):                # empty foundation 
                return( card.rank == 'A')       # can only take Aces
            else:                               # non empty 
                top = self.cards[-1]
                return top.precedes( card)

savedDeck = []
countSteps = 0

# init the deck
def init():
    global deck, waste, foundations, piles

    deck = Stack( 'deck', [], (0,0))
    waste = Stack( 'waste', [], (0,0))
    foundations = map( lambda x: Stack('foundation', [], (0,0)), xrange( 4))
    piles = map( lambda x: Stack('pile', [], (0,0)), xrange( 7))    # all piles are empty lists

    # define the deck as a list of cards
    for n in xrange( 13):
      for s in xrange( 4):
        deck.cards.append( Card( rank = n, suit = s))

def shuffle( ):
    global savedDeck
    # shuffle
    random.shuffle( deck.cards)
    savedDeck = deck.cards[:]   # make a copy for later use in restart

# deal cards
def deal():
    # distribute in a diagonal pattern 1, 2, 3, 4, 5, 6, 7
    for h in xrange( 6):
        for i in xrange( 6-h):
            card = deck.cards.pop()
            card.face = 'D'      
            piles[ 6-i].cards.append( card)
        card = deck.cards.pop()
        card.face = 'U'
        piles[h].cards.append( card)
    card = deck.cards.pop()
    card.face = 'U'
    piles[6].cards.append( card)

def restart():
    global deck
    init()
    deck.cards = savedDeck[:]
    deal()

def countHidden():
    'count all the hidden cards left'
    count = 0
    for pile in piles:
        for card in pile.cards:
            if card.face == 'D':
                count += 1 
    # including those in the waste
    if waste:
        return count + len( deck.cards) + len( waste.cards) -1
    else:
        return count + len( deck.cards)

def checkFinished():
    'verify that all piles are empty'
    for pile in piles:
        if pile.cards:
            return False
    # verify that deck and waste are empty too
    return not( deck.cards or waste.cards)

# recycle the deck from the waste
def recycle():
    if waste.cards:
        deck.cards = waste.cards[:]
        deck.cards.reverse()
        waste.cards = []

# undo recycle 
def undoRecycle():
    waste.cards = deck.cards[:]
    waste.cards.reverse()
    deck.cards = []
    
def getCardsFrom( source, index):
    tail = source.cards[index:]
    del source.cards[index:]
    return tail    

def getCount():
    return countSteps
