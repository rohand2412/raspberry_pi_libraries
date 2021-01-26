import serial
import numpy as np

class SerialWrapper:
    @classmethod
    def begin(cls, serial_port, baud_rate):
        cls._serial = serial.Serial(serial_port, baud_rate)

    @classmethod
    def send(cls, buffer):
        for item in buffer:
            item = item.encode()
            cls._serial.write(item)

    @classmethod
    def receive(cls):
        buffer = []
        if cls._serial.in_waiting:
            buffer = np.zeros(cls._serial.in_waiting, dtype=str)
            for index in range(len(buffer)):
                buffer[index] = cls._serial.read().decode()

        return buffer
