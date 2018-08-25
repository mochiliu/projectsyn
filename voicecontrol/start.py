
from clapdetection import TapTester
import RPi.GPIO as GPIO
from display import LEDDisplay
import time


powerstate = False
disp = LEDdisplay()

def set_power_state():
	# set the power state of the light panel, to save energy and reduce excess noise
	GPIO.setmode(GPIO.BCM)
	powersupplypin = 2
	GPIO.setup(powersupplypin,GPIO.OUT)
	GPIO.output(powersupplypin,powerstate)

def listen_for_voice_command():
	#listen for a command after booting up the LED strips
	display_listening_indicator()
	time.sleep(10)
	powerstate = False
	set_power_state()


def display_listening_indicator():
	#display on the LED panel the listening indicator
	if not powerstate:
		#turn the LED panel ON if it is not already on
    	powerstate = True
    	set_power_state() 

    disp.set_from_image_path("listening.bmp")



if __name__ == "__main__":

    while True:
    	# never stop
		tt = TapTester()
    	while tt.doubleTap == False:
        	tt.listen()
        # we got a double clap!
        listen_for_voice_command()
        

