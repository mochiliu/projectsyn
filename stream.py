import numpy as np
from neopixel import *
import socket

UDP_IP = "192.168.1.247"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))


def set_from_matrix(strip, mat):
    mat = mat.astype(int)
    mat[range(mat.shape[0])[::2], :, :] = np.fliplr(mat[range(mat.shape[0])[::2], :, :])
    for r in range(mat.shape[0]):
        for c in range(mat.shape[1]):
            i = r * mat.shape[1] + c
            strip.setPixelColorRGB(i, *mat[r, c, :])
    strip.show()


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

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ,
                          LED_DMA,LED_INVERT, LED_BRIGHTNESS,
                          LED_CHANNEL, LED_STRIP)
strip.begin()

while True:
	data, addr = sock.recvfrom(2700) # buffer size is 2700 bytes
	print "received message:", data
