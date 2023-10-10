import RPi.GPIO as GPIO

class LCD:
    RS = 4
    RW = 5
    E = 6
    D4 = 0
    D5 = 0
    D6 = 0
    D7 = 0


    def __init__(self):
        GPIO.setup()


