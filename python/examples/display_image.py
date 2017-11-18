# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
import time
import numpy as np

from neopixel import *


# LED strip configuration:
LED_COUNT      = 900      # Number of LED pixels.
LED_PIN        = 12      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

shift = 0;

# Define a function that displays an image on the LED
def display(strip, image):
	position = 0;
	for i in range(np.size(image,0)):
		for j in range(np.size(image,1)):
			strip.setPixelColor(position, Color(image[i,j,0], image[i,j,1], image[i,j,2]))
			#strip.setPixelColor(position, Color(i, j, 0))
			position += 1
	strip.show()



# Main program logic follows:
if __name__ == '__main__':
	# Create NeoPixel object with appropriate configuration.
	strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
	# Intialize the library (must be called once before other functions).
	strip.begin()
	#image = np.full((30,30,3), 255)
	#bw_image = np.diag(range(30))
	image = np.zeros((30,30,3))
	for i in range(30):
		for j in range(30):
			image[i,j,0] = 255;
			image[i,j,1] = 255;
			image[1,j,2] = 255;
	while True:
		#image = np.concatenate((bw_image, bw_image, bw_image), axis=2)
		image = np.roll(image, 1, axis=0)
		print ('displaying image')
		display(strip, image.astype(int))
		time.sleep(1)
