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
"""Model Utilities Library"""

import numpy as np
import tflite_runtime.interpreter as tflite
import cv2

class ModelWrapper:
    """Class containing usage methods of the TFLite model"""
    OBJECT_DETECTION = "object_detection"
    REGRESSION = "regression"

    def __init__(self, model_path, mode):
        self._model_path = model_path
        self._mode = mode

        self._interpreter = tflite.Interpreter(model_path=self._model_path)
        self._interpreter.allocate_tensors()

        self._input_index = self._interpreter.get_input_details()[0]['index']
        self._output_details = self._interpreter.get_output_details()
        self._output_index = self._output_details[0]['index']

        _, self._input_height, self._input_width, _ = self._interpreter.get_input_details()[0]['shape']

    def run_inference(self, raw_image):
        """Invokes interpreter on image"""
        image = cv2.resize(raw_image, (self._input_width, self._input_height))

        if self._mode == self.REGRESSION:
            image = np.expand_dims(image, axis=0).astype(np.float32)
        elif self._mode == self.OBJECT_DETECTION:
            image = np.round(np.expand_dims(image, axis=0)).astype(np.uint8)

        self._interpreter.set_tensor(self._input_index, image)
        self._interpreter.invoke()

        if self._mode == self.REGRESSION:
            return self._interpreter.get_tensor(self._output_index)[0][0]
        elif self._mode == self.OBJECT_DETECTION:
            boxes = self._interpreter.get_tensor(self._output_details[0]['index'])[0]
            classes = self._interpreter.get_tensor(self._output_details[1]['index'])[0]
            scores = self._interpreter.get_tensor(self._output_details[2]['index'])[0]
            num = self._interpreter.get_tensor(self._output_details[3]['index'])[0]

            return {'boxes': boxes, 'classes': classes, 'scores': scores, 'num': num}

    def get_box(self, box):
        return ((int(box[1] * self._input_width),
                 int(box[0] * self._input_height)),
                (int(box[3] * self._input_width),
                 int(box[2] * self._input_height)))