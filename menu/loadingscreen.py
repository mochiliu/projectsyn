import os, sys
import pygame
from pygame.locals import *

from display import LEDdisplay
import numpy as np


def init_pygame_display(width, height):
	#os.environ["SDL_VIDEODRIVER"] = "dummy"
	pygame.init()
	pygame.display.set_mode((width, height), pygame.FULLSCREEN, 24)
	return pygame.display.get_surface()

def send_frame(myLEDdisplay, game_surface):
  myLEDdisplay.set_from_array(game_surface.get_view('3'))


class Menu:
    lista = []
    pola = []
    font_size = 10
    font_path = 'data/coders_crux/coders_crux.ttf'
    font = pygame.font.Font
    dest_surface = pygame.Surface
    item_count = 0
    color_background = (0,0,0)
    color_text =  (0,255,0)
    color_selection = (50,0,0)
    selection_position = 0
    move_correction = (0,0)
    menu_width = 0
    menu_height = 0
    disp = LEDdisplay()

    class Pole:
        tekst = ''
        pole = pygame.Surface
        pole_rect = pygame.Rect
        zaznaczenie_rect = pygame.Rect

    def move_menu(self, top, left):
        self.move_correction = (top,left) 

    def set_colors(self, text, selection, background):
        self.color_background = background
        self.color_text =  text
        self.color_selection = selection

    def set_font(self, path):
        self.font_path = path

    def get_position(self):
        return self.selection_position
    
    def init(self, lista, dest_surface):
        self.lista = lista
        self.dest_surface = dest_surface
        self.item_count = len(self.lista)
        self.stworz_strukture()        
        
    def draw(self,move=0):
        if move:
            self.selection_position += move 
            if self.selection_position == -1:
                self.selection_position = self.item_count - 1
            self.selection_position %= self.item_count
        menu = pygame.Surface((self.menu_width, self.menu_height))
        menu.fill(self.color_background)
        zaznaczenie_rect = self.pola[self.selection_position].zaznaczenie_rect
        pygame.draw.rect(menu,self.color_selection,zaznaczenie_rect)

        for i in range(self.item_count):
            menu.blit(self.pola[i].pole,self.pola[i].pole_rect)
        self.dest_surface.blit(menu,self.move_correction)
        send_frame(self.disp, self.dest_surface)
        return self.selection_position

    def stworz_strukture(self):
        moveiecie = 0
        self.menu_height = 0
        self.font = pygame.font.Font(self.font_path, self.font_size)
        for i in range(self.item_count):
            self.pola.append(self.Pole())
            self.pola[i].tekst = self.lista[i]
            self.pola[i].pole = self.font.render(self.pola[i].tekst, 1, self.color_text)

            self.pola[i].pole_rect = self.pola[i].pole.get_rect()
            moveiecie = int(self.font_size * 0.2)

            height = self.pola[i].pole_rect.height
            self.pola[i].pole_rect.left = moveiecie
            self.pola[i].pole_rect.top = moveiecie+(moveiecie*2+height)*i

            width = self.pola[i].pole_rect.width+moveiecie*2
            height = self.pola[i].pole_rect.height+moveiecie*2            
            left = self.pola[i].pole_rect.left-moveiecie
            top = self.pola[i].pole_rect.top-moveiecie

            self.pola[i].zaznaczenie_rect = (left,top ,width, height)
            if width > self.menu_width:
                    self.menu_width = width
            self.menu_height += height
        x = self.dest_surface.get_rect().centerx - self.menu_width / 2
        y = self.dest_surface.get_rect().centery - self.menu_height / 2
        mx, my = self.move_correction
        self.move_correction = (x+mx, y+my) 


if __name__ == '__main__':
  fps = 10
  #disp = LEDdisplay()
  width = 30
  height = 30
  clock = pygame.time.Clock();

  surface = init_pygame_display(width, height)
  surface.fill((51,51,51))

  menu = Menu()
  menu.init(['START','OPTIONS','QUIT'], surface)
  #menu.move_menu(0, 0)#optional
  menu.draw()#necessary
  
  pygame.key.set_repeat(199,69)#(delay,interval)
  pygame.display.update()
  while 1:
      for event in pygame.event.get():
          if event.type == KEYDOWN:
              if event.key == K_UP:
                  menu.draw(-1) #here is the Menu class function
              if event.key == K_DOWN:
                  menu.draw(1) #here is the Menu class function
              if event.key == K_RETURN:
                  if menu.get_position() == 2:#here is the Menu class function
                      pygame.display.quit()
                      sys.exit()                        
              if event.key == K_ESCAPE:
                  pygame.display.quit()
                  sys.exit()
              pygame.display.update()
          elif event.type == QUIT:
              pygame.display.quit()
              sys.exit()
      #clock.tick(fps)

      
