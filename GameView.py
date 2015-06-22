#
# Solitaire Game View
#
import pygame
import sys
import Model as m
from collections import namedtuple

GREEN = ( 0, 128, 0)
BLACK = ( 0, 0, 0)
WHITE = ( 255, 255, 255)
YELLOW = ( 245, 200, 10)
RED   = ( 255, 0, 0)
BLUE  = ( 0, 0, 255)
LIGHTGRAY = ( 128, 128, 128)
DARKGRAY  = ( 64, 64, 64)

# parameterized display
BRADIUS = 7
pad = 8
card_w = 100
card_h = 145
cardtop_h = 35
backtop_h = 35

XMax, YMax = 9*card_w, card_h*2 + backtop_h*6 + cardtop_h*12
foundations_space = 20
foundations_left = ( XMax-(4*card_w)-(4*foundations_space))/2
foundations_y = 10
rows_space = 5
rows_left = 10
rows_y = foundations_y + card_h + 2*rows_space
deck_x = XMax - card_w - foundations_space
deck_y = foundations_y
waste_x = deck_x
waste_y = rows_y

_screen = None
_clock = None

class Log( object):
    def __init__( self):
        self.list=[]

    def append( self, actionTuple):
        self.list.append( actionTuple)

    def pop( self):
        return self.list.pop()

    def clear( self):
        self.list = []

log = Log()

Rectangle = namedtuple('Rectangle', 'x y x1 y1')
def contains( self, x, y):
    return ( x > self.x) and ( x < self.x1) and ( y > self.y) and ( y < self.y1)
Rectangle.contains = contains

Touch = namedtuple( 'Touch', 'source index')

class Button( object):
    def __init__( self, img, rect):
        self.img = img
        self.rect = rect
        
def checkTouch( x, y):
    'identify the object touched'
    for i, foundation in enumerate( m.foundations):
        if foundation.cards:
            if foundation.top().rect.contains( x, y):
                return Touch( source=foundation, index=-1)
    # note the deck is always clickable (even when empty!)
    if Rectangle(deck_x, deck_y, deck_x+card_w, deck_y+card_h).contains( x, y):
        return Touch( source=m.deck, index=-1)
    if m.waste.cards:
        if m.waste.top().rect.contains( x, y):
            return Touch( source=m.waste, index=-1)
    for pile in m.piles:
        if pile.cards:
            for i, card in enumerate( pile.cards):
                if card.rect.contains( x, y):
                    return Touch( source=pile, index=i)  
    for i, button in enumerate( buttons.cards):
        if button.rect.contains( x, y):
            return Touch( source=buttons, index=i)  
    return None

def touchWaste():
    if m.waste.cards:
        return Touch( source=m.waste, index=-1)

def touchDeck():
    return Touch( source=m.deck, index=-1)

def touchButton( index):
    return Touch( buttons, index)

def touchPile( pile):
    return Touch( pile, index=-1)

class Animation( object):
    first = 5           # default number of steps
    speed = 40          # defautl animation speed

    def __init__( self):
        self.steps = 0          # animation steps counter
        self.dest = []          # target list for card(s) at the end of animation
        self.cards = []         # list of card(s) 'in motion'
        self.currentXY = (0,0)  # animation current position

    def set( self, dest, cards):
        self.steps = self.first
        self.dest = dest
        self.cards = cards

    def inMotion( self):
        return (self.steps > 0)

    def lastStep( self):
        return (self.steps == 1)  

    def sourceCoords( self):
        return ( self.cards[0].rect.x, self.cards[0].rect.y)

animation = Animation()

def drawEmptyStack( stack, x, y):
    pygame.draw.rect( _screen, LIGHTGRAY, (x, y, card_w, card_h), 2)
    stack.xy = (x, y)

def drawTopBevel( _color, left, top, w, h, r):
    right = left + w
    bottom = top + h
    pygame.draw.circle( _screen, _color, (left+r,  top+r), r, 0)
    pygame.draw.circle( _screen, _color, (right-r, top+r), r, 0)
    pygame.draw.rect  ( _screen, _color, (left, top+r, w, h), 0)
    pygame.draw.rect  ( _screen, _color, (left+r, top, w-r-r , r), 0)

def drawBottomBevel( _color, left, top, w, h, r):
    right = left + w
    bottom = top + h
    pygame.draw.circle( _screen, _color, (left+r,  bottom-r), r, 0)
    pygame.draw.circle( _screen, _color, (right-r, bottom-r), r, 0)
    pygame.draw.rect  ( _screen, _color, (left, top, w, h-r), 0)
    pygame.draw.rect  ( _screen, _color, (left+r, top+h-r, w-r-r , r), 0)

