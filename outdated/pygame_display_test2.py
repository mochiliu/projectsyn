# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 02:50:15 2019

@author: Mochi
"""

import pygame, sys, time, random
from pygame.locals import *

# set up pygame
pygame.init()

# set up the window
windowSurface = pygame.display.set_mode((500, 400), 0, 32)
pygame.display.set_caption('Hello world!')

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# set up fonts
basicFont = pygame.font.SysFont(None, 48)

def draw_loop():
#    # set up the text
#    text = basicFont.render('Hello world!', True, WHITE, BLUE)
#    textRect = text.get_rect()
#    textRect.centerx = windowSurface.get_rect().centerx
#    textRect.centery = windowSurface.get_rect().centery
#    
    # draw the white background onto the surface
    windowSurface.fill(WHITE)
    
    # get a pixel array of the surface
    pixArray = pygame.PixelArray(windowSurface)
    pixArray[random.randint(0, 100)][random.randint(0, 100)] = BLACK
    del pixArray
    
#    # draw the text onto the surface
#    windowSurface.blit(text, textRect)
#    
    # draw the window onto the screen
    pygame.display.update()

# run the game loop
last_frame_time = time.clock()
frame_period = 1
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    current_time = time.clock()        
    if (current_time - last_frame_time > frame_period):
        draw_loop()
        last_frame_time = current_time