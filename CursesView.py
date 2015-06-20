#
# Solitaire Curses View
#
from Model import *

# update display with current game status
RED     = '\033[01;31m'
BLACK   = '\033[00m'

def printCard( c):
    #depending on seed change color
    if c.isRed():
        print RED,  c.val(), ",", c.seed(), BLACK,
    else:
        print BLACK, c.val(), ",", c.seed(), BLACK,


def display( ):
    # print the four tops
    for i in xrange( 4):
        if i & 1 == 0:
            print RED,

        else:
            print BLACK,

        print seedseq[ i],
        if tops[ i] > 0:
            print cardseq[ tops[ i]-1],
        else:
            print '-',
        print "    ",
    print

    # print the stack and the basket
    print "stack: %d, basket: %d" % (len(stack), len(basket))
    if stack:
        printCard( stack[-1]),
    #if basket:
    #    print basket[0]
    print

    # print the rows
    for i in xrange( 7):
        print i, #hidden[i],
        x = 0
        for card in rows[i]:
            if hidden[i] > x:
                print '(X,X),',
            else:
                printCard( card),
            x+=1
        print


