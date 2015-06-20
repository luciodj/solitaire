#
# Solitaire Game View
#
import pygame
import sys
from Model import *

GREEN = ( 0, 128, 0)
BLACK = ( 0, 0, 0)
WHITE = ( 255, 255, 255)
YELLOW = ( 245, 200, 10)
RED   = ( 255, 0, 0)
BLUE  = ( 0, 0, 255)
LIGHTGRAY = ( 128, 128, 128)
DARKGRAY  = ( 64, 64, 64)

# parameterized display
pad = 8
card_w = 100
card_h = 145
cardtop_h = 35
backtop_h = 10
XMax, YMax = 9*card_w, card_h*2 + backtop_h*6 + cardtop_h*12

tops_space = 10
tops_left = ( XMax-(4*card_w)-(4*tops_space))/2
tops_y = 10
rows_space = 5
rows_left = 10
rows_y = tops_y + card_h + 2*rows_space
stack_x = XMax - card_w - tops_space
stack_y = tops_y
basket_x = stack_x
basket_y = rows_y

_screen = None
_clock = None

def printEmptyCard( x, y):
    pygame.draw.rect( _screen, LIGHTGRAY, (x, y, card_w, card_h), 1)


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


def printTopCard( c, x, y):
    # draw card white background
    #pygame.draw.rect( _screen, WHITE, (x, y, card_w, cardtop_h), 0)
    drawTopBevel( WHITE, x, y, card_w, cardtop_h, 4)

    # separator
    pygame.draw.line( _screen, LIGHTGRAY, ( x+4, y), ( x+card_w-4, y), 1)

    # value
    value = c.c if c.c != "X" else "10"
    img = _font.render( value, 1, (BLACK,RED)[ c.isRed()])
    _screen.blit( img, (x+pad, y+pad))

    # Seed
    sfc = SeedImages[ seedOrd( c.s)]
    _screen.blit( sfc, ( x+card_w-sfc.get_height()-pad, y+pad))



def printFullCard( c, x, y):
    # print top
    printTopCard( c, x, y)

    # draw card white background
    #pygame.draw.rect( _screen, WHITE, (x, y +cardtop_h, card_w, card_h-cardtop_h), 0)
    # draw full size bevel
    drawBottomBevel( WHITE, x, y+cardtop_h, card_w, card_h-cardtop_h, 4)


    # add the larger image
    if cardOrd( c.c) <= cardOrd( "X"):
        # print a big seed
        sfc = SeedImages[ seedOrd( c.s)+4]
    else:
       # print the figure
        sfc = FigureImages[ ( cardOrd( c.c)-cardOrd( "J"))*4 + seedOrd( c.s)]

    _screen.blit( sfc, (x+2, y +card_h -sfc.get_height()-2),
                        (0, 0, card_w-4, card_h-6))


def printCardBack( x, y):
    drawTopBevel( WHITE, x, y, card_w, cardtop_h, 4)
    drawBottomBevel( WHITE, x, y+cardtop_h, card_w, card_h-cardtop_h, 4)
    _screen.blit( BackImage, (x+2, y+2), (0, 0, card_w-4, card_h-4))


def printTopCardBack( x, y):
    drawTopBevel( WHITE, x, y, card_w, cardtop_h, 4)
    _screen.blit( BackImage, (x+2, y+2),(0, 0, card_w-4, backtop_h))


def display( ):
    # displays current game board
    # creates a list of rects for touch and animate
    global RectList, topXY, tipXY

    RectList = []
    topXY = []
    tipXY = []

    # paint the background
    _screen.fill( GREEN)

    # 1. print the four tops
    x = tops_left
    for i in xrange( 4):
        topXY.append( (x, tops_y))  # record coordinates
        if getTop( i):
            printFullCard( getTop( i), x, tops_y)
            RectList.append( ( "top", i, ( x, tops_y, card_w, card_h)))
        else:
            #place a hole
            printEmptyCard( x,  tops_y)

        x += card_w +tops_space


    # 2. print the stack and the basket
    st = getStackTip()
    if st:
        printCardBack( stack_x, stack_y)
    else:
        # leave a hole
        printEmptyCard( stack_x, stack_y)
    # always click-able
    RectList.append( ( "stack", 0, ( stack_x, stack_y, card_w, card_h)))

    # 3. print the basket
    bt = getBasketTip()
    if bt:
        printFullCard( bt, basket_x , basket_y)
        RectList.append( ( "basket", 0, ( basket_x, basket_y, card_w, card_h)))
    else:
        # empty hole
        printEmptyCard( basket_x, basket_y)

    # 4. print the 7 rows
    for i in xrange( 7):
        x = rows_left + i * ( card_w +rows_space)
        count = 0
        y = rows_y
        # in case row is empty
        if not getTip( i):
            printEmptyCard( x, y)
            tipXY.append( (x, y))

        else: # print each card in the row
            for card in rows[i]:
                if hidden[i] > count:
                    # show back of card
                    #printTopCardBack( x, y)
                    printCardBack( x, y)
                    y += backtop_h
                else: #visible
                    if card == getTip( i):
                        printFullCard( card, x, y)
                        tipXY.append( ( x, y+cardtop_h))  # record tip coordinates
                        RectList.append( ( "tip", i, ( x, y, card_w, card_h)))
                    else:
                        printTopCard( card, x, y)
                        RectList.append( ( "tail", i*16+count, ( x, y, card_w, cardtop_h)))
                    y += cardtop_h
                count +=1

    # status updates
    x, y = XMax -120, basket_y + card_h + 20

    # 5. add hidden counter
    #text = "%d" % countHidden()
    #img = _font.render( text, 1, WHITE)
    #_screen.blit( img, (x, y))
    #y+= 20

    # 6. add step counter
    text = "Move: %d" % getCount()
    img = _font.render( text, 1, WHITE)
    _screen.blit( img, (x, y))
    y += 20

    # 7. add buttons
    for i in xrange( len(ButtonImages)):
        _screen.blit( ButtonImages[ i], (x, y ))
        RectList.append( ( "button", i, ( x, y, 100, 100)))
        y += 80


