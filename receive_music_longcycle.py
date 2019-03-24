import numpy as np
from display import LEDdisplay
import socket
import struct
import fluidsynth
import time

UDP_IP = "192.168.1.247"
UDP_PORT = 5005
BUFFER_SIZE = 3200
N = 30
CYCLE_PERIOD = 10. #seconds
NOTE_PERIOD = CYCLE_PERIOD / 256
#FRAMERATE = 3 #Hz
INSTRUMENT = 1
#presets
#piano(0,0) rhodesep(0,4) legendep(0,5) glockenspiel (0,9) vibraphone (0,11) xylophone (0,13) tubularbells (0,14) 
        #percussive organ (0,17) churchorgan (0,19) accordian (0,21) gitar (0,25) bass gitar (0,34) synth bass (0,38) violin (0,40) strings (0,48) ahhchoir (0,52) 
        #trumpet (0,56) tuba (0,58) brasssection (0,61)

frame_period = CYCLE_PERIOD

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

def decodeUDP(msg):
    linear_array = msg[0:(N*N*3)]
    ns_pitch = []
    ns_velocity = []
    ns_start_time = []
    ns_end_time = []
    
    index = N*N*3
    while True:
        if msg[index] == 0 and msg[index+1] == 0 and msg[index+2] == 0 and msg[index+3] == 0 or index+3 >= BUFFER_SIZE:
            #look for 4 0s in a row
            break
        ns_pitch.append(msg[index])
        ns_velocity.append(msg[index+1])
        ns_start_time.append(msg[index+2]) # out of 255
        ns_end_time.append(msg[index+3]) # out of 255
        index += 4
    #print(index)
    return linear_array, ns_pitch, ns_velocity, ns_start_time, ns_end_time

msg = []
on_keys = []
off_keys = []
linear_array =np.zeros((N*N*3,), dtype=np.int)
last_frame_time = 0
note_sequence_index = 0
ns_start_time = []
ns_end_time = []
ns_pitch = []
ns_velocity = []

while True:
    current_time = time.clock()
    if not msg:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            linear_array = np.zeros(BUFFER_SIZE, dtype=np.int)
            s = ""
            for i in range(BUFFER_SIZE):
                s+="B"
            msg = struct.unpack(s,data)
        except BlockingIOError:
            pass
    
    if (current_time - last_frame_time > NOTE_PERIOD):
        on_notes = np.where(ns_start_time == note_sequence_index)[0]
        off_notes = np.where(ns_end_time == note_sequence_index)[0]
        #print(on_notes)
        for on_note in on_notes:
            fs.noteon(0, ns_pitch[on_note], ns_velocity[on_note])
        for off_note in off_notes:
            fs.noteoff(0, ns_pitch[off_note])
        last_frame_time = current_time        
        note_sequence_index += 1
        
    if note_sequence_index >= 256 and msg:    
        #cycle is done, load the next game board
        #unload msg
        linear_array, ns_pitch, ns_velocity, ns_start_time, ns_end_time = decodeUDP(msg)
        print(ns_pitch)
        print(ns_velocity)
        print(ns_start_time)
        print(ns_end_time)
        disp.set_from_array(linear_array)
        msg = []
        note_sequence_index = 0


        
        

        
#	print "received message:", linear_array
