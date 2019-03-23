import numpy as np
from display import LEDdisplay
import socket
import struct
import fluidsynth
import time

UDP_IP = "192.168.1.247"
UDP_PORT = 5005
BUFFER_SIZE = 3000
N = 30
FRAMERATE = 3 #Hz
INSTRUMENT = 11


frame_period = 1.0 / FRAMERATE

def play_midi(on_keys, off_keys, fs):
    for pitch, velocity in off_keys:
        # turn off the last set of keys
        fs.noteoff(0, pitch)
    for pitch, velocity in on_keys:
        # turn on the next set of keys
        fs.noteon(0, pitch, velocity) #instument keys, and velocity

#set up UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False)

#start synth
fs = fluidsynth.Synth(gain=3)
fs.start(driver='alsa')
sfid = fs.sfload('/usr/share/sounds/sf2/FluidR3_GM.sf2')
fs.program_select(0, sfid, 0, INSTRUMENT) #instrument selection
print(fs.channel_info(0))

disp = LEDdisplay()

def receiveUDP(msg):
    linear_array = msg[0:(N*N*3)]
    on_keys = []
    
    index = N*N*3
    while True:
        if msg[index] == 0 and msg[index+1] == 0:
            #look for 2 0s in a row
            break
        on_keys.append((msg[index], msg[index+1]))
        index += 2
#    index += 2
#    off_keys = []
#    while True:
#        if msg[index] == 0 and msg[index+1] == 0:
#            #look for 2 0s in a row
#            break
#        off_keys.append((msg[index], msg[index+1]))
#        index += 2
        
    return linear_array, on_keys#, off_keys

on_keys = []
last_frame_time = 0
while True:
    data, addr = sock.recvfrom(BUFFER_SIZE)
    if data:
        linear_array = np.zeros(BUFFER_SIZE, dtype=np.int)
        s = ""
        for i in range(BUFFER_SIZE):
            s+="B"
        msg = struct.unpack(s,data)
        off_keys = on_keys
        linear_array, on_keys = receiveUDP(msg)
    
    current_time = time.clock()        
    if (current_time - last_frame_time > frame_period):    
        disp.set_from_array(linear_array)
        play_midi(on_keys, off_keys, fs)
        last_frame_time = current_time
#	print "received message:", linear_array
