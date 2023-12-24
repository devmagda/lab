import time
from venv import logger

from flask import logging

import RPi.GPIO as GPIO

# ---------- Initialisation Phase ----------------------------------------------------------
try:
    GPIO.setmode(GPIO.BOARD)
except:
    print('Board mode already set..')

GPIO.setwarnings(False)


# ---------- Raspberry Pi Pins -------------------------------------------------------------
class Pin:
    def __init__(self, pin, mode):
        self.pin = pin
        self.mode = mode
        GPIO.setup(pin, mode)


class Out(Pin):
    clockPulseLen = .01

    def __init__(self, pin):
        super().__init__(pin, GPIO.OUT)

    def high(self):
        GPIO.output(self.pin, GPIO.HIGH)

    def low(self):
        GPIO.output(self.pin, GPIO.LOW)

    def tick(self):
        self.high()
        time.sleep(Out.clockPulseLen)
        self.low()
        time.sleep(Out.clockPulseLen)


class PWM(Out):
    def __init__(self, pin, pulse_width=100):
        super().__init__(pin)
        self.pwm = GPIO.PWM(pin, pulse_width)
        self.pwm.start(0)

    def set_power(self, percentage=0):
        self.pwm.ChangeDutyCycle(percentage)


# ---------- Controllers ----------------------------------------------------------------
class Controller:
    pass


class ShiftRegister(Controller):

    def __init__(self, clock, data, latch):
        self.clock = Out(clock)
        self.data = Out(data)
        self.latch = Out(latch)
        self.registers = [False, False, False, False, False, False, False, False]

    @staticmethod
    def from_config():
        import pins
        return ShiftRegister(clock=pins.L_SH_CP, data=pins.L_DS, latch=pins.L_ST_CP)

    def set(self, registers=None):
        if registers is not None:
            self.registers = registers

        for register in self.registers[::-1]:
            if register:
                self.data.high()
            else:
                self.data.low()
            self.clock.tick()

    def set_index(self, index, value: bool):
        self.registers[index] = value
        self.set()


class LightSystem(ShiftRegister):
    I_LIGHTS = 0
    I_BREAKS = 1
    I_LEFT = 2
    I_RIGHT = 3

    def __init__(self, clock, data, latch):
        super.__init__(clock, data, latch)

    def set_lights(self, on):
        self.set_index(LightSystem.I_LIGHTS, on)

    def set_breaks(self, on):
        self.set_index(LightSystem.I_BREAKS, on)

    def set_left(self, on):
        self.set_index(LightSystem.I_LEFT, on)

    def set_right(self, on):
        self.set_index(LightSystem.I_RIGHT, on)

    @staticmethod
    def from_config():
        import pins
        return LightSystem(clock=pins.L_SH_CP, data=pins.L_DS, latch=pins.L_ST_CP)


class L293D(Controller):
    class __Motor:
        def __init__(self, forward_pin, backward_pin, speed_pin):
            self.forward = Out(forward_pin)
            self.backward = Out(backward_pin)
            self.speed = PWM(speed_pin)

        def stop(self):
            self.forward.low()
            self.backward.low()
            self.speed.set_power(percentage=0)

        def set_speed(self, speed):
            if speed > 100 or speed < -100:
                raise ValueError(f'Speed is out of range ({speed})')
            self.stop()
            if speed > 0:
                self.forward.high()
                self.speed.set_power(percentage=speed)
            if speed < 0:
                self.backward.high()
                self.speed.set_power(percentage=-speed)

    @staticmethod
    def from_config():
        def from_config():
            import pins
            return L293D(pins.E_IN1, pins.E_IN2, pins.E_IN3, pins.E_IN4, pins.E_EN_12, pins.E_EN_34)

    def __init__(self, in1: int, in2: int, in3: int, in4: int, vcc1: int, vcc2: int):
        self.motor1 = L293D.__Motor(in1, in2, vcc1)
        self.motor2 = L293D.__Motor(in3, in4, vcc2)

    def reset(self):
        self.motor1.stop()
        self.motor2.stop()

    def forward(self, speed):
        self.motor1.set_speed(speed)
        self.motor2.set_speed(speed)

    def rotate_right(self, speed):
        self.motor1.set_speed(speed)
        self.motor2.set_speed(-speed)

    def rotate_left(self, speed):
        self.rotate_right(-speed)


