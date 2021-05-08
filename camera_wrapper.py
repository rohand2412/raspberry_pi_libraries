#!/usr/bin/env python3
"""This script contains all of the modules that are tied to the camera"""

import picamera
from picamera.array import PiRGBArray
import time
import numpy as np
import cv2
from raspberry_pi_libraries import multi_wrapper

class Packages:
    """Encapsulates all classes in this file in case inheritance of these classes is necessary"""

    class Frame:
        """Keeps track of all data regarding the video stream"""
        def __init__(self, name):
            self._width = 640
            self._height = 480
            self._camera = picamera.PiCamera()
            self._camera.resolution = (self._width, self._height)
            self._camera.framerate = 32
            self._camera.start_preview()
            time.sleep(0.1)
            self._camera.stop_preview()
            self._name = name
            self._frame = np.empty((self._height, self._width, 3), dtype=np.uint8)

        def capture_frame(self):
            """Reads the frame from the video stream"""
            try:
                self._camera.capture(self._frame, format="bgr", use_video_port=True)
            except:
                raise multi_wrapper.Packages.Break()

        def preprocessing(self):
            """Preprocesses the frame"""

        def imshow(self):
            """Displays the frame"""
            cv2.imshow(self._name, self._frame)

        def update(self):
            """Checks certain break conditions and updates certain variables"""

        def get_name(self):
            """Returns name of the camera"""
            return self._name

        def get_camera(self):
            """Returns video stream object"""
            return self._camera

        def get_width(self):
            """Returns raw width of frame"""
            return self._width

        def get_height(self):
            """Returns raw height of frame"""
            return self._height
        
        def get_frame(self):
            """Returns raw frame"""
            return self._frame
