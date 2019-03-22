#
# I got this wooden puzzle composed of 25 y-shaped pentominoes 
# The objective is to tile pentominoes into a 5x5x5 cube.
# Playing around with it, I found that I was not clever enough. 
# This necessitated the need for assistance in for of a fast, cold and precise python mind.
#
# This is a program to try all possible combinations and find all solutions [ignoring symmetries].
#

import numpy as np
import time

def find_lastzero(ls):
    '''Returns the index of the last free field.'''
    ls = np.reshape(ls,(5*5*5))
    imax = -1
    for i in range(len(ls)):
        if ls[i]==0:
            imax = i
    x = (imax - (imax%25)) / 25
    z = (imax%25) % 5
    y = ((imax%25)-z) / 5
    return np.int(x), np.int(y), np.int(z)

def TestPuzzle(testpuzzle):
    '''Returns true if the puzzle is without contradictions.'''
    if np.max(testpuzzle) > 1:
        return False
    return True

def PrintPuzzle(puzzle):
    '''Prints the 3D puzzle as sequence of individual x|y layers.'''
    size = np.int(np.ceil(puzzle.size**(1/3.)))
    s = "\n\n"
    for z in range(size):
        for y in range(size):  
            for x in range(size):  
                s = s + str(puzzle[x,y,z]) + " "
            s = s + "\n"
        s = s + "------------\n"
    print(s)

def make_lut():
    '''Make a lookup table for all pieces.'''
    lut = np.zeros((5,5,5,4,6,5,5,5,5), dtype=np.int)    
    flags = np.zeros((5,5,5,4,6,5),dtype = np.bool)
    for x in range(5):
        for y in range(5):
            for z in range(5):
                for revo in [0,1,2,3]:
                    for ori in [0,1,2,3,4,5]:
                        for pos in [0,1,2,3,4]:
                            coords = [x,y,z]
                            l = give_piece(coords,revo, ori, pos)
                            flags[x,y,z,revo,ori,pos] = np.isfinite(np.sum(l))
                            if np.isfinite( np.sum(l) ):
                                lut[x,y,z,revo,ori,pos,:,:,:] = l			    
    return lut, flags

def give_piece(coords, revo, ori, pos):
    ''' Returns a pice centered at (x,y,z), with choice revo, ori and pos
        if possible    : returns a piece   and   flag = True
        if not possible: returns Empty     and   flag = False
        Generates all conceivable pieces with 4 revolutions x 6 orientations x 5 positions.
        Yields -> 120 options
    '''
    x,y,z = coords[0], coords[1], coords[2]
    piece_template = np.zeros((7,7,7),dtype=np.int)
    t = [\
    [ 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0], 
    [ 0, 1, 0, 0, 0, 0, 0],
    [ 1, 1, 1, 1, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0],
    [ 0, 0, 0, 0, 0, 0, 0]]
    t = np.transpose(t)
    # first, center on piece index "pos"
    if pos in range(4):
        t = np.roll(t, (pos,0), axis = (0,1) )
    else:
        t = np.roll(t, (2,  1), axis = (0,1) )
    # second, select orientation "ori" with revolutions "revo"
    if ori == 0:      # along  -x, rotate y|z
        piece_template[:,:,3] = t
        piece_template = np.rot90(piece_template, revo, axes=(1,2))
    elif ori == 1:    # along  x, rotate y|z
        t = np.flipud(t)
        piece_template[:,:,3] = t
        piece_template = np.rot90(piece_template, revo, axes=(1,2))
    elif ori == 2:   # along -y, rotate x|z
        t = np.rot90(t)
        piece_template[:,:,3] = t
        piece_template = np.rot90(piece_template, revo, axes=(0,2))
    elif ori == 3:   # along  y, rotate x|z
        t = np.rot90(np.rot90(np.rot90(t)))
        piece_template[:,:,3] = t
        piece_template = np.rot90(piece_template, revo, axes=(0,2))
    elif ori == 4:   # along  z, rotate x|y
        piece_template[:,:,3] = t
        piece_template = np.rot90(piece_template,1,axes=(0,2))
        piece_template = np.rot90(piece_template, revo, axes=(0,1))
    elif ori == 5:   # along  -z, rotate x|y
        piece_template[:,:,3] = t
        piece_template = np.rot90(piece_template,-1,axes=(0,2))
        piece_template = np.rot90(piece_template, revo, axes=(0,1))
    piece_template = np.roll(piece_template, (-2+x,-2+y,-2+z), axis = (0,1,2))
    mask = np.zeros((7,7,7), dtype=np.int)
    mask[1:6,1:6,1:6] = 1
    if np.sum((1-mask)*piece_template) == 0:
        return piece_template[1:6,1:6,1:6]
    else:
        return np.nan

def tail_call(puzzle, t0):
    '''Saves the solution and computing time to a textfile.'''
    size = np.int(np.ceil(puzzle.size**(1/3.)))
    s = "\nFound at " + str(round(time.time()-t0)) + "s:\n\n"
    for z in range(size):
        for y in range(size):  
            for x in range(size):  
                s = s + str(puzzle[x,y,z]) + " "
            s = s + "\n"
        s = s + "------------\n"
    text_file = open('puzzle_solutions.dat', "a")
    text_file.write(s)
    text_file.close()

lut, flags = make_lut()

def solver(puzzle, puzzle_config, reccounter, t0):
    x,y,z = find_lastzero(puzzle)           # Find last free spot
    for revo in [0,1,2,3]:
        for ori in [0,1,2,3,4,5]:
            for pos in [0,1,2,3,4]:
                flag = flags[x,y,z, revo, ori, pos]
                if flag:
                    newpiece = lut[x,y,z, revo, ori, pos,:,:,:]
                    puzzleToFill = np.copy(puzzle) + newpiece
                    if TestPuzzle(puzzleToFill):      # If this is ok, follow the tree
                        missing_numbers = np.sum(np.array(puzzleToFill)==0)
                        new_puzzle_config = np.copy(puzzle_config) + newpiece*np.sum(puzzle)/5
                        if missing_numbers > 0:
                            solver(puzzleToFill,new_puzzle_config,reccounter+1, t0)
                        else:                         # If the Puzzle is solved, print it. 
                            PrintPuzzle(new_puzzle_config)
                            tail_call(new_puzzle_config, t0)


t0 = time.time()
puzzle = np.zeros((5,5,5),dtype=np.int)
puzzle_config = np.copy(puzzle)
solver(puzzle, puzzle_config, 0, t0)
t1 = time.time()
print(t1-t0)
