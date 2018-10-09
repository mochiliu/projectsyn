import numpy as np
#import time
import RPi.GPIO as GPIO
from enum import Enum
from display import LEDdisplay
from voicecontrol import VoiceController
from ColorPDFLearner import ColorPDFLearner


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


def main_fxn():
    number_of_samples = 20

    light_state = light_states.PowerOff #start assuming we are off
    disp = LEDdisplay()
    vc = VoiceController()
    color_learner = ColorPDFLearner()
    vc.open_tap_mic_stream()
    ml_color = None
    #sampled_colors = None
    
    while True:
        # never stop doing the lights! lights or bust
        if light_state == light_states.CyclingSampleDisplay:
            print('to do')
            return 
        
        if vc.listen_for_tap():
            # a double tap is detected! listen for speech
            vc.stop()
            powerstate = not light_state == light_state.Poweroff
            powerstate = display_listening_indicator(powerstate, disp)
            light_state = light_states.ListeningForSpeech
            
            response = vc.listen_for_speech()
            
            # process responses
            # check for exit commands
            command_index = 1
            command_word_found = False
            if response == []:
                # no words detected, turn the panel off
                light_state = light_state.Poweroff
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
                ml_color = color_learner.maxlikelihoodcolor(response)
                single_color_linear_array = np.tile(ml_color, 900)
                disp.set_from_array(single_color_linear_array)
                
            elif light_state == light_state.CyclingSampleDisplay:
                words = list( response[i] for i in range(command_index, len(response)))
                sampled_colors = color_learner.samplemultiple(words, number_of_samples)
                print(sampled_colors)
                
                
            vc.open_tap_mic_stream() #start the tap mic again
            
if __name__ == "__main__":
    main_fxn()