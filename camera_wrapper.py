# Copyright (C) 2022  Rohan Dugad
#
# Contact info:
# https://docs.google.com/document/d/17IhBs4cz7FXphE0praCaWMjz016a7BFU5IQbm1CNnUc/edit?usp=sharing
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
        def __init__(self, name, img_format="bgr"):
            self._format = img_format
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
                self._camera.capture(self._frame, format=self._format, use_video_port=True)
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
