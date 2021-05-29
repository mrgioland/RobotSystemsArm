
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
except: a='nop e'


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
                result = AK.setPitchRangeMoving((sel
                    f.coordinate[self.detect_color][0], self.coordinate[self.detect_color][1], 12), -90,
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
                AK.setPitchRangeMoving((se
                    lf.coordinate[self.detect_color][0], self.coordinate[self.detect_color][1], 12), -90, -90, 0,
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
        else:
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0,


0, 0))
            Board.RGB.show()

class PerceptionClass():
    def __init__(self, target_color='None'):
        self.target_color = target_color
        self.color = 'None'
        self.size = (640, 480)
        self.rotation_angle = 0
        self.unreachable = False
        self.world_X, self.world_Y = 0, 0
        self.world_x, self.world_y = 0, 0
        self.roi = ()
        self.detect_color = 'None'
        self.range_rgb = {
            'red': (0, 0, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'darkYellow': (210, 153, 16),
        }
        self.objDetected = False


    def locateItem(self, img, targetColor='red'):
        last_x = 0
        last_y = 0
        t1 = 0
        center_list = []
        start_count_t1 = True
        count = 0
        world_x, world_y = 0, 0

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

        # identify contours
        area_max = 0
        areaMaxContour = 0
        # print(color_range)
        for i in color_range:
            # print(self.target_color)
            if i in self.target_color:
                self.detect_color = i
                frame_mask = cv2.inRange(frame_l
                                         b, color_range[self.detect_color][0], color_range[self.detect_color][1])
                opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))
                closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))
                contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]
                areaMaxContour, area_max = self.getAreaMaxContour(contours)

        # print(area_max)
        # identify contours on image
        if area_max > 2500:
            rect = cv2.minAreaRect(areaMaxContour)
            box = np.int0(cv2.boxPoints(rect))

            self.roi = getROI(box)

            img_centerx, img_centery = getCenter(rect, self.roi, self.size, square_length)
            self.world_x, self.world_y = convertCoordinate(img_centerx, img_centery, self.size)

            cv2.drawContours(img, [box], -1, self.range_rgb[self.detect_color], 2)
            cv2.putText(img, '(' + str(self.world_x) + ',' + str(self.world_y) + ')',
                        (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.range_rgb[self.detect_color], 1)
            distance = math.sqrt(pow(self.world_x - last_x, 2) + pow(self.world_y - last_y, 2))
            last_x, last_y = self.world_x, self.world_y

            if distance < 0.3:
                center_list.extend((self.world_x, self.world_y))
                count += 1
                if start_count_t1:
                    start_count_t1 = False
                    t1 = time.time()
                # if time.time() - t1 > 1.5:
                if time.time() - t1 > 0:
                    self.rotation_angle = rect[2]
                    start_count_t1 = True
                    self.world_X, self.world_Y = np.mean(np.array(center_list).reshape(count, 2), axis=0)
                    self.objDetected = True
                    count = 0
                    center_list = []
                    start_pick_up = True
            else:
                t1 = time.time()
                start_count_t1 = True
                count = 0
                center_list = []

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

    tmp.targetColor = ('red', 'green', 'blue')
    while True:
        print('tick')
        img = my_camera.frame
        if img is not None:
            frame = img.copy()
            Frame = tmp.locateItem(frame, ('red', 'green', 'blue'))
            m.detect_color = tmp.detect_color
            m.world_X = tmp.world_x
            m.world_x = tmp.world_x
            m.world_Y = tmp.world_y
            m.world_y = tmp.world_y
            m.rotation_angle = tmp.rotation_angle
            if tmp.objDetected:
                print('object detected')
                m.move()
                tmp.objDetected = False
            cv2.imshow('Frame', Frame)
        key = cv2.waitKey(1)
        if key == 27:
            break
    my_camera.camera_close()
    cv2.destroyAllWindows()



