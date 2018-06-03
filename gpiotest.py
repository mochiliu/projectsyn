import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
powersupplypin = 2
powerstate = False
GPIO.setup(powersupplypin,GPIO.OUT)

GPIO.output(powersupplypin,powerstate)
