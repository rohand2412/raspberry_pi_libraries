#!/usr/bin/env python3
"""This script contains all of the base modules used in this directory"""

import os
import datetime
import time
import queue
import string
import argparse
import numpy as np
import cv2
import pynput
import re

class Packages:
    """Contains basic framework of all modules utilized in this directory"""
    KEYBOARD_PRESSED_STATE = True
    KEYBOARD_RELEASED_STATE = False
    KEYBOARD_ACTION_TYPE_TAP = "tap"
    KEYBOARD_ACTION_TYPE_HOLD = "hold"
    READDIR_SLIDESHOW_MODE_KEYBOARD = "keyboard"
    READDIR_SLIDESHOW_MODE_DELAY = "delay"

    @staticmethod
    def check_for_quit_request():
        """Quits if 'q' key is pressed"""
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(end="")
            raise Packages.Break()

    class Break(Exception):
        """Emulates a break from within a function"""

    class TimerError(Exception):
        """Used to report errors from Timer class"""

    class ArguementError(Exception):
        """Used to report errors from InitBashArgs class"""

    class DirectoryManagement:
        """Manages the directory and has classes to write and read directories"""
        class WriteDir:
            """Class with methods to add more directories with similar naming conventions"""
            def __init__(self, target_dir, first_dir_name):
                self._target_dir = target_dir
                self._first_dir_name = first_dir_name
                self._names = []
                self._nums = []
                self._most_recent_dir = self._MostRecentDir()
                self._new_folder = None
                os.chdir(target_dir)

            def add(self):
                """Follows naming conventions of the first directory and adds another one"""
                self._names = os.listdir(self.get_target_dir())
                self._nums = []
                self._new_folder = None
                if self._names:
                    self._names = np.sort(self._names)
                    self._nums = []
                    for name in self._names:
                        self._nums = np.append(self._nums, int(''.join(filter(str.isdigit, name))))
                    self._most_recent_dir.calculate(self._names, self._nums)
                    self._new_folder = (self._most_recent_dir.get_text() +
                                        str(self._most_recent_dir.get_num()+1))
                else:
                    self._new_folder = self.get_first_dir_name()
                os.mkdir(self._new_folder)
                os.chdir(self._new_folder)

            def debug(self, debug):
                """Prints out values of all variables for debugging"""
                if debug:
                    print("names: " + str(self._names))
                    print("nums: " + str(self._nums))
                    self._most_recent_dir.debug(True)
                    print("newFolder: " + str(self._new_folder))

            def get_target_dir(self):
                """Returns the directory that this class with manage"""
                return self._target_dir

            def get_first_dir_name(self):
                """Returns the first directory that was made in the target directory"""
                return self._first_dir_name

            class _MostRecentDir:
                def __init__(self):
                    self._index = None
                    self._name = None
                    self._num = None
                    self._text = None

                def calculate(self, names, nums):
                    """Calculates data on the most recent directory from the names and numbers of
                    all of them"""
                    self._num = np.amax(nums)
                    self._index = int(np.where(nums == self._num)[0])
                    self._name = names[self._index]
                    self._num = int(''.join(filter(str.isdigit, self._name)))
                    self._text = ''.join(filter(str.isalpha, self._name))

                def debug(self, debug):
                    """Prints out values of all variables for debugging"""
                    if debug:
                        print("MostRecentDir: index: " + str(self._index))
                        print("MostRecentDir: name: " + str(self._name))
                        print("MostRecentDir: num: " + str(self._num))
                        print("MostRecentDir: text: " + str(self._text))

                def get_index(self):
                    """Returns the index of the most recent directory"""
                    return self._index

                def get_name(self):
                    """Returns the name of the most recent directory"""
                    return self._name

                def get_num(self):
                    """Returns the number of the most recent directory"""
                    return self._num

                def get_text(self):
                    """Returns the text of the most recent directory"""
                    return self._text

        class ReadDir:
            """Class with methods to read and display from an images directory"""
            def __init__(self, target_dir, mode, delay=250):
                self._keyboard = Packages.Keyboard()
                self._target_dir = target_dir
                self._mode = mode
                self._names = []
                self._digits = []
                self._text = None
                self._ext = None
                self._images = []
                self._img_num = 0
                self._start_delay = None
                self._delay = delay
                self._left_key = "left"
                self._right_key = "right"
                self._left_key_state = Packages.KEYBOARD_RELEASED_STATE
                self._right_key_state = Packages.KEYBOARD_RELEASED_STATE
                self._left_key_action_type = None
                self._right_key_action_type = None
                self._left_tap_update = False
                self._right_tap_update = False

                if self._mode == Packages.READDIR_SLIDESHOW_MODE_KEYBOARD:
                    self._keyboard.start()

            def read(self):
                """Cache or Load and Store the images in the target directory"""
                self._names = os.listdir(self.get_target_dir())
                self._digits = [None for name in self._names]
                self._text, self._ext = os.path.splitext(self._names[0])
                self._text = ''.join(filter(str.isalpha, self._text))
                for i, name in enumerate(self._names):
                    self._digits[i] = int(''.join(filter(str.isdigit, name)))
                self._digits.sort()
                self._names = [self._text + str(digit) + self._ext for digit in self._digits]

                self._images = [None for name in self._names]
                for i, name in enumerate(self._names):
                    self._images[i] = cv2.imread(self._target_dir+name)
                    self._images[i] = cv2.putText(self._images[i], text=str(self._digits[i]),
                                                  org=(0, 25), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                                  fontScale=1, color=(0, 255, 0), thickness=2,
                                                  lineType=cv2.LINE_AA)
                self._images = np.array(self._images)

            def imshow(self):
                """Display the image that is next up in the slideshow"""
                if self._mode == Packages.READDIR_SLIDESHOW_MODE_DELAY:
                    if not self._start_delay:
                        cv2.imshow("slideshow", self._images[self._img_num])
                elif self._mode == Packages.READDIR_SLIDESHOW_MODE_KEYBOARD:
                    cv2.imshow("slideshow", self._images[self._img_num])

            def update(self):
                """Check if delay is completed or if delay needs to be reset"""
                if self._mode == Packages.READDIR_SLIDESHOW_MODE_DELAY:
                    if not self._start_delay:
                        self._img_num += 1
                        if self._img_num >= len(self._images):
                            raise Packages.Break
                        self._start_delay = datetime.datetime.now()
                    elif (datetime.datetime.now() - self._start_delay).total_seconds() >= (self._delay/1000.0):
                        self._start_delay = None
                elif self._mode == Packages.READDIR_SLIDESHOW_MODE_KEYBOARD:
                    self._keyboard.update_events()
                    while not self._keyboard.get_events().empty():
                        event = self._keyboard.get_events().get()
                        if event.get_name() == self._left_key:
                            self._left_key_state = event.get_state()
                            self._left_key_action_type = event.get_action_type()
                        elif event.get_name() == self._right_key:
                            self._right_key_state = event.get_state()
                            self._right_key_action_type = event.get_action_type()

                    if self._left_key_state == Packages.KEYBOARD_PRESSED_STATE and self._img_num > 0:
                        if self._left_key_action_type == Packages.KEYBOARD_ACTION_TYPE_TAP and not self._left_tap_update:
                            self._img_num -= 1
                            self._left_tap_update = True
                        elif self._left_key_action_type == Packages.KEYBOARD_ACTION_TYPE_HOLD:
                            self._img_num -= 1
                    elif self._left_key_state == Packages.KEYBOARD_RELEASED_STATE:
                        self._left_tap_update = False

                    if self._right_key_state == Packages.KEYBOARD_PRESSED_STATE and self._img_num < (len(self._images) - 1):
                        if self._right_key_action_type == Packages.KEYBOARD_ACTION_TYPE_TAP and not self._right_tap_update:
                            self._img_num += 1
                            self._right_tap_update = True
                        elif self._right_key_action_type == Packages.KEYBOARD_ACTION_TYPE_HOLD:
                            self._img_num += 1
                    elif self._right_key_state == Packages.KEYBOARD_RELEASED_STATE:
                        self._right_tap_update = False

            def close(self):
                """Deactivates keyboard if necessary"""
                if self._mode == Packages.READDIR_SLIDESHOW_MODE_KEYBOARD:
                    self._keyboard.stop()

            def get_target_dir(self):
                """Return name of target directory"""
                return self._target_dir

            def get_names(self):
                """Return image filenames"""
                return self._names

            def get_images(self):
                """Return images in the target directory"""
                return self._images

            def get_mode(self):
                """Returns mode of image slideshow"""
                return self._mode

    class Fps:
        """Computes Fps over a series of frames and their times"""
        def __init__(self):
            self._timer = Packages.Timer()
            self._elapsed_times = np.array([])
            self._ms_to_seconds = 1.0/1000000.0
            self._mean = None
            self._fps = None

        def open_timer(self):
            """Starts timer that determines the elapsed time"""
            self._timer.start()

        def close_timer(self):
            """Stops timer that determines the elapsed time"""
            self._timer.stop()
            self._elapsed_times = np.append(self._elapsed_times, self._timer.get_elapsed_time())
            return self._elapsed_times[-1]

        def calculate(self):
            """Calculates the fps based upon a series of stats"""
            self._elapsed_times = np.delete(self._elapsed_times, [0])
            self._mean = np.mean(self._elapsed_times)
            self._fps = 1.0/self._mean

        def print_fps(self):
            """Prints out just fps"""
            print("FPS: " + str(self._fps))

        def debug(self, debug):
            """Prints out values of all variables for debugging"""
            if debug:
                print("elapsedTimes: " + str(self._elapsed_times))
                print("mean: " + str(self._mean))
                print("fps: " + str(self._fps))
                self._timer.debug(debug)

        def get_fps(self):
            """Returns fps"""
            return self._fps

        def time_this(self):
            """Returns an automated timer context manager for usage in 'with' statements"""
            return self._AutomatedTiming(self.open_timer, self.close_timer)

        class _AutomatedTiming:
            """Context Manager that can be used without redefining class instance"""
            def __init__(self, enter_func, exit_func):
                self._enter = enter_func
                self._exit = exit_func

            def __enter__(self):
                self._enter()

            def __exit__(self, exc_type, exc_value, exc_traceback):
                self._exit()

    class Keyboard:
        """Wraps pynput keyboard class and embeds event queue for accesing and organizing key
        events"""
        def __init__(self, len_event_buffers=64):
            self._listener = pynput.keyboard.Listener(on_press=self._on_press,
                                                      on_release=self._on_release)
            self._events = queue.Queue(maxsize=len_event_buffers)
            self._keys = {key_name: self._Key(key_name) for key_name in self.get_key_names()}

        def _on_press(self, key):
            """Callback for when key is pressed"""
            self._produce(Packages.KEYBOARD_PRESSED_STATE, key)

        def _on_release(self, key):
            """Callback for when key is released"""
            self._produce(Packages.KEYBOARD_RELEASED_STATE, key)

        def start(self):
            """Starts listening to the keyboard"""
            self._listener.start()

        def stop(self):
            """Stops listening to the keyboard"""
            self._listener.stop()

        def _produce(self, state, key):
            """Produces key into events queue"""
            key_name = self._Key.name(key)
            try:
                self._keys[key_name].set_state(state)
                self._events.put(self._keys[key_name], block=False)
            except KeyError:
                unknown_key = self._Key(key_name)
                unknown_key.set_state(state)
                self._events.put(unknown_key, block=False)

        def consume(self):
            """Consumes keys in the events queue"""

        @staticmethod
        def get_key_names():
            """Returns string list of all key names including both special keys and letter keys"""
            key_data = list(pynput.keyboard.Key.__dict__.values())
            key_names = np.array([])
            for data in key_data:
                if isinstance(data, list):
                    special_keys = np.array(data)
                    lowercase_alphabet = np.array(list(string.ascii_lowercase),
                                                  dtype=special_keys.dtype)
                    numbers = np.array([str(i) for i in range(10)])
                    key_names = np.concatenate((special_keys, lowercase_alphabet, numbers))
                    break
            return key_names

        def update_events(self):
            """Put new events if key data changed"""
            for key_name in self.get_key_names():
                if self._keys[key_name].get_state():
                    if self._keys[key_name].check_for_action_update():
                        self._events.put(self._keys[key_name], block=False)

        def get_events(self):
            """Returns events queue"""
            return self._events

        class _Key:
            def __init__(self, name):
                self._state = False
                self._name = name
                self._timer = Packages.Timer()
                self._sent_hold_message = False

            @staticmethod
            def name(key):
                """Returns name of key enum if special character or key itself if in alphabet"""
                try:
                    return key.name
                except AttributeError:
                    return key.char

            def set_state(self, state):
                """Sets the state of the key and start and stop the timer"""
                if self._state != state:
                    self._state = state
                    if self._state == Packages.KEYBOARD_PRESSED_STATE:
                        self._timer.start()
                    elif self._state == Packages.KEYBOARD_RELEASED_STATE:
                        self._timer.stop()

            def debug(self, debug):
                """Prints out all stored data for debugging"""
                if debug:
                    print("state: ", self._state)
                    print("name: ", self._name)
                    self._timer.debug(debug)

            def check_for_action_update(self):
                """Check if the action has changed from 'tap' to 'hold'"""
                if self.get_action_type() == Packages.KEYBOARD_ACTION_TYPE_HOLD:
                    if not self._sent_hold_message:
                        self._sent_hold_message = True
                        return True
                else:
                    self._sent_hold_message = False
                return False

            def get_action_type(self):
                """Classify key action as 'tap' or 'hold' based on press duration"""
                tap_duration = 0.15
                elapsed_time = self.get_elapsed_time()
                if elapsed_time <= tap_duration:
                    return Packages.KEYBOARD_ACTION_TYPE_TAP
                else:
                    return Packages.KEYBOARD_ACTION_TYPE_HOLD

            def get_elapsed_time(self):
                """Wraps Timer class' get_elapsed_time method"""
                return self._timer.get_elapsed_time()

            def get_state(self):
                """Returns state of key"""
                return self._state

            def get_name(self):
                """Returns name of key"""
                return self._name

    class Timer:
        """Monitors time to provide elapsed time or activate a callback"""
        def __init__(self, callback=None, delay_ms=None):
            self._start_time = None
            self._elapsed_time = None
            self._callback = callback
            self._delay_ms = delay_ms

        def start(self):
            """Starts Timer"""
            if self._start_time is not None:
                raise Packages.TimerError(f"Timer is already running. Use .stop() to stop it")

            self._start_time = time.perf_counter()

        def stop(self):
            """Stops Timer"""
            if self._start_time is None:
                raise Packages.TimerError(f"Timer is not already running. Use .start() to \
                                                start it")

            self._elapsed_time = time.perf_counter() - self._start_time
            self._start_time = None

        def get_elapsed_time(self):
            """Calculates elapsed time if timer is running or provides already defined value"""
            if self._start_time is not None:
                return time.perf_counter() - self._start_time
            else:
                return self._elapsed_time

        def update(self):
            """Activates callback and resets timer if specified amount of time has passed"""
            if self._callback is None:
                raise Packages.TimerError(f"No callback specified. Please specify in \
                                                constructor")
            if self._delay_ms is None:
                raise Packages.TimerError(f"No delay specified. Please specify in \
                                                constructor")
            if self._start_time is None:
                raise Packages.TimerError(f"Timer is not already running. Cannot check \
                                                elapsed time on inactive Timer.Use.start() to \
                                                start it ")

            if (time.perf_counter() - self._start_time) >= (self._delay_ms / 1000.0):
                self.stop()
                self._callback()
                return True
            else:
                return False

        def debug(self, debug):
            """Prints out all stored data for debugging"""
            if debug:
                print("start_time: ", self._start_time)
                print("elapsed_time: ", self._elapsed_time)
                print("delay_ms: ", self._delay_ms)
                print("callback: ", self._callback)

    class InitBashArgs:
        """Initalizes the arguements present for bash execution which will be different for each
        application of this wrapper"""
        @classmethod
        def __init__(cls):
            cls._parser = argparse.ArgumentParser()
            cls.get_arg_params()
            cls._args = cls._parser.parse_args()

        @classmethod
        def get_arg_params(cls):
            """Returns the argument paramters"""

        @classmethod
        def get_args(cls):
            """Returns data inputted from bash"""
            return cls._args

    class Dataset:
        """Collection of methods regarding dataset manipulation"""
        @staticmethod
        def get_ordered_path(path):
            """Returns list of all items in specified path in numerical order"""
            files = os.listdir(path)
            num_data_types = 3
            files_split = [[None for data_type in range(num_data_types)] \
                           for name in range(len(files))]

            for i, name in enumerate(files):
                text = ''.join(filter(str.isalpha, os.path.splitext(name)[0]))
                num = ''.join(filter(str.isdigit, name))
                ext = os.path.splitext(name)[1]
                files_split[i] = [text, num, ext]

            files_split = np.array(files_split)
            files_ordered = [None for name in range(len(files_split))]
            files_ordered_len = 0
            files_cur_index = 0
            while files_ordered_len < len(files_ordered):
                indices = np.where(files_split[:, 1]==str(files_cur_index))
                if len(indices[0]) == 1:
                    files_ordered[files_ordered_len] = files_split[indices[0][0]][0] \
                                                    + files_split[indices[0][0]][1] \
                                                    + files_split[indices[0][0]][2]
                    files_ordered_len += 1
                elif indices[0].size > 0:
                    while True:
                        print("[ERROR] MULTIPLE DIRECTORIES WITH THE SAME ID")
                files_cur_index += 1

            return files_ordered

        @staticmethod
        def load_label_map(path):
            """
            Loads the labels file. Supports files with or without index numbers.
            From Tensorflow Example Code.
            """
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                labels = {}
                for row_number, content in enumerate(lines):
                    pair = re.split(r'[:\s]+', content.strip(), maxsplit=1)
                    if len(pair) == 2 and pair[0].strip().isdigit():
                        labels[int(pair[0])] = pair[1].strip()
                    else:
                        labels[row_number] = pair[0].strip()
            return labels

    class Xml:
        """Collection of xml manipulation methods"""
        @staticmethod
        def indent(elem, level=0, more_sibs=False):
            """Indents xml object properly in preparation for saving"""
            i = "\n"
            indentchar = '\t'
            if level:
                i += (level-1) * indentchar
            num_kids = len(elem)
            if num_kids:
                if not elem.text or not elem.text.strip():
                    elem.text = i + indentchar
                    if level:
                        elem.text += indentchar
                count = 0
                for kid in elem:
                    Packages.Xml.indent(kid, level+1, count < num_kids - 1)
                    count += 1
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
                    if more_sibs:
                        elem.tail += indentchar
            else:
                if level and (not elem.tail or not elem.tail.strip()):
                    elem.tail = i
                    if more_sibs:
                        elem.tail += indentchar

    class ColorTracker:
        """Tracks colors using customizable colorspace and has easy calibration with trackbars"""
        def __init__(self, channel_max_values, channel_names, window_detection_name, \
                     channel_bounds):
            self._window_detection_name = window_detection_name

            self._num_of_channels = 3
            self._channels = {}
            for i in range(self._num_of_channels):
                self._channels[channel_names[i]] = self._Channel(max_value=channel_max_values[i],
                                                                name=channel_names[i],
                                                                window_detection_name= \
                                                                self._window_detection_name,
                                                                bounds=channel_bounds[i])

        def create_trackbar(self):
            """Creates the trackbars used for easy calibration"""
            keys = list(self._channels)
            for i in range(self._num_of_channels):
                self._channels[keys[i]].create_trackbar()

        def processing(self, frame, iterations=2):
            """Thresholds, removes noise, and returns the contours"""
            keys = list(self._channels)
            frame_threshold = cv2.inRange(frame,
                                        (self._channels[keys[0]].get_low(),
                                         self._channels[keys[1]].get_low(),
                                         self._channels[keys[2]].get_low()),
                                        (self._channels[keys[0]].get_high(),
                                         self._channels[keys[1]].get_high(),
                                         self._channels[keys[2]].get_high()))
            frame_erode = cv2.erode(frame_threshold, None, iterations=iterations)
            frame_dilate = cv2.dilate(frame_erode, None, iterations=iterations)

            contours, _ = cv2.findContours(frame_dilate.copy(), cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)
            return contours.copy()

        def get_channels(self):
            """Returns a deepcopy of the channels of the colorspace"""
            return copy.deepcopy(self._channels)

        class _Channel:
            """Allows individual manipulation of the channels"""
            def __init__(self, max_value, name, window_detection_name, bounds=()):
                self._max_value = max_value
                self._name = name
                self._low_name = "Low " + self._name
                self._high_name = "High " + self._name
                self._window_detection_name = window_detection_name

                if len(bounds) == 2:
                    self._low = bounds[0]
                    self._high = bounds[1]
                else:
                    self._low = 0
                    self._high = max_value

            def create_trackbar(self):
                """Generates trackbars for high and low bounds"""
                cv2.createTrackbar(self._low_name, self._window_detection_name, self._low,
                                self._max_value, self._on_low_thresh_trackbar)
                cv2.createTrackbar(self._high_name, self._window_detection_name, self._high,
                                self._max_value, self._on_high_thresh_trackbar)

            def _on_low_thresh_trackbar(self, trackbar_pos):
                """Callback on new position of lower bound trackbar"""
                self._low = min(self._high-1, trackbar_pos)
                cv2.setTrackbarPos(self._low_name, self._window_detection_name, self._low)

            def _on_high_thresh_trackbar(self, trackbar_pos):
                """Callback on new position of higher bound trackbar"""
                self._high = max(trackbar_pos, self._low+1)
                cv2.setTrackbarPos(self._high_name, self._window_detection_name, self._high)

            def get_low(self):
                """Returns lower bound"""
                return self._low

            def get_high(self):
                """Returns higher bound"""
                return self._high

            def get_max_value(self):
                """Returns max value of the channel"""
                return self._max_value
