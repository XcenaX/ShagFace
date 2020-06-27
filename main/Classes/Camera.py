import cv2
import numpy as np
from django.http import StreamingHttpResponse
import threading

class Camera(object):
    def __init__(self):
        indexes = self.getCameraIndexes()
        print("INDEXES: ")
        print(indexes)
        self.video = cv2.VideoCapture(indexes[0])
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def getCameraIndexes(self):
        index = 0
        arr = []
        i = 10
        while i > 0:
            cap = cv2.VideoCapture(index)
            if cap.read()[0]:
                arr.append(index)
                cap.release()
            index += 1
            i -= 1
        return arr

    def get_frame(self):
        image = self.frame
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def get_frame_as_image(self):
        image = self.frame
        return image

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()