def drawTopCard( card, x, y):
    # draw card white background
    drawTopBevel( WHITE, x, y, card_w, cardtop_h, BRADIUS)
    # separator
    pygame.draw.line( _screen, LIGHTGRAY, ( x+4, y), ( x+card_w-4, y), 1)
    # rank
    value = card.rank if card.rank != "X" else "10"
    img = _font.render( value, 1, (BLACK,RED)[ card.isRed()])
    _screen.blit( img, (x+pad, y+pad))
    # suit
    sfc = suitsImages[ m.suits.index( card.suit)]
    _screen.blit( sfc, ( x+card_w-sfc.get_height()-pad, y+pad))
    #annotate card area
    card.rect = Rectangle( x, y, x+card_w, y+cardtop_h)

def drawFullCard( card, x, y):
    # draw top
    drawTopCard( card, x, y)
    # draw full size bevel
    drawBottomBevel( WHITE, x, y+cardtop_h, card_w, card_h-cardtop_h, BRADIUS)
    # add the larger image
    if m.ranks.index( card.rank) <= m.ranks.index( "X"):
        # draw a big seed
        sfc = bigSuitsImages[ m.suits.index( card.suit)]
    else:
       # draw the figure
        sfc = figureImages[ ( m.ranks.index( card.rank) 
                            - m.ranks.index( "J"))*4 + m.suits.index( card.suit)]
    _screen.blit( sfc, (x+2, y +card_h -sfc.get_height()-2),
                        (0, 0, card_w-4, card_h-6))
    #annotate card area
    card.rect = Rectangle( x, y, x+card_w, y+card_h)

def drawCardBack( card, x, y):
    drawTopBevel( WHITE, x, y, card_w, cardtop_h, BRADIUS)
    drawBottomBevel( WHITE, x, y+cardtop_h, card_w, card_h-cardtop_h, BRADIUS)
    _screen.blit( backImage, (x+2, y+2), (0, 0, card_w-4, card_h-4))
    #annotate card area
    card.rect = Rectangle( x, y, x+card_w, y+card_h)

def drawTopCardBack( card, x, y):
    drawTopBevel( WHITE, x, y, card_w, cardtop_h, BRADIUS)
    _screen.blit( backImage, (x+2, y+2),(0, 0, card_w-4, backtop_h))
    #annotate card area
    card.rect = Rectangle( x, y, x+card_w, y+cardtop_h)

def drawPile( pile, x, y):
    for card in pile.cards:
        if ( card == pile.top()):
            if card.face != 'U':    # ensure top cards are always face up
                card.face = 'U'     # turn card up
                log.append( ('turn', pile))
            drawFullCard( card, x, y)
        else: # visible
            if card.face == 'D':
                drawTopCardBack( card, x, y)
            else:
                drawTopCard( card, x, y)
        y += cardtop_h
        # count +=1

def display( ):
    'displays current game board'
    global buttons

    # 0. paint the background
    _screen.fill( GREEN)

    # 1. draw the four foundations
    x = foundations_left
    y = foundations_y
    for foundation in m.foundations:
        if foundation.cards:
            drawFullCard( foundation.top(), x, y)
        else:
            # leave empty space
            drawEmptyStack( foundation, x, y)
        x += card_w + foundations_space

    # 2. draw the deck and the waste
    if m.deck.cards:
        drawCardBack( m.deck.top(), deck_x, deck_y)
    else:
        # draw empty space
        drawEmptyStack( m.deck, deck_x, deck_y)

    # 3. draw the waste
    if m.waste.cards:
        drawFullCard( m.waste.top(), waste_x , waste_y)
    else:
        # draw empty space
        drawEmptyStack( m.waste, waste_x, waste_y)

    # 4. draw the 7 piles
    x = rows_left    
    for pile in m.piles:
        # count = 0
        y = rows_y
        if not pile.cards:      # in case pile is empty
            drawEmptyStack( pile, x, y)
        else: 
            drawPile( pile, x, y)
        x +=  card_w + rows_space

    # 4.bis add card in animation
    if animation.steps == animation.first:
        # find the source and destination coordinates
        dx, dy = animation.dest.coords()
        if animation.dest.name == 'pile' and animation.dest.cards:
            dy += cardtop_h
        sx, sy = animation.sourceCoords()
        # calculate the speed
        animation.speed_x = (dx-sx) / (animation.first)
        animation.speed_y = (dy-sy) / (animation.first)
        animation.currentXY = ( sx, sy)
    
    if animation.steps > 0:   
        # advance position
        x, y = animation.currentXY
        x += animation.speed_x
        y += animation.speed_y
        animation.currentXY = ( x, y)
        for card in animation.cards[:-1]:           # draw first cards (partially covered)
            drawTopCard( card, x, y)
            y += cardtop_h
        drawFullCard( animation.cards[-1], x, y)    # draw last card in full
        animation.steps -= 1  

    # 5. status updates
    x, y = XMax -120, waste_y + card_h + 20

    # 6. add step counter
    text = "Move: %d" % m.getCount()
    img = _font.render( text, 1, WHITE)
    _screen.blit( img, (x, y))
    y += 20

    # 7. add buttons
    buttons = m.Stack('button', [], ( x, y))
    for img in buttonImages:
        _screen.blit( img, (x, y))
        buttons.cards.append( Button( img, Rectangle( x, y, x+100, y+100)))
        y += 80

