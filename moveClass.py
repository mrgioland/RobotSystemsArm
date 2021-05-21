import sys

sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import threading

try:
    import Camera
    from LABConfig import *
    from ArmIK.Transform import *
    from ArmIK.ArmMoveIK import *
    import HiwonderSDK.Board as Board
    from CameraCalibration.CalibrationConfig import *
except:
    a='nothing'


class moveClass():
    def __init__(self, target_color='None'):
        self.target_color = target_color
        self.start_pick_up = True
        self.first_move = True
        self.world_X, self.world_Y = 0, 0
        self.world_x, self.world_y = 0, 0
        self.servo1 = 500
        self.detect_color = target_color
        self.coordinate = {
            'red': (-15 + 0.5, 12 - 0.5, 1.5),
            'green': (-15 + 0.5, 6 - 0.5, 1.5),
            'blue': (-15 + 0.5, 0 - 0.5, 1.5),
        }

    def initMove(self):
        Board.setBusServoPulse(1, self.servo1 - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)

    def stopMove(self):
        Board.setBusServoPulse(1, self.servo1 - 70, 300)
        time.sleep(0.5)
        Board.setBusServoPulse(2, 500, 500)
        AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
        time.sleep(1.5)
        time.sleep(0.01)

    def move(self):
        unreachable = False
        track = False
        rotation_angle = 0
        __isRunning = True

        while True:
            if self.detect_color != 'None' and self.start_pick_up:
                self.set_rgb(self.detect_color)

                #pickup block
                action_finish = False
                Board.setBusServoPulse(1, self.servo1 - 280, 500)

                servo2_angle = getAngle(self.world_X, self.world_Y, rotation_angle)
                Board.setBusServoPulse(2, servo2_angle, 500)
                time.sleep(0.8)

                if not __isRunning:
                    continue
                AK.setPitchRangeMoving((self.world_X, self.world_Y, 2), -90, -90, 0, 1000)
                time.sleep(2)

                if not __isRunning:
                    continue
                Board.setBusServoPulse(1, self.servo1, 500)
                time.sleep(1)

                if not __isRunning:
                    continue
                Board.setBusServoPulse(2, 500, 500)
                AK.setPitchRangeMoving((self.world_X, self.world_Y, 12), -90, -90, 0, 1000)
                time.sleep(1)

                if not __isRunning:
                    continue

                #move block to end goal location
                result = AK.setPitchRangeMoving((self.coordinate[self.detect_color][0], self.coordinate[self.detect_color][1], 12), -90,
                                                -90, 0)
                time.sleep(result[2] / 1000)

                if not __isRunning:
                    continue
                servo2_angle = getAngle(self.coordinate[self.detect_color][0], self.coordinate[self.detect_color][1], -90)
                Board.setBusServoPulse(2, servo2_angle, 500)
                time.sleep(0.5)

                if not __isRunning:
                    continue
                AK.setPitchRangeMoving(
                    (self.coordinate[self.detect_color][0], self.coordinate[self.detect_color][1], self.coordinate[self.detect_color][2] + 3),
                    -90, -90, 0, 500)
                time.sleep(0.5)

                if not __isRunning:
                    continue
                AK.setPitchRangeMoving((self.coordinate[self.detect_color]), -90, -90, 0, 1000)
                time.sleep(0.8)

                if not __isRunning:
                    continue
                Board.setBusServoPulse(1, self.servo1 - 200, 500)
                time.sleep(0.8)

                if not __isRunning:
                    continue
                AK.setPitchRangeMoving((self.coordinate[self.detect_color][0], self.coordinate[self.detect_color][1], 12), -90, -90, 0,
                                       800)
                time.sleep(0.8)

                self.initMove()
                time.sleep(1.5)

                self.detect_color = 'None'
                self.first_move = True
                get_roi = False
                action_finish = True
                self.start_pick_up = False
                self.set_rgb(self.detect_color)




    def set_rgb(self, color):
        if color == "red":
            Board.RGB.setPixelColor(0, Board.PixelColor(255, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(255, 0, 0))
            Board.RGB.show()
        elif color == "green":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 255, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 255, 0))
            Board.RGB.show()
        elif color == "blue":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 255))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 255))
            Board.RGB.show()
        else:
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
            Board.RGB.show()







    def test(self):
        return 1


if __name__ == "__main__":
    tmp = moveClass()






