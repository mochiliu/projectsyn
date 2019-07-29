import pygame
import time
import numpy as np


def display_test():
    pygame.init()
    screen = pygame.display.set_mode((100,100))
    pygame.display.set_caption('Pygame')
    pygame.mouse.set_visible(0)

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250,250,250))


    test = np.ones((100,100), dtype=hex)
    
    pxarray = pygame.PixelArray(background)
    print(np.shape(pxarray))
    print(np.shape(test))    
    pxarray[0:9999] = test[0:9999]

    del pxarray

    screen.blit(background, (0,0))
    pygame.display.flip()
    time.sleep(30) 
    pygame.quit()
    
display_test()