def selectBox( optionsList):
    ' model box selection menu'
    options = []
    for option in optionsList:
        options.append( Button( _font.render( option, 1, WHITE), Rectangle(0,0,0,0)))

    width = max( map( lambda(x): x.img.get_width(), options))+2
    height = max( map( lambda(x): x.img.get_height(), options))+2

    # draw a (centered) box capable of containing all the strings
    x = (XMax - width -10)/2
    y = (YMax - height* len( options) - 10)/2
    pygame.draw.rect( _screen, LIGHTGRAY, (x, y, width+10, height*len( options)+10), 0)

    # draw each string in a box and record the rectangle
    x += 5
    y += 5
    for i, option in enumerate( options):
        # the first line of text is the title so it does not get a dark bkgnd
        if i>0:
            pygame.draw.rect( _screen, DARKGRAY, ( x, y, width, height), 0)
            option.rect = Rectangle(x, y, x+width, y+height)
        _screen.blit( option.img, (x+1, y+1))
        y += height

    # now wait for user input (modal)
    while True:
        wait( 5)
        touch = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                for index, option in enumerate( options):
                    if option.rect.contains( x, y):
                        return index-1   # ignore the title

def wait( rate):
    _clock.tick( rate)
    pygame.display.flip()

def initView():
    global _clock, _screen, _font, XMax, YMax
    global figureImages, suitsImages, bigSuitsImages, backImage, buttonImages
    pygame.init()
    pygame.display.set_caption( "PySolitaire")
    _clock = pygame.time.Clock()
    _font = pygame.font.Font( None, 32)
    _screen = pygame.display.set_mode( (XMax, YMax))
    figureImages = []
    figureImages.append( pygame.image.load("images/jh.png"))
    figureImages.append( pygame.image.load("images/jp.png"))
    figureImages.append( pygame.image.load("images/jd.png"))
    figureImages.append( pygame.image.load("images/jf.png"))
    figureImages.append( pygame.image.load("images/qh.png"))
    figureImages.append( pygame.image.load("images/qp.png"))
    figureImages.append( pygame.image.load("images/qd.png"))
    figureImages.append( pygame.image.load("images/qf.png"))
    figureImages.append( pygame.image.load("images/kh.png"))
    figureImages.append( pygame.image.load("images/kp.png"))
    figureImages.append( pygame.image.load("images/kd.png"))
    figureImages.append( pygame.image.load("images/kf.png"))
    suitsImages = []
    suitsImages.append( pygame.image.load("images/hearts.png"))
    suitsImages.append( pygame.image.load("images/spades.png"))
    suitsImages.append( pygame.image.load("images/diamonds.png"))
    suitsImages.append( pygame.image.load("images/clubs.png"))
    bigSuitsImages = []
    bigSuitsImages.append( pygame.image.load("images/bigheart.png"))
    bigSuitsImages.append( pygame.image.load("images/bigspade.png"))
    bigSuitsImages.append( pygame.image.load("images/bigdiamond.png"))
    bigSuitsImages.append( pygame.image.load("images/bigclub.png"))
    backImage = pygame.image.load( "images/RedBack.png")
    buttonImages = []
    buttonImages.append( pygame.image.load( "images/undo.png"))
    buttonImages.append( pygame.image.load( "images/restart.png"))
    buttonImages.append( pygame.image.load( "images/new.png"))
