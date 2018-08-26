
from clapdetection import TapTester
import RPi.GPIO as GPIO
from display import LEDdisplay
import time


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


if __name__ == "__main__":
	powerstate = False
	disp = LEDdisplay()
	tt = TapTester()

	while True:
		# never stop
		tt.resetDoubleTap()
		
		while tt.doubleTap == False:
    		tt.listen()

    	# we got a double clap!
		powerstate = display_listening_indicator(powerstate, disp)
		time.sleep(10)
		powerstate = False
		set_power_state(powerstate)

