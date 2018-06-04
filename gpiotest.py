import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
powersupplypin = 2
powerstate = True
GPIO.setup(powersupplypin,GPIO.OUT)

GPIO.output(powersupplypin,powerstate)
