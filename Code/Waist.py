from Stepper import Stepper
from hx711 import HX711
from machine import Pin, SPI
import time

class Waist:
    def __init__(self):
        # Stepper Config
        self.stepper = Stepper(17, 14)

        # Load Cell Config
        self.pin_OUT = Pin(19, Pin.IN, pull=Pin.PULL_DOWN)
        self.pin_SCK = Pin(23, Pin.OUT)
        self.spi_SCK = Pin(5)

        self.spi = SPI(1, baudrate=1000000, polarity=0,
                  phase=0, sck=self.spi_SCK, mosi=self.pin_SCK, miso=self.pin_OUT)

        self.hx711 = HX711(self.pin_SCK, self.pin_OUT, self.spi)

        self.hx711.set_gain(128)
        self.hx711.set_scale(-1850105.0)
        self.hx711.set_offset(103893.1)
    
    def zero(self):
        print('Zero out scale')
        self.hx711.tare()
        print('Offset set')
        print(self.hx711.OFFSET)

    def calibrate(self, scale, target, count=10):
        print('reading')
        value = self.hx711.get_value()
        calibrate_value = value / scale
        print('Value:', value)
        print('Units:', calibrate_value)
        new_scale = value / target
        print('New Target Scale:', new_scale)
        return new_scale
    
    def get_avg_torque(self, reads=1):
        measurements = []
        for x in range(reads):
            measurements.append(self.hx711.get_units())
        return sum(measurements) / reads
    
    def read_loop(self):
        while True:
            measurement = self.hx711.get_units()
            print(measurement)

    def set_tension(self, torque, hold=True, step_limit=None):
        torque_range = torque * 0.1
        high_window = torque + (torque_range / 2)
        low_window = torque - (torque_range / 2)
        steps = 0
        print(torque, low_window, high_window)
        while True:
            measurement = self.hx711.get_units() #get_avg_torque()
            direction = -1 if measurement < torque else 1
            if measurement < low_window or measurement > high_window:
                if torque == 0:
                    error = measurement
                    step_count = 20
                    if measurement < 0:
                        return
                else:
                    error = abs(measurement / torque)
                
                    if error < 0.2:
                        step_count = 40
                    elif error < 0.4:
                        step_count = 20
                    elif error < 0.6:
                        step_count = 10
                    else:
                        step_count = 1
                print('in window', step_count, direction)
                self.stepper.increase_target(step_count * direction)    
                while self.stepper.has_more_steps():
                    self.stepper.step()
                    steps += 1
                    
                    if step_limit is not None and steps >= step_limit:
                        print('Step Limit Reached')
                        return
            else:
                if hold is False:
                    return steps
            #print(low_window, measurement, high_window)

    def pick_assist(self):
        pin_bind_tension = 0.2
        self.set_tension(pin_bind_tension, hold=False)
        print('Holding while lock is being picked')
        measurement = self.hx711.get_units()
        pin_set_tension = pin_bind_tension * 0.9
        while measurement > pin_set_tension:
            measurement = self.hx711.get_units()
            time.sleep(0.2)
            print(measurement, pin_set_tension)
        print('Pins Set Detected')
        self.set_tension(0.5, hold=False, step_limit=1400)
