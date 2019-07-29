# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 01:08:17 2019

@author: Mochi
"""

import pygame
from pygame.locals import *
import numpy as np

def rgb_int2tuple(rgbint):
    return (rgbint // 256 // 256 % 256, rgbint // 256 % 256, rgbint % 256)

def rgb2int(rint, gint, bint):
    return int(rint*256*256 + (gint*256) + bint)


def randomGrid(N): 
    """returns a grid of NxN random values"""
    grid = np.zeros((N,N), dtype=int)
    for i in range(N): 
        for j in range(N): 
            if np.random.uniform() < 0.1:
                # cell alive
                grid[i,j] = int(np.random.uniform(low=1, high=(256*256*256)-1))
    return grid


def local_GOL_display(screen, gol_board, magnifcation):
    #display the board
    magnified_board = np.repeat(gol_board, magnifcation, axis=0)
    magnified_board = np.repeat(magnified_board, magnifcation, axis=1)  
    
    screen.fill((0,0,0))
    pxarray = pygame.PixelArray(screen)
    for x in range(len(pxarray)):
        for y in range(len(pxarray)):
            pxarray[x,y] = rgb_int2tuple(magnified_board[x,y])
    del pxarray
    pygame.display.update()


#if __name__ == '__main__': 

N = 30
magnifcation = 5

pygame.init()
screen = pygame.display.set_mode((N*magnifcation,N*magnifcation), pygame.HWSURFACE)
pygame.display.set_caption('Pygame')

gol_board = randomGrid(N)
local_GOL_display(screen, gol_board, magnifcation)
