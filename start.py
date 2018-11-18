import numpy as np
import RPi.GPIO as GPIO
from enum import Enum
from display import LEDdisplay
from voicecontrol import VoiceController
from ColorPDFLearner import ColorPDFLearner
from CyclingDisplay import CyclingDisplay
import threading
import os

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

def get_preloaded_keywords():
    keywords = ['quit','exit','off','sample']
    cwd = os.getcwd()
    pdfdir = os.path.join(cwd, 'colorpdfs')
    filenames = os.listdir(pdfdir)
    for names in filenames:
        if names.endswith(".npy"):
            keywords.append(os.path.splitext(names)[0])
    return keywords

def parse_response(response, preloaded_keywords):
    # parses through the response from google cloud voice to consider alternatives
    # take the most likely alternative unless we notice key words we already have
    parsed_response = []
    print(response)
    for result in response.results:
        best_split_result = []
        break_flag = False
        for alternative in result.alternatives:
            potential_split_result = []
            split_results = alternative.transcript.split(' ')
            for split_result in split_results:
                lowercase_split_result = split_result.lower()
                potential_split_result.append(lowercase_split_result)
                if lowercase_split_result in preloaded_keywords:
                    break_flag = True
            if not best_split_result:
                #this is the most likely alternative
                best_split_result = potential_split_result.copy()
            if break_flag:
                # a keyword is detected, use this alternative, skip the rest
                break # go to the next result
        if break_flag:
            parsed_response = parsed_response + potential_split_result
        else:
            parsed_response = parsed_response + best_split_result
    return parsed_response
    
def main_fxn(debug_param):
    number_of_samples = 50
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
                #we are debugging commands, skip voice input
                response = debug_param
                debug_param = []
            else:
                response = vc.listen_for_speech()
                response = parse_response(response, get_preloaded_keywords())
            
            print(response)
            
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
                sampled_colors, new_words_to_learn = color_learner.sortedsamplemultiple(words, number_of_samples)
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
            words_to_learn = list(set(words_to_learn)) # only learn new words once
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
    main_fxn(['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'indigo', 'violet', 'purple', 'magenta', 'pink', 'brown', 'white', 'gray', 'black', 'teal'])
    #main_fxn([])

