#
# Model
#
import random

cardseq = 'A23456789XJQK'

def cardOrd( c):
    return cardseq.index( c)


# H = Harts D = Diamonds P = Pikes  F = Flowers
seedseq = 'HPDF'  #define the four seeds

def seedOrd( s):
    return seedseq.index( s)

class card( object):
    # internal representation of a card uses two chars

    def __init__( self, c, s):  #initialize with 2 integers
        self.c = cardseq[ c]
        self.s = seedseq[ s]

    def isRed( self):
        return self.s in 'HD'   # hearts and diamonds are red

    def isNext( self, card):    # check if a card is the next in sequence
        return (cardOrd( self.c) == cardOrd( card.c)-1)

rows = map( lambda x:[], xrange( 7))    # all rows are empty lists
hidden = map( lambda x:0, xrange( 7))   # define all cards as uncovered
savedStack = []
countSteps = 0

# init the stack
def init():
    global stack, basket, tops, rows, hidden

    stack = []                  # the stack of cards
    basket = []                 # the basket collecting discarded cards
    tops = [[], [], [], []]     # the four tops (one per type)
    rows[:] = [[], [], [], [], [], [], []]
    hidden[:] = [ 0, 0, 0, 0, 0, 0, 0]

    # define the stack as a list of cards (tuples)
    for n in xrange( 13):
      for s in xrange( 4):
        stack.append( card( n, s))


def shuffle():
    global savedStack

    # shuffle
    random.shuffle( stack)
    savedStack = stack[:]   # make a copy for later use in restart


# deal cards
def deal():
    # distribute as a diagonal
    for j in xrange( 7):
        hidden[j] = j
        for i in xrange( 7-j):
            rows[ 6-i].append( stack.pop())


# testing deal, to verify special termination conditions and auto mode
def test_deal():
    global stack, basket, tops, hidden

    # all cards uncovered ready for auto
    for j in xrange( 7):
        hidden[j] = 0
        rows[ j] = []

    # 4 tops loaded up to the 10s
    for s in xrange( 4):
        for n in xrange(10):
            tops[s].append( card( n, s))

    # stack contains 0 cards
    stack = []
    # basket is empty
    basket = [ card( 12, 0)]

    # four rows are loaded
    rows[0] = [ card(11, 1), card(10, 0)]
    rows[1] = [ card( 12, 1), card(11, 0), card(10, 1)]
    rows[2] = [ card( 12, 2), card(11, 3), card(10, 2)]
    rows[3] = [ card( 12, 3), card(11, 2), card(10, 3)]


def restart():
    global stack
    init()
    stack = savedStack[:]
    deal()


# check if card/tail compatible with destination row
def checkRowCard( row, card):
    if not rows[row]:                   # empty row
        return ( card.c == 'K')         # can only take Kings

    else:                               # non empty row
        r = rows[ row][-1]
        # ensure that the seed is alternate RED/Black
        if r.isRed() == card.isRed(): return False

        # and the card is sequential
        return  card.isNext( r)


# see if any new card has been uncovered (in a row)
def checkHidden( source):
    length = len( rows[ source])
    # if the last card in a row is hidden
    if length > 0 and hidden[ source] > length-1:
        hidden[ source] = length-1     # uncover it
        return True
        #print "source %d, hidden %d, len %d" % (source, hidden[source], len(rows[source]))
    else:
        return False


def rowHide( row):
    hidden[ row] += 1


def countHidden():
    # count all the hidden cards left
    count = sum( hidden)

    # including those in the basket
    if basket:
        return count + len( stack) + len( basket) -1
    else:
        return count + len( stack)


def checkFinished():
    # verify that all rows are empty
    for i in xrange( 7):
        if rows[i]:
            return False

    # verify that stack and basket are empty
    if stack or basket:
        return False
    else:
        return True


# move a card to a row (automatic)
def matchRow( card):
    # find if the top of stack is compatible with any of the rows
    for row in xrange(7):
        if checkRowCard( row, card):  #
            # move the card or tail as appropriate
            return row
    return -1   # no match


def matchTop( card):
    global tops

    # find which top it belongs
    top = seedOrd( card.s)
    # aces go first
    if card.c == 'A':
        return top

        # sequential cards follow
    elif tops[top] and tops[top][-1].isNext( card):
        return top
    return -1   # no match


# refill the stack from the basket
def refillStack():
    global stack, basket
    stack = basket[:]
    stack.reverse()
    basket = []


# undo refill the stack from the basket
def unrefillStack():
    global stack, basket
    basket = stack[:]
    basket.reverse()
    stack = []


def moveTo( dest, index, card):
    if dest == 't':     #top
        tops[ index].append( card)
    elif dest == 'r':   #row
        rows[ index].append( card)
    elif dest == 'b':   #bascket
        basket.append( card)
    elif dest == 's':   #stack
        stack.append( card)
    

def getCards( source, index, len):
    if source == 't':     #top
        slist = tops[ index]
    elif source == 'r':   #row
        slist= rows[ index]
    elif source == 'b':   #bascket
        slist = basket
    elif source == 's':   #stack
        slist = stack

    cards = []
    for i in xrange(len):
        cards.append( slist.pop())
    return cards


def getTop( top):
    if tops[ top]:
        return tops[ top][-1]
    

def getBasketTip():
    if basket:
        return basket[-1]
    

def getStackTip():
    if stack:
        return stack[-1]
    

def getTip( row):
    if rows[ row]:
        return rows[ row][-1]
    

def getCount():
    return countSteps