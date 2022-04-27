import cv2
import numpy as np
class VideoCamera(object):
    def __init__(self,camera_id=0):
        #self.cap = cv2.VideoCapture(camera_id)
    def __del__(self):
        self.cap.release()
    def get_frame(self):
        #ret, frame = self.cap.read()
        #frame_flip = cv2.flip(frame, 1)
        #ret, frame = cv2.imencode('.jpg', frame_flip)
        return frame.tobytes()