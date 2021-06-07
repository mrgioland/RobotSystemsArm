import sys

sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import threading

import Camera
from LABConfig_mark import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *


class moveClass():
    def __init__(self, target_color='None'):
        self.target_color = target_color
        self.start_pick_up = True
        self.first_move = True
        self.world_X, self.world_Y = 0, 0
        self.world_x, self.world_y = 0, 0
        self.rotation_angle = 0
        self.servo1 = 500
        self.detect_color = target_color
        self.coordinate = {
            'red': (-15 + 0.5, 12 - 0.5, 1.5),
            'green': (-15 + 0.5, 6 - 0.5, 1.5),
            'blue': (-15 + 0.5, 0 - 0.5, 1.5),
            'yellow': (15 + 0.5, 1 - 0.5, 10),
        }

    def initMove(self):
        AK = ArmIK()

        Board.setBusServoPulse(1, self.servo1 - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)

    def stopMove(self):
        AK = ArmIK()

        Board.setBusServoPulse(1, self.servo1 - 70, 300)
        time.sleep(0.5)
        Board.setBusServoPulse(2, 500, 500)
        AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
        time.sleep(1.5)
        time.sleep(0.01)

    def move(self):
        unreachable = False
        track = False
        __isRunning = True
        AK = ArmIK()

        while True:
            # print(self.world_X, self.world_Y)

            if self.detect_color != 'None' and self.start_pick_up:
                self.set_rgb(self.detect_color)
                # pickup block
                action_finish = False
                Board.setBusServoPulse(1, self.servo1 - 280, 500)

                servo2_angle = getAngle(self.world_X, self.world_Y, self.rotation_angle)
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

                # move block to end goal location
                result = AK.setPitchRangeMoving(
                    (self.coordinate[self.detect_color][0], self.coordinate[self.detect_color][1], 12), -90, -90, 0)
                time.sleep(result[2] / 1000)

                if not __isRunning:
                    continue
                servo2_angle = getAngle(self.coordinate[self.detect_color][0], self.coordinate[self.detect_color][1],
                                        -90)
                Board.setBusServoPulse(2, servo2_angle, 500)
                time.sleep(0.5)

                if not __isRunning:
                    continue
                AK.setPitchRangeMoving(
                    (self.coordinate[self.detect_color][0], self.coordinate[self.detect_color][1], self
                     .coordinate[self.detect_color][2] + 3),
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
                AK.setPitchRangeMoving(
                    (self.coordinate[self.detect_color][0], self.coordinate[self.detect_color][1], 12), -90, -90, 0,
                    800
                    )
                time.sleep(0.8)

                self.initMove()
                time.sleep(1.5)

                self.detect_color = 'None'
                self.first_move = True
                get_roi = False
                action_finish = True
                self.start_pick_up = False
                self.set_rgb(self.detect_color)

                if action_finish:
                    print('move complete')
                    return

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
        elif color == "yellow":
            Board.RGB.setPixelColor(0, Board.PixelColor(255, 255, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(255, 255, 0))
            Board.RGB.show()
        else:
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
            Board.RGB.show()


class PerceptionClass():
    def __init__(self, target_color='yellow'):
        self.target_color = target_color
        self.color = 'None'
        self.size = (640, 480)
        self.rotation_angle = 0
        self.unreachable = False
        self.world_X, self.world_Y = 0, 0
        self.world_x, self.world_y = 0, 0
        self.roi = ()
        self.color_list = []
        self.detect_color = 'None'
        self.range_rgb = {
            'red': (0, 0, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'yellow': (210, 153, 16),
        }
        self.draw_color = self.range_rgb["black"]
        self.objDetected = False
        self.start_pick_up = True
        self.start_count_t1 = False

    def locateItem(self, img, targetColor='yellow'):
        last_x = 0
        last_y = 0
        t1 = 0
        center_list = []
        start_count_t1 = True
        count = 0

        self.set_rgb(targetColor)
        self.target_color = targetColor

        # initial frame processing
        img_copy = img.copy()
        img_h, img_w = img.shape[:2]
        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)

        # frame processing
        frame_resize = cv2.resize(img_copy, self.size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)
        frame_hsv = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2HSV)

        # identify contours
        max_area = 0
        color_area_max = None
        areaMaxContour = 0
        for i in color_range:
            if i in self.target_color:
                frame_mask_lab = cv2.inRange(frame_lab, color_range[i][0], color_range[i][1])
                frame_mask_hsv = cv2.inRange(frame_hsv, color_range[i][0], color_range[i][1])  # 对原图像和掩模进行位运算
                frame_mask_gb = cv2.inRange(frame_gb, color_range[i][0], color_range[i][1])  # 对原图像和掩模进行位运算
                frame_mask = frame_mask_gb

                # if i == 'yellow':
                #    print(color_range[i][0])
                #    print(color_range[i][1])
                #    return frame_mask_gb
                opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))
                closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))
                contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]
                areaMaxContour, area_max = self.getAreaMaxContour(contours)
                if areaMaxContour is not None:
                    if area_max > max_area:
                        max_area = area_max
                        color_area_max = i
                        areaMaxContour_max = areaMaxContour

        print(max_area)
        # identify object if big enough
        if max_area > 2500:
            rect = cv2.minAreaRect(areaMaxContour_max)
            box = np.int0(cv2.boxPoints(rect))

            self.roi = getROI(box)

            img_centerx, img_centery = getCenter(rect, self.roi, self.size, square_length)
            self.world_x, self.world_y = convertCoordinate(img_centerx, img_centery, self.size)

            cv2.drawContours(img, [box], -1, self.range_rgb[color_area_max], 2)
            cv2.putText(img, '(' + str(self.world_x) + ',' + str(self.world_y) + ')',
                        (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.range_rgb[color_area_max], 1)
            distance = math.sqrt(pow(self.world_x - last_x, 2) + pow(self.world_y - last_y, 2))
            last_x, last_y = self.world_x, self.world_y

            # color mapping, create color_list
            if True:
                if color_area_max == 'red':
                    color = 1
                elif color_area_max == 'green':
                    color = 2
                elif color_area_max == 'blue':
                    color = 3
                elif color_area_max == 'yellow':
                    color = 4
                else:
                    color = 0
                self.color_list.append(color)

                if True:
                    count += 1
                    center_list.extend((self.world_x, self.world_y))
                    if self.start_count_t1:
                        self.start_count_t1 = False
                        t1 = time.time()
                    if True:
                        # if time.time() - t1 > 1:
                        rotation_angle = rect[2]
                        self.start_count_t1 = True
                        self.world_X, self.world_Y = np.mean(np.array(center_list).reshape(count, 2), axis=0)
                        self.objDetected = True

                        center_list = []
                        count = 0
                        self.start_pick_up = True
                else:
                    t1 = time.time()
                    self.start_count_t1 = True
                    center_list = []
                    count = 0

                if len(self.color_list) == 3:
                    color = int(round(np.mean(np.array(self.color_list))))
                    color_list = []
                    if color == 1:
                        self.detect_color = 'red'
                        self.draw_color = self.range_rgb["red"]
                    elif color == 2:
                        self.detect_color = 'green'
                        self.draw_color = self.range_rgb["green"]
                    elif color == 3:
                        self.detect_color = 'blue'
                        self.draw_color = self.range_rgb["blue"]
                    elif color == 4:
                        self.detect_color = 'yellow'
                        self.draw_color = self.range_rgb["yellow"]
                    else:
                        self.detect_color = 'None'
                        self.draw_color = self.range_rgb["black"]
        else:
            if not self.start_pick_up:
                self.draw_color = (0, 0, 0)
                self.detect_color = "None"

        cv2.putText(img, "Color: " + self.detect_color, (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                    self.draw_color, 2)
        return img

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
        elif color == "yellow":
            Board.RGB.setPixelColor(0, Board.PixelColor(255, 255, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(255, 255, 0))
            Board.RGB.show()
        else:
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
            Board.RGB.show()

    def getAreaMaxContour(self, contours):
        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None

        for c in contours:
            contour_area_temp = math.fabs(cv2.contourArea(c))
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp
                if contour_area_temp > 300:
                    area_max_contour = c

        return area_max_contour, contour_area_max


if __name__ == "__main__":
    tmp = PerceptionClass()
    m = moveClass()

    th = threading.Thread(target=m.move)
    th.setDaemon(True)
    th.start()

    my_camera = Camera.Camera()
    my_camera.camera_open()

    # tmp.targetColor = ('red', 'green', 'blue')
    tmp.targetColor = ('yellow')

    while True:
        print('tick')
        img = my_camera.frame
        if img is not None:
            frame = img.copy()
            # Frame = tmp.locateItem(frame, ('red', 'green', 'blue'))
            Frame = tmp.locateItem(frame, ('yellow'))
            m.detect_color = tmp.detect_color
            m.world_X = tmp.world_x
            m.world_x = tmp.world_x
            m.world_Y = tmp.world_y
            m.world_y = tmp.world_y
            m.rotation_angle = tmp.rotation_angle
            print(tmp.objDetected)
            if tmp.objDetected:
                print('object detected')
                # m.move()
                tmp.objDetected = False
            cv2.imshow('Frame', Frame)
        key = cv2.waitKey(1)
        if key == 27:
            break
    my_camera.camera_close()
    cv2.destroyAllWindows()
