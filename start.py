import numpy as np
import time
from display import LEDdisplay
from voicecontrol import VoiceController
from ColorPDFLearner import ColorPDFLearner

if __name__ == "__main__":
    powerstate = False
    disp = LEDdisplay()
    vc = VoiceController()
    vc.set_display(disp)
    color_learner = ColorPDFLearner()
    #while True:
    # never stop
    #response = vc.listen()
    word = input("What color?")
    ml_color = color_learner.maxlikelihoodcolor(word)
    print(ml_color)
    if not powerstate:
        powerstate = vc.set_LED_power_state(True)
        
    single_color_linear_array = np.tile(ml_color, 900)
    disp.set_from_array(single_color_linear_array)
    time.sleep(1)
    powerstate = vc.set_LED_power_state(False)
