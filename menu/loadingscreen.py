import os, sys
import pygame
from pygame.locals import *

from display import LEDdisplay
#from menu import Menu
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
    ilosc_pol = 0
    kolor_tla = (51,51,51)
    kolor_tekstu =  (255, 255, 153)
    kolor_zaznaczenia = (153,102,255)
    pozycja_zaznaczenia = 0
    pozycja_wklejenia = (0,0)
    menu_width = 0
    menu_height = 0
    disp = LEDdisplay()

    class Pole:
        tekst = ''
        pole = pygame.Surface
        pole_rect = pygame.Rect
        zaznaczenie_rect = pygame.Rect

    def move_menu(self, top, left):
        self.pozycja_wklejenia = (top,left) 

    def set_colors(self, text, selection, background):
        self.kolor_tla = background
        self.kolor_tekstu =  text
        self.kolor_zaznaczenia = selection

    def set_font(self, path):
        self.font_path = path

    def get_position(self):
        return self.pozycja_zaznaczenia
    
    def init(self, lista, dest_surface):
        self.lista = lista
        self.dest_surface = dest_surface
        self.ilosc_pol = len(self.lista)
        self.stworz_strukture()        
        
    def draw(self,przesun=0):
        if przesun:
            self.pozycja_zaznaczenia += przesun 
            if self.pozycja_zaznaczenia == -1:
                self.pozycja_zaznaczenia = self.ilosc_pol - 1
            self.pozycja_zaznaczenia %= self.ilosc_pol
        menu = pygame.Surface((self.menu_width, self.menu_height))
        menu.fill(self.kolor_tla)
        zaznaczenie_rect = self.pola[self.pozycja_zaznaczenia].zaznaczenie_rect
        pygame.draw.rect(menu,self.kolor_zaznaczenia,zaznaczenie_rect)

        for i in range(self.ilosc_pol):
            menu.blit(self.pola[i].pole,self.pola[i].pole_rect)
        self.dest_surface.blit(menu,self.pozycja_wklejenia)
        send_frame(self.disp, self.dest_surface)
        return self.pozycja_zaznaczenia

    def stworz_strukture(self):
        przesuniecie = 0
        self.menu_height = 0
        self.font = pygame.font.Font(self.font_path, self.font_size)
        for i in range(self.ilosc_pol):
            self.pola.append(self.Pole())
            self.pola[i].tekst = self.lista[i]
            self.pola[i].pole = self.font.render(self.pola[i].tekst, 1, self.kolor_tekstu)

            self.pola[i].pole_rect = self.pola[i].pole.get_rect()
            przesuniecie = int(self.font_size * 0.2)

            height = self.pola[i].pole_rect.height
            self.pola[i].pole_rect.left = przesuniecie
            self.pola[i].pole_rect.top = przesuniecie+(przesuniecie*2+height)*i

            width = self.pola[i].pole_rect.width+przesuniecie*2
            height = self.pola[i].pole_rect.height+przesuniecie*2            
            left = self.pola[i].pole_rect.left-przesuniecie
            top = self.pola[i].pole_rect.top-przesuniecie

            self.pola[i].zaznaczenie_rect = (left,top ,width, height)
            if width > self.menu_width:
                    self.menu_width = width
            self.menu_height += height
        x = self.dest_surface.get_rect().centerx - self.menu_width / 2
        y = self.dest_surface.get_rect().centery - self.menu_height / 2
        mx, my = self.pozycja_wklejenia
        self.pozycja_wklejenia = (x+mx, y+my) 


if __name__ == '__main__':
  fps = 10
  #disp = LEDdisplay()
  width = 30
  height = 30
  clock = pygame.time.Clock();

  surface = init_pygame_display(width, height)
  surface.fill((51,51,51))

  menu = Menu()
  menu.init(['Start','Options','Quit'], surface)
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

      