from Robot import Robot

pins = [
    6.9088,
    6.5151,
    6.1214,
    5.7277,
    5.334,
    4.9403,
    4.5466,
    4.1529
]

pin_positions = [
    4.1148,
    5.3848,
    6.6548,
    7.9248
]

def pick_lock():
    print('Booting Up')

    robot = Robot()
    # robot.home()

    for pin_position in pin_positions:
        robot.move_pick_to(pin_position, 0)
        for pin in pins:
            robot.move_pick_to(pin_position, pin)
        robot.move_pick_to(pin_position, 0)
