# Python code to implement Conway's Game Of Life 
import numpy as np 
import threading
import fluidsynth
import time
import music_vae_generate_minimal

#presets

INSTRUMENT = 0
#piano(0,0) rhodesep(0,4) legendep(0,5) glockenspiel (0,9) vibraphone (0,11) xylophone (0,13) tubularbells (0,14) 
        #percussive organ (0,17) churchorgan (0,19) accordian (0,21) gitar (0,25) bass gitar (0,34) synth bass (0,38) violin (0,40) strings (0,48) ahhchoir (0,52) 
        #trumpet (0,56) tuba (0,58) brasssection (0,61)
FRAMERATE = 10 #Hz


def play_midi(last_keys, keys, fs):
    for pitch, velocity in last_keys:
        # turn off the last set of keys
        fs.noteoff(0, pitch)
        
    for pitch, v in keys:
        # turn on the next set of keys
        fs.noteon(0, pitch, velocity) #instument keys, and velocity


class MelodyPlayer:
    def __init__(self, frame_rate=10):
        self.fs = fluidsynth.Synth(gain=3)
        self.fs.start(driver='alsa')
        sfid = self.fs.sfload('/usr/share/sounds/sf2/FluidR3_GM.sf2')
        self.fs.program_select(0, sfid, 0, INSTRUMENT) #instrument selection
        #self.fs.program_select(0, sfid, 0, 0) 
        print(self.fs.channel_info(0))
            
    def play(self, ns, running):
        #loop and sample melodies until we are stopped
        
        last_frame_time = time.clock()
        last_note_time = last_frame_time + self.note_length + 1 #always start with turning a note on
        last_keys = []
        keys = []
        cursor = 0
        while running.is_set():
            current_time = time.clock()        
            if (current_time - last_note_time) > self.note_length:
                #time to update music
                last_keys = keys.copy()
                keys = []
                if cursor in self.notes:
                    for note, color in self.notes[cursor]:
                        pitch = 1
                        veolcity = 1
                        keys.append((pitch, veolcity))
                play_midi(last_keys, keys, self.fs)
                cursor += 1
                last_note_time = current_time
                
        

        #turn off the last set of keys before aborting
        play_midi(last_keys, [], self.fs)
        self.fs.delete()

# call main 
if __name__ == '__main__': 
    running = threading.Event()
    player = MelodyPlayer(FRAMERATE)
    running.set()
    ns = music_vae_generate_minimal.random_sample_model()
    player.play(ns, running)
    