#!/usr/bin/env python
# Solitaire
#

import GameView as view
import Model as model
import pygame, sys

#
# Controller
#

def animate( dest, dindex, dXY, source, sindex, slen, sXY):
    global Adest, Aindex, Log

    # program animation
    dx, dy = dXY     # get the tip dest coordinates
    sx, sy = sXY     # get source coordinates
    
    # save the destination list
    Adest = dest    # list to append to after animation
    Aindex = dindex

    # remove card/tail from source list
    cards = model.getCards( source, sindex, slen)
    # log the move
    Log.append( ("move", (dest, dindex, dXY, source, sindex, slen, sXY)))

    # final point
    Asteps.append( ( cards, 0, 0)) # only one step, final
    # 3/4 point
    Asteps.append( ( cards, sx+3*(dx-sx)/4, sy+3*(dy-sy)/4))
    # half point
    Asteps.append( ( cards, sx+2*(dx-sx)/4, sy+2*(dy-sy)/4))
    # 1/4 point
    Asteps.append( ( cards, sx+1*(dx-sx)/4, sy+1*(dy-sy)/4))


def undo():
    global Log
    if Log:
        # animate the reverse of the last move
        action, x  = Log.pop()
        if action == "move":
            dest, dindex, dXY, source, sindex, slen, sXY = x
            animate( source, sindex, sXY, dest, dindex, slen, dXY)
            Log.pop()   # avoid logging the undo action

        elif action == "unhide":
            undo()
            model.rowHide( x)

        elif action == "refill":
            model.unrefillStack()


if __name__ == "__main__":
    Auto = False
    Victory = False
    Log = []

    # init graphics environment
    view.init()

    # intialize the model
    model.init()

    # deal the cards (ramdom)
    model.shuffle()
    model.deal()

    #update display
    view.display()

    # count the steps
    model.countSteps = 0

    Asteps = []      # list of pre-computed steps for animation
    Adest = None     # target list for card at the end of animation
    Aindex = None    

    # main loop
    while( True):
        touch = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONUP:
                touch = view.checkTouch ( pygame.mouse.get_pos())

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    sys.exit()

                elif event.key == pygame.K_m:
                    touch = ("basket", 0, (view.basket_x, view.basket_y))

                elif event.key == pygame.K_SPACE:
                    touch = ("stack", 0, (view.stack_x, view.stack_y))

                elif event.key == pygame.K_COMMA:
                    touch = ("button", 0, 0)

        # check if animation pending
        if Asteps:
            cards, x, y = Asteps.pop()
            if Asteps: # there are more steps pending
                # update the view and then add the card in motion
                view.display()
                for card in cards:
                    if card == cards[-1]: # last in the tail
                        view.printFullCard( card, x, y)
                    else:
                        view.printTopCard( card, x, y)
                    y += view.cardtop_h

            else:   # end of animation 
                # place card(s) in final position then update view
                cards.reverse()
                for card in cards:
                    model.moveTo( Adest, Aindex, card)
                model.countSteps += 1
                view.display()

        # victory?
        elif Victory:
            choice = view.selectBox(["Victory", "Start a new Game", "Quit"])
            if choice == 0:
                Victory = False
                Auto = False
                model.init()
                model.shuffle()
                model.deal()
                model.countSteps = 0
                Log=[]
                view.display()
            else:
                sys.exit()

        # auto mode activated
        elif Auto:
            # try to use the top card in the basket
            if model.basket:
                card = model.getBasketTip()
                # try to move the card automatically to the first matching row
                top = model.matchTop( card)
                if top >= 0:
                    animate( 't', top,                      # dest list
                             view.topXY[ top],              # dest coord
                             'b', 0, 1,                     # source list
                             (view.basket_x, view.basket_y))# source coords
                    Victory = model.checkFinished()
                    # update display
                    view.display()
                    continue

            # try with one of the tips
            for i in xrange( 7):
                if model.rows[ i]:
                    card = model.getTip( i)
                    # check if it can go to the top
                    top = model.matchTop( card)
                    if top >= 0:
                        animate( 't', top,                  # dest list
                                 view.topXY[ top],          # dest coord
                                 'r', i, 1,                 # source list
                                 view.tipXY[ i])            # source coords
                        Victory = model.checkFinished()
                        # update display
                        view.display()
                        break


        # else respond to last user input
        elif touch:
            obj, srow, xy = touch

            if obj == "stack":
                if model.stack:
                    # get the top card down into the basket
                    animate( 'b', 0,                        # dest list
                             (view.basket_x, view.basket_y),# dest coord
                             's', 0, 1,                     # source list
                             xy)                            # source coord
                else: 
                    # if stack is empty
                    if model.basket:    # and basket is not empty
                        model.refillStack()
                        Log.append( ("refill", 0))
                    
            elif obj == "tip":
                card = model.getTip( srow)

                # check if it can go to the top
                top = model.matchTop( card)
                if top >= 0:
                    animate( 't', top,                  # dest list
                             view.topXY[ top],          # dest coord
                             'r',  srow, 1,             # source list
                             xy)                        # source coords
                    if model.checkHidden( srow):
                        Log.append( ("unhide", srow))

                # or to another row
                else:
                    drow = model.matchRow( card)
                    if drow >= 0:
                        animate( 'r', drow,             # dest list
                                 view.tipXY[ drow],     # dest coord
                                 'r', srow, 1,          # source list
                                 xy)                    # source coords
                        if model.checkHidden( srow):
                            Log.append( ("unhide", srow))

            elif obj == "tail":
                srow = touch[1]/16
                index = touch[1]%16
                card = model.rows[ srow][index]
                drow = model.matchRow( card)
                if drow >= 0:
                    slen = len( model.rows[srow]) - index
                    animate( 'r', drow,                 # dest list
                             view.tipXY[ drow],         # dest coord
                             'r', srow, slen,           # source list
                             xy)                        # source coord
                    if model.checkHidden( srow):
                        Log.append( ("unhide", srow))

            elif obj == "top":
                top = touch[1]
                card = model.getTop( top)
                row = model.matchRow( card)
                if row >= 0:
                    animate( 'r', row,                  # dest list
                             view.tipXY[ row],          # dest coord
                             't', top, 1,               # source list
                             xy)                        # source coords

            elif obj == "basket":
                card =  model.getBasketTip()
                if card:
                    # try to move the card automatically to a top
                    top = model.matchTop( card)
                    if top >= 0:
                        animate( 't', top,              # dest list
                                 view.topXY[ top],      # dest coord
                                 'b', 0, 1,             # source list
                                 xy)                    # source coords

                    else: # move to a tip
                        row = model.matchRow( card)
                        if row >= 0:
                            animate( 'r', row,          # destination list
                                     view.tipXY[ row],  # dest coordinates
                                     'b', 0, 1,         # source list
                                     xy)                # source coordinates

            elif obj == "button":
                if srow == 0:  # undo
                    undo()

                elif srow == 1:  # restart
                    model.restart()
                    model.countSteps = 0
                    Log=[]

                elif srow == 2:  # re-shuffle and deal a new one
                    model.init()
                    model.shuffle()
                    model.deal()
                    model.countSteps = 0
                    Log=[]

            # update display
            view.display()
            # check if auto can be activated
            if not Auto:
                Auto = ( model.countHidden() < 1)

        # refresh
        view.wait( 20)

