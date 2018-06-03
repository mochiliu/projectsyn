import os, sys
import pygame as pg
from display import LEDdisplay
import numpy as np


def init_pygame_display(width, height):
	#os.environ["SDL_VIDEODRIVER"] = "dummy"
	pg.init()
	pg.display.set_mode((width, height), pygame.FULLSCREEN, 24)
	return pg.display.get_surface()


class PGMatrixApp:
  def __init__(self):
    self.width = 30
    self.height = 30
    self.screen = init_pygame_display(self.width, self.height)
    self.clock = pg.time.Clock();
    self.fps = 10
    self.disp = LEDdisplay()

  def send_frame(self):
    self.disp.set_from_array(self.screen.get_view('3'))

  def setup(self):
    self.text = "HELLO"
    self.x = 0.0
    self.y = 0.0
    self.t = 0.0
    self.vx = 1.0
    self.vy = 1.0
    self.vt = 1.0
    self.ticks = 0;

  def logic_loop(self):
    self.t += self.vt
    if (abs(self.t) > 30):
      self.vt *= -1.0;

    self.x += self.vx
    if self.x < 0 or self.x > self.width - 10:
      self.vx *= -1
   
    self.y += self.vy
    if self.y < 0 or self.y > self.height - 10:
      self.vy *= -1

  def graphics_loop(self):
    font = pg.font.SysFont(None, 10)
    label = font.render(self.text, True, pg.Color(b'red'))

    self.screen.blit(label, (self.x, self.y))

  def run(self):
    self.setup()
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
			    pygame.quit()
			    sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
			    pygame.quit()
			    sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                self.y += self.vy
            if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                self.y -= self.vy

		self.screen.fill(pg.Color(b'black'))
		self.logic_loop()
		self.graphics_loop()
		# send_frame(self.pipe, self.screen)
		#testarray = np.random.randint(256, size=2700)
		#self.disp.set_from_array(testarray)
		self.send_frame()
		pg.display.update()
		self.clock.tick(self.fps)


if __name__ == '__main__':
  PGMatrixApp().run()
