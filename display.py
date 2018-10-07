import numpy as np
from neopixel import *
from PIL import Image
import os

class LEDdisplay:
	def __init__(self):
		# LED strip configuration:
		self.LED_COUNT      = 900      # Number of LED pixels.
		self.LED_PIN        = 12      # GPIO pin connected to the pixels (18 uses PWM!).
		#self.LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
		self.LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
		self.LED_DMA        = 10       # DMA channel to use for generating signal (try 5)
		self.LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
		self.LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
		self.LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
		self.LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

		self.strip = Adafruit_NeoPixel(self.LED_COUNT, self.LED_PIN, self.LED_FREQ_HZ,
		                          self.LED_DMA, self.LED_INVERT, self.LED_BRIGHTNESS,
		                          self.LED_CHANNEL, self.LED_STRIP)
		self.strip.begin()

	def set_from_array(self, linear_array):
		try:
			mat = np.reshape(linear_array, (30,30,3));
			mat = mat.astype(int)
			mat = np.fliplr(mat)
			# mat = np.rot90(mat,3)
			mat[range(mat.shape[0])[::2], :, :] = np.fliplr(mat[range(mat.shape[0])[::2], :, :])
			for r in range(mat.shape[0]):
				for c in range(mat.shape[1]):
					i = r * mat.shape[1] + c
					self.strip.setPixelColorRGB(i, *mat[r, c, :])
			self.strip.show()
		except:
			print('error setting strip')

	def set_from_image_path(self, imagepath):
		loaded_image = np.reshape(np.array(Image.open(imagepath)),[2700])
		self.set_from_array(loaded_image)

	def test(self):
		testarray = np.random.randint(256, size=2700)
		self.set_from_array(testarray)

if __name__ == '__main__':
	LEDdisplay().set_from_image_path("listening.bmp")
