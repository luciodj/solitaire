'''
    view for Solitaire 
'''
import pygame
import sys
import Model as m
from collections import namedtuple

GREEN = (0, 128, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (245, 200, 10)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHTGRAY = (128, 128, 128)
DARKGRAY = (64, 64, 64)

# parameterized display
BRADIUS = 7
PAD = 8
CARD_W = 100
CARD_H = 145
CARDTOP_H = 35
BACKTOP_H = 35

XMAX, YMAX = 9*CARD_W, CARD_H*2 + BACKTOP_H*6 + CARDTOP_H*12
FOUNDATIONS_SPACE = 20
FOUNDATIONS_LEFT = (XMAX-(4*CARD_W)-(4*FOUNDATIONS_SPACE))//2
FOUNDATIONS_Y = 10
ROWS_SPACE = 5
ROWS_LEFT = 10
ROWS_Y = FOUNDATIONS_Y + CARD_H + 2*ROWS_SPACE
DECK_X = XMAX - CARD_W - FOUNDATIONS_SPACE
DECK_Y = FOUNDATIONS_Y
WASTE_X = DECK_X
WASTE_Y = ROWS_Y

screen = None
clock = None

class Log(object):
    'action log for undo feature'
    def __init__(self):
        self.list = []

    def append(self, action_tuple):
        'add an action to the log queue'
        self.list.append(action_tuple)

    def pop(self):
        'retrieve an action from the log queue'
        return self.list.pop()

    def clear(self):
        'empty the log queue'
        self.list = []

log = Log()

Touch = namedtuple('Touch', 'source index')
Button = namedtuple('Button', 'img, rect')
Rectangle = namedtuple('Rectangle', 'left top right bottom')
def contains(self, coords):
    'adds the ability to check for a point to be contained in the rectangle'
    return (self.left < coords[0] < self.right) and (self.top < coords[1] < self.bottom)
Rectangle.contains = contains


def check_touch(coords):
    'identify the object touched'
    for i, foundation in enumerate(m.FOUNDATIONS):
        if foundation.cards:
            if foundation.top().rect.contains(coords):
                return Touch(source=foundation, index=-1)
    # note the DECK is always clickable (even when empty!)
    if Rectangle(DECK_X, DECK_Y, DECK_X+CARD_W, DECK_Y+CARD_H).contains(coords):
        return Touch(source=m.DECK, index=-1)
    if m.WASTE.cards:
        if m.WASTE.top().rect.contains(coords):
            return Touch(source=m.WASTE, index=-1)
    for pile in m.PILES:
        if pile.cards:
            for i, card in enumerate(pile.cards):
                if card.rect.contains(coords):
                    return Touch(source=pile, index=i)
    for i, button in enumerate(buttons.cards):
        if button.rect.contains(coords):
            return Touch(source=buttons, index=i)
    return None

def touch_waste():
    'produce a touch on the waste bin'
    if m.WASTE.cards:
        return Touch(source=m.WASTE, index=-1)

def touch_deck():
    'produce a touch on the deck'
    return Touch(source=m.DECK, index=-1)

def touch_button(index):
    'produce a touch on one of the'
    return Touch(buttons, index)

def touch_pile(pile):
    'produce a touch on a pile'
    return Touch(pile, index=-1)

class Animation(object):
    'support for animation sequences'
    first = 5           # default number of steps
    speed = 20          # defautl animation speed

    def __init__(self):
        self.speed = Animation.speed
        self.steps = 0          # animation steps counter
        self.dest = []          # target list for card(s) at the end of animation
        self.cards = []         # list of card(s) 'in motion'
        self.current_xy = (0, 0) # animation current position
        self.speed_x = 0
        self.speed_y = 0

    def set(self, dest, cards):
        'create a new animation sequence'
        self.steps = self.first
        self.dest = dest
        self.cards = cards

    def in_motion(self):
        'check if card is being animated'
        return self.steps > 0

    def last_step(self):
        'check if card at last step of animation'
        return self.steps == 1

    def source_coords(self):
        'get the starting coordinates'
        return (self.cards[0].rect.left, self.cards[0].rect.top)

animation = Animation()

def draw_empty_stack(stack, coords):
    'draw a placeholder for the stack'
    left, top = coords
    pygame.draw.rect(screen, LIGHTGRAY, (left, top, CARD_W, CARD_H), 2)
    stack.xy = coords

def draw_top_bevel(_color, coords, width, height):
    'drop a top rounded rectangle'
    left, top = coords
    right = left + width
    pygame.draw.circle(screen, _color, (int(left+BRADIUS), int(top+BRADIUS)), int(BRADIUS), 0)
    pygame.draw.circle(screen, _color, (int(right-BRADIUS), int(top+BRADIUS)), int(BRADIUS), 0)
    pygame.draw.rect(screen, _color, (left, top+BRADIUS, width, height), 0)
    pygame.draw.rect(screen, _color, (left+BRADIUS, top, width-BRADIUS-BRADIUS, BRADIUS), 0)

def draw_bottom_bevel(_color, coords, width, height):
    'draw a bottom rounded rectangle'
    left, top = coords
    left = int(left)
    top = int(top)
    right = left + width
    bottom = top + height
    pygame.draw.circle(screen, _color, (int(left+BRADIUS), int(bottom-BRADIUS)), BRADIUS, 0)
    pygame.draw.circle(screen, _color, (right-BRADIUS, bottom-BRADIUS), BRADIUS, 0)
    pygame.draw.rect(screen, _color, (left, top, width, height-BRADIUS), 0)
    pygame.draw.rect(screen, _color, (left+BRADIUS, top+height-BRADIUS,
                                      width-2*BRADIUS, BRADIUS), 0)

def draw_top_card(card, coords):
    'draw the top visible portion of a card when covered by others'
    left, top = coords
    # draw card white background
    draw_top_bevel(WHITE, coords, CARD_W, CARDTOP_H)
    # separator
    pygame.draw.line(screen, LIGHTGRAY, (left+4, top), (left+CARD_W-4, top), 1)
    # rank
    value = card.rank if card.rank != "X" else "10"
    img = _font.render(value, True, (BLACK, RED)[card.is_red()])
    screen.blit(img, (left+PAD, top+PAD))
    # suit
    sfc = suitsImages[m.SUITS.index(card.suit)]
    screen.blit(sfc, (left+CARD_W-sfc.get_width()-PAD, top+PAD+2))
    #annotate card area
    card.rect = Rectangle(left, top, left+CARD_W, top+CARDTOP_H)

def draw_full_card(card, coords):
    'draw a fully visible card'
    left, top = coords
    draw_top_card(card, coords)
    draw_bottom_bevel(WHITE, (left, top+CARDTOP_H), CARD_W, CARD_H-CARDTOP_H)
    # add the larger image
    if m.RANKS.index(card.rank) <= m.RANKS.index("X"):
        # draw a big seed
        sfc = bigSuitsImages[m.SUITS.index(card.suit)]
        screen.blit(sfc, (left+(CARD_W-sfc.get_width())/2, top+CARD_H -sfc.get_height()-4),
                    (0, 0, CARD_W-8, CARD_H-8))
    else:
       # draw the figure
        sfc = figureImages[(m.RANKS.index(card.rank)
                            - m.RANKS.index("J"))*4 + m.SUITS.index(card.suit)]
        screen.blit(sfc, (left+4, top+CARD_H -sfc.get_height()-4),
                    (0, 0, CARD_W-8, CARD_H-8))
    #annotate card area
    card.rect = Rectangle(left, top, left+CARD_W, top+CARD_H)

def draw_card_back(card, coords):
    'draw the back of a card'
    left, top = coords
    draw_top_bevel(WHITE, coords, CARD_W, CARDTOP_H)
    draw_bottom_bevel(WHITE, (left, top+CARDTOP_H), CARD_W, CARD_H-CARDTOP_H)
    screen.blit(backImage[0], (left+4, top+4), (0, 0, CARD_W-8, CARD_H-8))
    #annotate card area
    card.rect = Rectangle(left, top, left+CARD_W, top+CARD_H)

def draw_top_card_back(card, coords):
    'draw only the visible portion of the back of a card partialy covered'
    left, top = coords
    draw_top_bevel(WHITE, coords, CARD_W, CARDTOP_H)
    screen.blit(backImage[0], (left+4, top+4), (0, 0, CARD_W-8, BACKTOP_H))
    #annotate card area
    card.rect = Rectangle(left, top, left+CARD_W, top+CARDTOP_H)

def draw_pile(pile, coords):
    'draw a pile of cards'
    left, top = coords
    for card in pile.cards:
        if card == pile.top():
            if card.face != 'U':    # ensure top cards are always face up
                card.face = 'U'     # turn card up
                log.append(('turn', pile))
            draw_full_card(card, (left, top))
        else: # visible
            if card.face == 'D':
                draw_top_card_back(card, (left, top))
            else:
                draw_top_card(card, (left, top))
        top += CARDTOP_H

buttons = m.Stack('button')

def draw():
    'displays current game board'
    # 0. paint the background
    screen.fill(GREEN)

    # 1. draw the four foundations
    left, top = FOUNDATIONS_LEFT, FOUNDATIONS_Y
    for foundation in m.FOUNDATIONS:
        if foundation.cards:
            draw_full_card(foundation.top(), (left, top))
        else:
            # leave empty space
            draw_empty_stack(foundation, (left, top))
        left += CARD_W + FOUNDATIONS_SPACE

    # 2. draw the DECK and the WASTE
    if m.DECK.cards:
        draw_card_back(m.DECK.top(), (DECK_X, DECK_Y))
    else:
        # draw empty space
        draw_empty_stack(m.DECK, (DECK_X, DECK_Y))

    # 3. draw the WASTE
    if m.WASTE.cards:
        draw_full_card(m.WASTE.top(), (WASTE_X, WASTE_Y))
    else:
        # draw empty space
        draw_empty_stack(m.WASTE, (WASTE_X, WASTE_Y))

    # 4. draw the 7 PILES
    left = ROWS_LEFT
    for pile in m.PILES:
        # count = 0
        top = ROWS_Y
        if not pile.cards:      # in case pile is empty
            draw_empty_stack(pile, (left, top))
        else:
            draw_pile(pile, (left, top))
        left += CARD_W + ROWS_SPACE

    # 4.bis add card in animation
    if animation.steps == animation.first:
        # find the source and destination coordinates
        destx, desty = animation.dest.coords()
        if animation.dest.name == 'pile' and animation.dest.cards:
            desty += CARDTOP_H
        srcx, srcy = animation.source_coords()
        # calculate the speed
        animation.speed_x = (destx-srcx) / (animation.first)
        animation.speed_y = (desty-srcy) / (animation.first)
        animation.current_xy = (srcx, srcy)

    if animation.steps > 0:
        # advance position
        # print('animation step', animation.steps)
        curx, cury = animation.current_xy
        curx += animation.speed_x
        cury += animation.speed_y
        animation.current_xy = (curx, cury)
        for card in animation.cards[:-1]:           # draw first cards (partially covered)
            draw_top_card(card, (curx, cury))
            cury += CARDTOP_H
        draw_full_card(animation.cards[-1], (curx, cury))    # draw last card in full
        animation.steps -= 1

    # 5. status updates
    left, top = XMAX -120, WASTE_Y + CARD_H + 20

    # 6. add step counter
    text = "Move: %d" % m.get_count()
    img = _font.render(text, 1, WHITE)
    screen.blit(img, (left, top))
    top += 20

    # 7. add buttons
    buttons.set_coords((left, top))
    for img in buttonImages:
        screen.blit(img, (left, top))
        buttons.cards.append(Button(img, Rectangle(left, top, left+100, top+100)))
        top += 80

    pygame.display.flip()

def select_box(options_list):
    ' model box selection menu'
    options = []
    for option in options_list:
        options.append(Button(_font.render(option, 1, WHITE), Rectangle(0, 0, 0, 0)))

    # width = max(map(lambda(x): x.img.get_width(), options)) + 2
    width = max([x.img.get_width() for x in options]) + 2
    # height = max(map(lambda(x): x.img.get_height(), options)) + 2
    height = max([x.img.get_height() for x in options]) + 2

    # draw a (centered) box capable of containing all the strings
    boxx = (XMAX - width - 10) / 2
    boxy = (YMAX - height* len(options) - 10) / 2
    pygame.draw.rect(screen, LIGHTGRAY, (boxx, boxy, width + 10, height*len(options) + 10), 0)

    # draw each string in a box and record the rectangle
    boxx += 5
    boxy += 5
    for i, option in enumerate(options):
        # the first line of text is the title so it does not get a dark bkgnd
        if i > 0:
            pygame.draw.rect(screen, DARKGRAY, (boxx, boxy, width, height), 0)
            option.rect = Rectangle(boxx, boxy, boxx+width, boxy+height)
        screen.blit(option.img, (boxx+1, boxy+1))
        boxy += height

    # now wait for user input (modal)
    while True:
        wait(20)
        # touch = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                coords = pygame.mouse.get_pos()
                for index, option in enumerate(options):
                    if option.rect.contains(coords):
                        return index-1   # ignore the title

def wait(rate):
    'establish animation rate'
    # pygame.display.flip()
    clock.tick(rate)


figureImages = []
suitsImages = []
bigSuitsImages = []
buttonImages = []
backImage = []
pygame.init()
pygame.display.set_caption("PySolitaire")
screen = pygame.display.set_mode((XMAX, YMAX))
clock = pygame.time.Clock()
_font = pygame.font.Font(pygame.font.match_font('Arial'), 24)
_font.set_bold(False)

def init_view():
    'load images'
    figureImages.append(pygame.image.load("images/jh.png")) 
    figureImages.append(pygame.image.load("images/jp.png")) 
    figureImages.append(pygame.image.load("images/jd.png")) #
    figureImages.append(pygame.image.load("images/jf.png")) # 
    figureImages.append(pygame.image.load("images/qh.png"))
    figureImages.append(pygame.image.load("images/qp.png"))
    figureImages.append(pygame.image.load("images/qd.png")) 
    figureImages.append(pygame.image.load("images/qf.png")) 
    figureImages.append(pygame.image.load("images/kh.png"))
    figureImages.append(pygame.image.load("images/kp.png"))
    figureImages.append(pygame.image.load("images/kd.png"))
    figureImages.append(pygame.image.load("images/kf.png")) #
    suitsImages.append(pygame.image.load("images/hearts.png"))
    suitsImages.append(pygame.image.load("images/spades.png")) #
    suitsImages.append(pygame.image.load("images/diamonds.png"))
    suitsImages.append(pygame.image.load("images/clubs.png")) #
    bigSuitsImages.append(pygame.image.load("images/bigheart.png"))
    bigSuitsImages.append(pygame.image.load("images/bigspade.png"))
    bigSuitsImages.append(pygame.image.load("images/bigdiamond.png")) #
    bigSuitsImages.append(pygame.image.load("images/bigclub.png"))
    backImage.append(pygame.image.load("images/RedBack.png"))
    buttonImages.append(pygame.image.load("images/undo.png"))
    buttonImages.append(pygame.image.load("images/restart.png"))
    buttonImages.append(pygame.image.load("images/new.png"))
