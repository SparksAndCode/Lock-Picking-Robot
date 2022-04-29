import math


class Kinematics:
    def __init__(self):
        self.j = 0  # cart offset
        self.R = 49.426  # distance to center between arms
        self.L = 60  # arm length
        self.r = 7  # arms to effector center
        self.minArmAngle = 20
        self.maxArmAngle = 70
        self.linearRailLength = 137
        self.pickPivot = 47.879
        self.pickTip = 21.515
        self.pickLength = self.pickTip + self.pickPivot
        self.xHomeOffset = math.sqrt(self.L ** 2 - (self.R - self.r) ** 2)
        print('Kinematics loaded: HomeOffset = ', self.xHomeOffset)

    def get_config(self):
        return {
            'cartOffset': self.j,
            'armDistance': self.R * 2,
            'armLength': self.L,
            'effectorHeight': self.r,
            'linearRailLength': self.linearRailLength
        }

    def get_cart_positions(self, x, y):
        x -= self.xHomeOffset

        lower_b = self.R + y - self.r
        lower_a = math.sqrt(self.L ** 2 - lower_b ** 2)

        upper_b = (self.R * 2) - (self.R + y + self.r)
        upper_a = math.sqrt(self.L ** 2 - upper_b ** 2)

        upper_angle = math.asin((upper_a * math.sin(90)) / self.L) * (180 / math.pi)
        lower_angle = math.asin((lower_a * math.sin(90)) / self.L) * (180 / math.pi)

        if upper_angle > self.maxArmAngle or lower_angle > self.maxArmAngle:
            print('Angle to large: > ', self.maxArmAngle)
            print(upper_angle, lower_angle)
            return None

        if upper_angle < self.minArmAngle or lower_angle < self.minArmAngle:
            print('[GetCartPositions] Angle to acute: < ', self.minArmAngle)
            print(upper_angle, lower_angle)
            return None

        target_upper_distance = upper_a + x
        target_lower_distance = lower_a + x

        if target_upper_distance > self.linearRailLength or target_lower_distance > self.linearRailLength:
            print('OutOfBounds on the Rails')
            print(target_upper_distance, target_lower_distance)
            return None

        return {
            'upper': {
                'angle': upper_angle,
                'distance': target_upper_distance
            },
            'lower': {
                'angle': lower_angle,
                'distance': target_lower_distance
            }
        }
