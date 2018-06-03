import os, sys
from subprocess import call
import pygame as pg

def init_pygame_display(width, height):
  os.environ["SDL_VIDEODRIVER"] = "dummy"
  pg.init()
  pg.display.set_mode((width, height), 0, 24)
  return pg.display.get_surface()

def init_pipe():
  pipe_name = "/tmp/pgmatrix"
  if not os.path.exists(pipe_name):
    os.mkfifo(pipe_name)
  # call(["../matrix-server", sys.argv[1], sys.argv[2], sys.argv[3]])
  return os.open(pipe_name, os.O_WRONLY)

def send_frame(pipe, surface):
  return os.write(pipe, surface.get_view('0').raw)


class PGMatrixApp:
  def __init__(self):
    self.width = int(sys.argv[2]) * 32
    self.height = int(sys.argv[3]) * 32
    self.screen = init_pygame_display(self.width, self.height)
    self.pipe = init_pipe()
    self.clock = pg.time.Clock();
    self.fps = 10
    
  def setup(self):
    self.background = pg.transform.scale(pg.image.load(sys.argv[5]), (self.width, self.height))
    self.text = sys.argv[4]
    self.x = 10.0
    self.y = 10.0
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
    font = pg.font.SysFont("Comic Sans MS", 16)
    fps = font.render(str(int(self.clock.get_fps())) + ' fps', 1, pg.Color(b'orange'))
    label = font.render(self.text, 1, pg.Color(b'red'))
    label = pg.transform.rotate(label, self.t)
    label = pg.transform.rotate(label, self.t)

    self.screen.blit(self.background, (0, 0))
    self.screen.blit(label, (self.x, self.y))
    self.screen.blit(fps, (0, 50))

  def run(self):
    self.setup()
    while True:
      self.logic_loop()
      self.graphics_loop()
      send_frame(self.pipe, self.screen)
      self.screen.fill(pg.Color(b'black'))
      self.clock.tick(self.fps)


if __name__ == '__main__':
  DemoText().run()