def checkTouch( coord):
    for r in RectList:
        x, y, w, h = r[2]
        if ((coord[0] > x) and (coord[0]<(x+w))):
            if (( coord[1] > y) and ( coord[1]<(y+h))):
                return (r[0], r[1], r[2][0:2])     # string, index, (x,y)
    return None


def selectBox( textStrings):
    global RectList

    lines = []
    for text in textStrings:
        lines.append( _font.render( text, 1, WHITE))

    width = max( map( lambda(x): x.get_width(), lines))+2
    height = max( map( lambda(x): x.get_height(), lines))+2

    # draw a (centered) box capable of containing all the strings
    x = (XMax - width -10)/2
    y = (YMax - height* len(lines) - 10)/2
    pygame.draw.rect( _screen, LIGHTGRAY, (x, y, width+10, height*len(lines)+10), 0)

    # draw each string in a box and record the rectangle
    Reclist = []
    x += 5
    y += 5
    for i, line in enumerate(lines):
        # the first line of text is the title so it does not get a dark bkgnd
        if i>0:
            pygame.draw.rect( _screen, DARKGRAY, ( x, y, width, height), 0)
            RectList.append( ("Box", i, (x, y, width, height)))
        _screen.blit( line, (x+1, y+1))
        y += height


    # now wait for a choice from teh user (modal)
    while True:
        wait( 5)
        touch = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONUP:
                touch = checkTouch ( pygame.mouse.get_pos())

                if touch:
                    return touch[1]-1   # ignore the title


def loadCards():
    global FigureImages, SeedImages, BackImage, ButtonImages

    FigureImages = []
    FigureImages.append( pygame.image.load("images/jh.png"))
    FigureImages.append( pygame.image.load("images/jp.png"))
    FigureImages.append( pygame.image.load("images/jd.png"))
    FigureImages.append( pygame.image.load("images/jf.png"))
    FigureImages.append( pygame.image.load("images/qh.png"))
    FigureImages.append( pygame.image.load("images/qp.png"))
    FigureImages.append( pygame.image.load("images/qd.png"))
    FigureImages.append( pygame.image.load("images/qf.png"))
    FigureImages.append( pygame.image.load("images/kh.png"))
    FigureImages.append( pygame.image.load("images/kp.png"))
    FigureImages.append( pygame.image.load("images/kd.png"))
    FigureImages.append( pygame.image.load("images/kf.png"))
    SeedImages = []
    SeedImages.append( pygame.image.load("images/heart.png"))
    SeedImages.append( pygame.image.load("images/pike.png"))
    SeedImages.append( pygame.image.load("images/diamond.png"))
    SeedImages.append( pygame.image.load("images/flower.png"))
    SeedImages.append( pygame.image.load("images/bigheart.png"))
    SeedImages.append( pygame.image.load("images/bigpike.png"))
    SeedImages.append( pygame.image.load("images/bigdiamond.png"))
    SeedImages.append( pygame.image.load("images/bigflower.png"))
    BackImage = pygame.image.load( "images/RedBack.png")
    ButtonImages = []
    ButtonImages.append( pygame.image.load( "images/undo.png"))
    ButtonImages.append( pygame.image.load( "images/restart.png"))
    ButtonImages.append( pygame.image.load( "images/kill.png"))



def init():
    global _clock, _screen, _font, XMax, YMax

    pygame.init()
    pygame.display.set_caption( "PySolitaire")
    _clock = pygame.time.Clock()
    _font = pygame.font.Font( None, 32)
    _screen = pygame.display.set_mode( (XMax, YMax))
    loadCards()


def wait( rate):
    _clock.tick( rate)
    pygame.display.flip()
