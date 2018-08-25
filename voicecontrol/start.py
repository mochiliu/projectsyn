
from clapdetection import TapTester
import RPi.GPIO as GPIO
powerstate = False


def set_power_state():
	# set the power state of the light panel, to save energy and reduce excess noise
	GPIO.setmode(GPIO.BCM)
	powersupplypin = 2
	GPIO.setup(powersupplypin,GPIO.OUT)
	GPIO.output(powersupplypin,powerstate)

def listen_for_voice_command():



def display_listening_indicator():
	#display on the LED panel the listening indicator
	if not powerstate:
		#turn the LED panel ON if it is not already on
    	powerstate = True
    	set_power_state() 

	


if __name__ == "__main__":

    while True:
    	# never stop
		tt = TapTester()
    	while tt.doubleTap == False:
        	tt.listen()
        # we got a double clap!

        

