from machine import Pin
import time

class Stepper:
    def __init__(self, step_p, dir_p):
        self.current_pulse = 0
        self.step_pin = Pin(step_p, Pin.OUT)
        self.dir_pin = Pin(dir_p, Pin.OUT)
        self.current_direction = 0
        self.target_pulse = 0

    def zero(self):
        self.current_pulse = 0
        self.target_pulse = 0

    def step(self):
        if self.current_pulse != self.target_pulse:
            self.step_pin.value(1)
            time.sleep_us(450)
            self.step_pin.value(0)
            time.sleep_us(450)
            self.current_pulse += -1 if self.current_direction == 0 else 1

    def set_target(self, target_pulse):
        if target_pulse < self.current_pulse:
            self.dir_pin.value(0)
            self.current_direction = 0
        else:
            self.dir_pin.value(1)
            self.current_direction = 1
        self.target_pulse = target_pulse
        
    def set_and_move(self, target_pulse):
        self.set_target(target_pulse)
        while self.has_more_steps():
            self.step()

    def has_more_steps(self):
        return self.current_pulse != self.target_pulse

    def increase_target(self, delta):
        self.set_target(self.current_pulse + delta)

    def decrease_target(self, delta):
        self.set_target(self.current_pulse - delta)
