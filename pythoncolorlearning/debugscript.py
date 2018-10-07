# -*- coding: utf-8 -*-
"""
Created on Sun Oct  7 15:47:00 2018

@author: Mochi
"""

import pygame 
from math import *
from random import *
from copy import *

num_nodes = int(raw_input("Please enter the number of nodes to be visited: "))

#Initialize game
pygame.init()

# Set the height and width of the screen
size = [1000, 1000]
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Traveling salesman problem")

#Color definitions
BLACK = ( 0, 0, 0)
WHITE = (255, 255, 255)
BLUE =  ( 0, 0, 255)
GREEN = (0, 255, 0)
RED =   (255, 0, 0)

coords = []
for n in range(num_nodes):
    t = (randint(0,990),randint(0,990))
    coords.append(t)

def draw_nodes(num_nodes,temp):
    screen.fill(WHITE)
    #pygame.draw.rect(screen,BLACK,[1,1,10,10])
    for n in temp:
        pygame.draw.circle(screen,BLUE,n,10)
    return

def dist(x,y,x1,y1):
    return ((x-x1)**2 + (y-y1)**2)

def draw_path(cities):
    if cities == []:
        return
    else:
        for n in range(len(cities)-1):
            pygame.draw.line(screen,RED,cities[n],cities[n+1],1)
        return

temp = deepcopy(coords)
city_num = randint(0,len(coords)-1)
city = coords[city_num]
fcity = coords[city_num]
cities_t = []
best_city = None
shall_loop = True
temp.remove(city)

while True:
    draw_nodes(num_nodes,coords)
    dist1 = 1e10
    if shall_loop:
        for n in temp:
            if dist1 > dist(city[0],city[1],n[0],n[1]):
                dist1 = dist(city[0],city[1],n[0],n[1])
                best_city = n
            else:
                continue
        if temp != []:
            temp.remove(best_city)
        cities_t.append(city)
        city = best_city
        if temp == []:
            shall_loop = False
            cities_t.append(city)
            cities_t.append(fcity)
    draw_path(cities_t)
    pygame.time.wait(100)
    pygame.display.flip()
    if not temp:
        break