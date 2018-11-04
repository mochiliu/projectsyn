import numpy as np
import RPi.GPIO as GPIO
from enum import Enum
from display import LEDdisplay
from voicecontrol import VoiceController
from ColorPDFLearner import ColorPDFLearner
from CyclingDisplay import CyclingDisplay
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
    frame_rate = 10 #1 Hz
    
    light_state = light_states.PowerOff #start assuming we are off
    disp = LEDdisplay()
    vc = VoiceController()
    color_learner = ColorPDFLearner()
    vc.open_tap_mic_stream()
    cycling_diplay = None
    ml_color = None
    words_to_learn = []
    background_thread = None
    running = threading.Event()
    
    while True:
        # never stop doing the lights! lights or bust

        if vc.listen_for_tap() or debug_param:
            # a tap sequence is detected! listen for speech
            vc.stop()
            if light_state == light_state.CyclingSampleDisplay:
                # we are still runing the background changing color process, end it
                running.clear()
                
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
                number_in_path = np.shape(sampled_colors)
                number_in_path = number_in_path[1]
                if number_in_path == 1:                    
                    #there's only one color that is sampled, constantly display it
                    light_state = light_state.ConstantMLDisplay
                    single_color_linear_array = np.tile(sampled_colors, 900)
                    disp.set_from_array(single_color_linear_array)
                else:
                    #if there are more than 1 color to display, go through them
                    cycling_diplay = CyclingDisplay(disp, frame_rate, sampled_colors)
                    running.set()
                    background_thread = threading.Thread(target=cycling_diplay.start_cycling, args=[running])
                    background_thread.daemon = True
                    background_thread.start()

            # learn words
            words_to_learn = words_to_learn + new_words_to_learn            
            words_to_learn = list(set(words_to_learn)) # only learn new words onces
            new_words_to_learn = []
            vc.open_tap_mic_stream() #start the tap mic again
        
        # work in the background while power is off to learn new words
        if light_state == light_states.PowerOff and words_to_learn and (background_thread is None or not background_thread.is_alive()):
            # start learning a new word if we have words to learn and available resources
            word = words_to_learn.pop(0)
            background_thread = threading.Thread(target=color_learner.learnword, args=[word])
            background_thread.daemon = True
            background_thread.start()
            
if __name__ == "__main__":
    main_fxn(['sample','teal'])
    #main_fxn([])
