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

        image = np.expand_dims(image, axis=0).astype(np.float32)

        self._interpreter.set_tensor(self._input_index, image)
        self._interpreter.invoke()

        if self._mode == self.REGRESSION:
            return self._interpreter.get_tensor(self._output_index)[0][0]
        elif self._mode == self.OBJECT_DETECTION:
            boxes = self._interpreter.get_tensor(self._output_details[0]['index'])
            classes = self._interpreter.get_tensor(self._output_details[1]['index'])
            scores = self._interpreter.get_tensor(self._output_details[2]['index'])
            num = self._interpreter.get_tensor(self._output_details[3]['index'])

            return {'boxes': boxes[0], 'classes': classes[0], 'scores': scores[0], 'num': num[0]}