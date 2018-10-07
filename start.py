#from display import LEDdisplay

#from voicecontrol import VoiceController
from ColorPDFLearner import ColorPDFLearner

if __name__ == "__main__":
    powerstate = False
    #vc = VoiceController()
    color_learner = ColorPDFLearner()
    #while True:
    # never stop
    #response = vc.listen()
    word = input("What color?")
    ml_color = color_learner.maxlikelihoodcolor(word)
    print(ml_color)
        