class TrackController(L293D):
    @staticmethod
    def from_config():
        import pins
        return TrackController(pins.E_IN1, pins.E_IN2, pins.E_IN3, pins.E_IN4, pins.E_EN_12, pins.E_EN_34)

    def __init__(self, in1: int, in2: int, in3: int, in4: int, vcc1: int, vcc2: int):
        super().__init__(in1, in2, in3, in4, vcc1, vcc2)

    def forward(self, speed: float):
        self.steer(speed, speed)

    def backward(self, speed: float):
        self.steer(-speed, -speed)

    def rotate_right(self, speed: float):
        self.steer(speed, -speed)

    def rotate_left(self, speed: float):
        self.rotate_right(-speed)

    def stop(self):
        self.reset()

    def steer(self, left: float, right: float):
        logger.info("steering")
        self.motor1.set_speed(left)
        self.motor2.set_speed(right)

    def directions(self, x, y, direction):
        turn = 75
        speed = 100

        # limit speed to 100
        if x > 100:
            x = 100

        if y > 100:
            y = 100

        if x < -100:
            x = -100

        if y < -100:
            y = -100

        if direction == 'C':
            self.reset()
        elif direction == 'N':
            self.forward(speed)
        elif direction == 'NE':
            self.steer(speed, turn)
        elif direction == 'E':
            self.rotate_right(speed)
        elif direction == 'SE':
            self.steer(-speed, -turn)
        elif direction == 'S':
            self.forward(speed)
        elif direction == 'SW':
            self.steer(-turn, -speed)
        elif direction == 'W':
            self.rotate_left(-speed)
        elif direction == 'NW':
            self.steer(turn, speed)
        else:
            raise ValueError(f'Direction {direction} is not a valid direction')


# ---------- Stepper Motor -----------------------------------------------------------------
class ULN2003:
    # defining how long to wait between steps:
    motor_latency = 0.0008

    def __init__(self, pins, latency=motor_latency, half_step=True):
        self.pins = pins
        self.latency = latency
        if half_step:
            # half-step (step in cycle, pin output)
            self.sequence = [[1, 0, 0, 0],
                             [1, 1, 0, 0],
                             [0, 1, 0, 0],
                             [0, 1, 1, 0],
                             [0, 0, 1, 0],
                             [0, 0, 1, 1],
                             [0, 0, 0, 1],
                             [1, 0, 0, 1]]
        else:
            # full-step (step in cycle, pin output)
            self.sequence = [[1, 1, 0, 0],
                             [0, 1, 1, 0],
                             [0, 0, 1, 1],
                             [1, 0, 0, 1]]
        for p in range(len(self.pins)):
            GPIO.setup(self.pins[p], GPIO.OUT)

    def read_pins(self):
        config = []
        for p in range(len(self.pins)):
            config.append(GPIO.input(self.pins[p]))
        return config

    def cycle(self, sequence):
        for i in range(len(sequence)):
            for p in range(len(self.pins)):
                GPIO.output(self.pins[p], sequence[i][p])
            time.sleep(self.latency)
        return None

    def step(self, n=1):
        sequence = self.sequence

        sign = n / abs(n)
        if sign < 0:
            sequence = sequence[::-1]
        n = abs(n)

        config = self.read_pins()  # determining where in the cycle we currently are
        cycle_index = len(sequence) - 1  # initialising the cycle index

        for i in range(len(sequence)):
            if config == sequence[i]:
                cycle_index = i

        n_before = max(0, min(n,
                              len(sequence) - cycle_index - 1))  # number of steps still required to be at the begning of the next cycles (clipped to be less than n)
        n_after = (n - n_before) % len(
            sequence)  # the number of steps that will occur after the full cycles are executed
        n_cycles = (n - n_before - n_after) // len(sequence)  # the number of full cycles stepping by n will encompass

        for j in range(n_before):
            for p in range(len(self.pins)):
                GPIO.output(self.pins[p], sequence[cycle_index + j + 1][p])
            time.sleep(self.latency)

        for k in range(n_cycles):
            self.cycle(sequence)

        for l in range(n_after):
            for p in range(len(self.pins)):
                GPIO.output(self.pins[p], sequence[l][p])
            time.sleep(self.latency)

        return None
