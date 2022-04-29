from Kinematics import Kinematics
from Stepper import Stepper
from machine import Pin
import time

class Arms:
    def __init__(self):
        self.stepsPerMM = 314.96
        self.kinematics = Kinematics()
        self.upperCartPosition = 0
        self.lowerCartPosition = 0
        self.upperCartAngle = 0
        self.lowerCartAngle = 0
        self.effectorPosition = [0, 0]
        self.upper = Stepper(26, 16)
        self.lower = Stepper(25, 27)
        self.upper_limit = Pin(39, Pin.IN)
        self.lower_limit = Pin(36, Pin.IN)

    def get_state(self):
        return {
            'upperSteps': self.upper.current_pulse,
            'lowerSteps': self.lower.current_pulse,
            'upperArmDistance': self.upperCartPosition,
            'lowerArmDistance': self.lowerCartPosition,
            'upperCartAngle': self.upperCartAngle,
            'lowerCartAngle': self.lowerCartAngle,
            'effectorPosition': self.effectorPosition
        }
    
    def move_both(self, steps):
        self.upper.increase_target(steps)
        self.lower.increase_target(steps)
        while self.upper.has_more_steps() or self.upper.has_more_steps():
            self.upper.step()
            self.lower.step()

    def move_upper(self, steps):
        self.upper.set_target(self.upper.current_pulse + steps)
        self.step_till_settled()
        
    def move_lower(self, steps):
        self.lower.set_target(self.lower.current_pulse + steps)
        self.step_till_settled()

    def zero(self):
        self.upper.zero()
        self.lower.zero()

    def get_config(self):
        return self.kinematics.get_config()

    def step_till_settled(self):
        while self.upper.has_more_steps() or self.lower.has_more_steps():
            self.upper.step()
            self.lower.step()

    def extend(self, millimeters):
        [upper, lower] = self.get_cart_positions(self.effectorPosition[0] + millimeters, self.effectorPosition[1])
        self.upper.set_target(upper)
        self.lower.set_target(lower)
        self.step_till_settled()

    def retract(self, millimeters):
        [upper, lower] = self.get_cart_positions(self.effectorPosition[0] - millimeters, self.effectorPosition[1])
        self.upper.set_target(upper)
        self.lower.set_target(lower)
        self.step_till_settled()

    def move_pick_to(self, x, y):
        [upper, lower] = self.get_cart_positions(x, y)
        print('Moving carts to', upper, lower)
        print(self.get_state())
        self.upper.set_target(upper)
        self.lower.set_target(lower)
        self.step_till_settled()

    def get_cart_positions(self, x, y):
        y *= -1
        position_calc = self.kinematics.get_cart_positions(x, y)

        if position_calc is None:
            return None

        if position_calc['upper']['distance'] < 0 or position_calc['lower']['distance'] < 0:
            print('[get_cart_deltas] Can not move there')
            print(position_calc['upper']['distance'], position_calc['lower']['distance'])
            #return [self.upper.current_pulse, self.lower.current_pulse]

        # Movement has happened or is happening?
        self.upperCartAngle = position_calc['upper']['angle']
        self.lowerCartAngle = position_calc['lower']['angle']
        self.effectorPosition = [x, y]

        return [
            int(position_calc['upper']['distance'] * self.stepsPerMM),
            int(position_calc['lower']['distance'] * self.stepsPerMM)
        ]

    def home(self):
        print('Robot Homing')
        upper_offset = 0
        lower_offset = 0

        while self.upper_limit.value() == 0 or self.lower_limit.value() == 0:
            self.move_upper(10)
            self.move_lower(10)

        # move pick tip back to 0
        upper_homed = False
        lower_homed = False
        while upper_homed is False or lower_homed is False:
            if upper_homed is False:
                self.upper.decrease_target(1)
                self.upper.step()
            
            if lower_homed is False:
                self.lower.decrease_target(1)
                self.lower.step()

            # Todo: add in homing switches
            if upper_homed is False and self.upper_limit.value() == 0:
                time.sleep_ms(30)
                upper_homed = self.upper_limit.value() == 0
            if lower_homed is False and self.lower_limit.value() == 0:
                time.sleep_ms(30)
                lower_homed = self.lower_limit.value() == 0
                
        self.move_upper(upper_offset)
        self.move_lower(lower_offset)

        # pull back at same time till home switch tripped
        home_state = self.kinematics.get_cart_positions(0, 0)
        self.effectorPosition = [0, 0]
        self.upperCartPosition = 0
        self.lowerCartPosition = 0
        self.upper.zero()
        self.lower.zero()
        self.upperCartAngle = home_state['upper']['angle']
        self.lowerCartAngle = home_state['lower']['angle']
        print('Homing complete')
    
    def go_to_back(self):
        self.home()
        moves = [
            (1.5, 0),
            (1.5, -1),
            (11, -1)
        ]
        for move in moves:
            self.move_pick_to(move[0], move[1])
    
    def rake(self):
        self.move_pick_to(11, 3)
        self.move_pick_to(1, 3)