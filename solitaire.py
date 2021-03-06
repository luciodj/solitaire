#!/usr/bin/env python3
'''
    Solitaire
'''
from GameView import animation, log, draw, init_view, wait, check_touch
from GameView import touch_deck, touch_waste, touch_button, touch_pile, select_box
import Model as model
import pygame
import sys

#
# Controller
#

def move(dest, source, index):
    'move card(s) from source to destination'
    length = len(dest.cards)
    animation.set(dest=dest, cards=model.get_cards_from(source, index))
    log.append(("move", (dest, source, length)))
    # animation loop
    while animation.in_motion():
        draw()
        wait(animation.speed)
        pygame.event.get()
        # while(not pygame.event.get()): pass   # single step through animation
    # place card(s) in final position then update view
    for card in animation.cards:
        animation.dest.cards.append(card)
    draw()
    print(model.get_state())
    model.countSteps += 1

def check_move_to_pile(atouch):
    'verify if a card is compatible with a pile'
    if not atouch:
        return None
    card = atouch.source.cards[touch.index]
    apile = card.match_pile()
    if apile != None:
        move(dest=apile, source=atouch.source, index=atouch.index)
    return apile

def check_move_to_foundation(atouch):
    'verify if a card is compatible with a foundation'
    if not atouch:
        return None
    if len(atouch.source.cards[touch.index:]) > 1:
        return None
    card = atouch.source.cards[touch.index]
    foundation = card.match_foundation()
    if foundation != None:
        move(dest=foundation, source=atouch.source, index=atouch.index)
    return foundation

def undo():
    'undo last operation logged'
    if log.list:
        action, params = log.pop()
        if action == "move":
            dest, source, index = params
            move(source, dest, index)      # animate the reverse of the last move
            log.pop()                       # avoid logging the undo action
        elif action == "turn":
            card = params.top()
            undo()                          # move / animate
            card.face = 'D'                 # turn back down
        elif action == "recycle":
            model.undo_recycle()
        draw()
        print(model.get_state())

def user_input():
    'returns a touch tuple, intercepts QUIT'
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONUP:
            return check_touch(pygame.mouse.get_pos())
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                sys.exit()
            if event.key == pygame.K_m:
                return touch_waste()
            if event.key == pygame.K_SPACE:
                return touch_deck()
            if event.key == pygame.K_COMMA:
                return touch_button(0)

def start_game():
    'set up the intial game configuration'
    model.init()
    # check if a configuration restore is required for debugging
    if len(sys.argv) > 1:
        model.restore_state(sys.argv[1])
        del(sys.argv[1])
    else:
        model.shuffle()
        model.deal()
    model.countSteps = 0
    log.clear()


#----------------------------------------------------------------------

if __name__ == "__main__":
    init_view()
    auto = False
    victory = False
    start_game()
    draw()
    # print state for debugging purposes
    print(model.get_state())
    
    # main loop
    while True:

        wait(animation.speed)
        touch = user_input()

        if victory:
            choice = select_box(["victory", "Start a new Game", "Quit"])
            if choice == 0:
                auto = False
                victory = False
                start_game()
                continue
            else:
                sys.exit()

        # auto mode activated
        elif auto:
            # try to use the top card from the waste
            if model.WASTE:
                # print ('check Waste')
                # try to move the card automatically to the first matching foundation
                if check_move_to_foundation(touch_waste()):
                    victory = model.check_finished()

            # try with one of the tips
            for pile in model.PILES:
                if pile:
                    # print ('check Pile', pile)
                    if check_move_to_foundation(touch_pile(pile)):
                        victory = model.check_finished()

        # else respond to user input
        elif touch:
            if touch.source.name == "deck":
                if model.DECK.cards:
                    # get the top card down into the waste
                    move(dest=model.WASTE, source=model.DECK, index=-1)
                else: # if deck is empty
                    model.recycle()
                    draw()
                    print(model.get_state())
                    log.append(("recycle", 0))

            elif touch.source.name == "pile":
                if not check_move_to_foundation(touch):
                    check_move_to_pile(touch)

            elif touch.source.name == "tail":
                check_move_to_pile(touch)

            elif touch.source.name == "foundation":
                check_move_to_pile(touch)

            elif touch.source.name == "waste":
                if not check_move_to_foundation(touch):
                    check_move_to_pile(touch)

            elif touch.source.name == "button":
                if touch.index == 0:  # undo
                    undo()

                elif touch.index == 1:  # restart
                    model.restart()
                    model.count_steps = 0
                    log.clear()

                elif touch.index == 2:  # re-shuffle and deal a new one
                    auto = False
                    victory = False
                    start_game()
                draw()
                # print state for debugging purposes
                print(model.get_state())

            # check if auto can be activated
            if not auto:
                auto = (model.count_hidden() < 1)
