import numpy as np
import time
import RPi.GPIO as GPIO
from enum import Enum
from display import LEDdisplay
from voicecontrol import VoiceController
from ColorPDFLearner import ColorPDFLearner
import threading

class light_states(Enum):
    PowerOff = 0
    ListeningForSpeech = 1
    ConstantMLDisplay = 2
    CyclingSampleDisplay = 3

def set_power_state(powerstate):
    # set the power state of the light panel, to save energy and reduce excess noise
    GPIO.setmode(GPIO.BCM)
    powersupplypin = 2
    GPIO.setup(powersupplypin,GPIO.OUT)
    GPIO.output(powersupplypin,powerstate)

def display_listening_indicator(powerstate, disp):
    #display on the LED panel the listening indicator
    if not powerstate:
        #turn the LED panel ON if it is not already on
            powerstate = True
            set_power_state(powerstate) 
    disp.set_from_image_path("listening.bmp")
    return powerstate


def main_fxn(debug_param):
    number_of_samples = 20
    frame_period = 1.0 / 1 #1 hz
    sample_number = 0
    last_frame_time = time.clock()
    
    light_state = light_states.PowerOff #start assuming we are off
    disp = LEDdisplay()
    vc = VoiceController()
    color_learner = ColorPDFLearner()
    vc.open_tap_mic_stream()
    ml_color = None
    words_to_learn = []
    thread = None
    sampled_colors = None
    
    while True:
        # never stop doing the lights! lights or bust
        if light_state == light_states.CyclingSampleDisplay:
            current_time = time.clock()
            if (current_time - last_frame_time > frame_period):
                #time to update
                sampled_color = sampled_colors[:,sample_number]
                single_color_linear_array = np.tile(sampled_color, 900)
                disp.set_from_array(single_color_linear_array)
                sample_number = (sample_number + 1) // number_of_samples
        
        if vc.listen_for_tap() or debug_param:
            # a tap sequence is detected! listen for speech
            vc.stop()
            powerstate = not light_state == light_states.PowerOff
            powerstate = display_listening_indicator(powerstate, disp)
            light_state = light_states.ListeningForSpeech
            
            if debug_param:
                response = debug_param
                debug_param = []
            else:
                response = vc.listen_for_speech()
            
            # process responses
            # check for exit commands
            command_index = 1
            command_word_found = False
            if response == []:
                # no words detected, turn the panel off
                set_power_state(False)
                light_state = light_state.PowerOff
                command_word_found = True
            for word in response:
                if word == 'quit' or word == 'exit':
                    # bust :(
                    set_power_state(False)
                    return
                elif word == 'off':
                    set_power_state(False)
                    light_state = light_state.Poweroff
                    command_word_found = True
                    break
                elif word == 'sample':
                    if not command_index == len(response):
                        #command is the last word dont count
                        light_state = light_state.CyclingSampleDisplay
                        command_word_found = True
                        break
                command_index += 1
                
            if not command_word_found:
                # assume just color words, do the normal ML calculations
                light_state = light_state.ConstantMLDisplay
                ml_color, new_words_to_learn = color_learner.maxlikelihoodcolor(response)
                single_color_linear_array = np.tile(ml_color, 900)
                disp.set_from_array(single_color_linear_array)
                
            elif light_state == light_state.CyclingSampleDisplay:
                words = list( response[i] for i in range(command_index, len(response))) #get rid of words prior to command word
                sampled_colors, new_words_to_learn = color_learner.samplemultiple(words, number_of_samples)
                print(sampled_colors)
                
            # learn words
            words_to_learn = words_to_learn + new_words_to_learn            
            words_to_learn = list(set(words_to_learn)) # only learn new words onces
            new_words_to_learn = []
            vc.open_tap_mic_stream() #start the tap mic again
        
        # work in the background to learn new words
        if words_to_learn and (thread is None or not thread.is_alive()):
            # start learning a new word if we have words to learn and available resources
            word = words_to_learn.pop(0)
            thread = threading.Thread(target=color_learner.learnword, args=[word])
            thread.daemon = True
            thread.start()
            
if __name__ == "__main__":
    main_fxn(['red'])
