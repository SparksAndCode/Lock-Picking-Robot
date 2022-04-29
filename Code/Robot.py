from Waist import Waist
from Arms import Arms
import time

class Robot:
    def __init__(self):
        self.arms = Arms()
        self.waist = Waist()
        
    def pick_rake(self):
        self.arms.go_to_back()
        pin_bind_tension = 0.25
        self.waist.set_tension(pin_bind_tension, hold=False)
        print('Holding while lock is being picked')
        self.arms.rake()
        self.waist.set_tension(0.75, hold=False, step_limit=1500)


    def pick_single(self):
        # how far from the tip of the key each pin is
        pin_positions = [
            1.5,
            1.75,
            2.75,
            4.5
        ]
        pick_offset = 1.5 # how far back is triangle from the tip

        self.arms.go_to_back() # send pick to back bottom of lock
        [workspace_x, workspace_y] = self.arms.effectorPosition # store relative position so we can move to pins from there
        print('Back Position', workspace_x, workspace_y)
        pin_bind_tension = 0.2 # tension required on plug for pins to be set
        self.waist.set_tension(pin_bind_tension, hold=False)
        print('Lock Under Tension')
        picking = True
        pin_set_tension = pin_bind_tension * 0.9 # value to watch for to detect if pins are set
        while picking:
            for pin in range(len(pin_positions)):
                rel_x = pin_positions[pin]
                print('Attempting to pick pin:', pin)
                temp_x = workspace_x - rel_x + pick_offset
                print('Moving to', temp_x, workspace_y)
                self.arms.move_pick_to(temp_x, workspace_y) # move to pin
                time.sleep_ms(500)
                print('Moving to', temp_x, 2.5)
                self.arms.move_pick_to(temp_x, 2.5) # push up on pin
                time.sleep_ms(500)
                print('Moving to', temp_x, workspace_y)
                self.arms.move_pick_to(temp_x, workspace_y) # got back to bottom
            
                print('Taking tension measurement')        
                measurement = self.waist.hx711.get_units()
                print('Measurement', measurement, pin_set_tension)
                if measurement < pin_set_tension:
                    print('Pins Set State Detected')
                    picking = False
                    break
                else:
                    print('Pins not set')
            self.arms.move_pick_to(temp_x, workspace_y)
        self.arms.home()
        self.waist.set_tension(0.75, hold=False, step_limit=1500)
        self.waist.stepper.set_and_move(0)
        
    def reset(self):
        self.waist.stepper.decrease_target(1700)
        while self.waist.stepper.has_more_steps():
            self.waist.stepper.step()     
