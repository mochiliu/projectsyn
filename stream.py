import pyaudio
import time
import numpy as np
from pyAudioAnalysis.audioFeatureExtraction import stFeatureExtraction
import argparse
from neopixel import *

import os
from PIL import Image


parser = argparse.ArgumentParser(description="Read audio from microphone and output features.")
parser.add_argument('--sample_len', type=float, default=0.2,
                    help="length (in seconds) of each audio sample.")
parser.add_argument('--mean', type=bool, default=False, help="whether to include means of recent features as more features.")
parser.add_argument('--std', type=bool, default=False, help="whether to include standard deviation of recent features as more features.")
parser.add_argument('--memory_len', type=float, default=3, help="length (in seconds) of audio samples to remember.")
args = parser.parse_args()

Fs = 44100                      # audio signal frequency
chunk = int(args.sample_len * Fs)


class FeatureBuffer:
    """Store recent feature vectors and compute stats."""
    def __init__(self, n_stored, n_features):
        self.mem = np.zeros((n_stored, n_features))
        self.index = 0

    def store(self, features):
        self.mem[self.index, :] = features
        self.index = (self.index + 1) % self.mem.shape[0]

    def mean(self):
        return self.mem.mean(0)

    def std(self):
        return self.mem.std(0)


def set_from_matrix(strip, mat):
    mat = mat.astype(int)
    mat[range(mat.shape[0])[::2], :, :] = np.fliplr(mat[range(mat.shape[0])[::2], :, :])
    for r in range(mat.shape[0]):
        for c in range(mat.shape[1]):
            i = r * mat.shape[1] + c
            strip.setPixelColorRGB(i, *mat[r, c, :])
    strip.show()

def output(data):
    """Called for each chunk of input signal"""
    data = np.fromstring(data, dtype = np.int16)
    F = stFeatureExtraction(data, Fs, data.size, data.size).flatten()

    if args.mean or args.std:
        buf.store(F)
        if args.mean:
            F = np.concatenate((F, buf.mean()))
        if args.std:
            F = np.concatenate((F, buf.std()))
    
#    for i in range(900):
#        strip.setPixelColor(i, Color(np.random.randint(255),
#                                     np.random.randint(255),
#                                     np.random.randint(255)))
#    strip.show()


    inputV = [x * 100 for x in F[22:27]]
    #print(inputV)
    n1 = np.multiply(rc1,inputV[0])
    n2 = np.multiply(rc2,inputV[1])
    n3 = np.multiply(rc3,inputV[2])
    n4 = np.multiply(rc4,inputV[3])
    n5 = np.multiply(rc5,inputV[4])

    Im = n1+n2+n3+n4+n5
    m = np.amax(Im)

    ImN = np.divide(Im,m/255)
    ImP = np.reshape(ImN,[30,30,3])

    mat = np.zeros((30, 30, 3), dtype='float64')
    x = F[1] * 2.5 * 1.5
    x = (x - 0.5) * 1.5 + 0.5
    x = 1 - x
    x = max(0.05, min(x, 1))
    print(x)
    mat[:, :, :] = x

    ImP = np.multiply(ImP, mat)
    #print(ImP[0,:])

    ImP = ImP * ImP / 255.

    set_from_matrix(strip, ImP)

def callback(in_data, frame_count, time_info, status):
    output(in_data)
    return in_data, status

if args.mean or args.std:
    n_stored = int(args.memory_len / args.sample_len)
    buf = FeatureBuffer(n_stored, 34)

p = pyaudio.PyAudio()
s = p.open(format = pyaudio.paInt16,
           channels = 1,
           rate = Fs,
           input = True,
           frames_per_buffer = chunk)
#           stream_callback = callback)

dir = 'synesthesia/samples/'
c = os.listdir(dir)
c = np.random.choice(c, 5)
print(c)
rc1 = np.reshape(np.array(Image.open(dir + c[0])),[2700])
rc2 = np.reshape(np.array(Image.open(dir + c[1])),[2700])
rc3 = np.reshape(np.array(Image.open(dir + c[2])),[2700])
rc4 = np.reshape(np.array(Image.open(dir + c[3])),[2700])
rc5 = np.reshape(np.array(Image.open(dir + c[4])),[2700])


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

print("listening")

i = 0
while True:
    #time.sleep(1)
    output(s.read(chunk, exception_on_overflow=False))
    i += 1
    if i == 20:
        i = 0
        c = os.listdir(dir)
        #c = np.random.choice(c, 5)
        #print(c)
        #rc1 = np.reshape(np.array(Image.open(dir + c[0])),[2700])
        #rc2 = np.reshape(np.array(Image.open(dir + c[1])),[2700])
        #rc3 = np.reshape(np.array(Image.open(dir + c[2])),[2700])
        #rc4 = np.reshape(np.array(Image.open(dir + c[3])),[2700])
        #rc5 = np.reshape(np.array(Image.open(dir + c[4])),[2700])
        rc1 = rc2
        rc2 = rc3
        rc3 = rc4
        rc4 = rc5
        c = np.random.choice(c)
        print(c)
        rc5 = np.reshape(np.array(Image.open(dir + c)),[2700])


    #data = s.read(chunk)
    #data = np.fromstring(data, dtype = np.int16)
    #F = stFeatureExtraction(data, Fs, data.size, data.size).flatten()

    # if args.mean or args.std:
    #     buf.store(F)
    #     if args.mean:
    #         F = np.concatenate((F, buf.mean()))
    #     if args.std:
    #         F = np.concatenate((F, buf.std()))


    # Now feed F into net and send output to LEDs
    #for i in range(900):
    #    strip.setPixelColor(i, Color(np.random.randint(255),
    #                                 np.random.randint(255),
    #                                 np.random.randint(255)))
    #strip.show()

print("done listening")
s.close()
p.terminate()
