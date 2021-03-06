import numpy as np
from neopixel import *
from PIL import Image
import ctypes
import os

def gamma_correct_pixel_color(pixel_color, LUT):
    return LUT[pixel_color]

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
		self.LUT            = np.array([0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, \
                                0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1, \
                                1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2, \
                                2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5, \
                                5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10, \
                               10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16, \
                               17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25, \
                               25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36, \
                               37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50, \
                               51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68, \
                               69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89, \
                               90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114, \
                              115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142, \
                              144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175, \
                              177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213, \
                              215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255],dtype=int)


		self.strip = Adafruit_NeoPixel(self.LED_COUNT, self.LED_PIN, self.LED_FREQ_HZ,
		                          self.LED_DMA, self.LED_INVERT, self.LED_BRIGHTNESS,
		                          self.LED_CHANNEL, self.LED_STRIP)
		self.strip.begin()


	def set_from_array(self, linear_array, gamma_correct=True):
		#try:
			mat = np.reshape(linear_array, (30,30,3))
			mat = np.fliplr(mat)
			# mat = np.rot90(mat,3)
			mat[range(mat.shape[0])[::2], :, :] = np.fliplr(mat[range(mat.shape[0])[::2], :, :])
			mat.astype(int)
			for r in range(mat.shape[0]):
				for c in range(mat.shape[1]):
					i = r * mat.shape[1] + c
					pixel_color = mat[r, c, :]
					if gamma_correct:
						pixel_color = gamma_correct_pixel_color(pixel_color, self.LUT)
					pixel_color = pixel_color.tolist()
					self.strip.setPixelColorRGB(i, *pixel_color)
			self.strip.show()
		#except:
			#print('error setting strip')

	def set_from_image_path(self, imagepath):
		loaded_image = Image.open(imagepath)
		width, height = loaded_image.size
		leftpixel = np.floor(width/2)-15
		toppixel = np.floor(height/2)-15
		rightpixel = leftpixel+30
		bottompixel = toppixel+30       
		loaded_image = loaded_image.crop((leftpixel, toppixel, rightpixel, bottompixel))
		loaded_image = np.reshape(np.array(loaded_image),[2700])
		self.set_from_array(loaded_image)

	def test(self):
		testarray = np.random.randint(256, size=2700)
		self.set_from_array(testarray)

if __name__ == '__main__':
    #LEDdisplay().test()
    LEDdisplay().set_from_image_path("listening.bmp")
