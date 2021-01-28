import serial
import enum
import numpy as np

class SerialWrapper:
    @classmethod
    def begin(cls, serial_port, baud_rate):
        cls._serial = serial.Serial(serial_port, baud_rate)
        cls._DELIMITER_BYTE = 0xff
        cls._DELIMITER_BYTE_PCS = cls._process(cls._DELIMITER_BYTE)
        cls._ESCAPE_BYTE = 0xfe
        cls._ESCAPE_BYTE_PCS = cls._process(cls._ESCAPE_BYTE)
        cls._CONVERSION = 0x80
        cls._state = cls._State.INIT
        cls._itemNum = 0

        cls._CRC_CALCULATOR =   [0,
                                3, 6, 5, 7, 4, 1, 2, 5, 6, 3,
                                0, 2, 1, 4, 7, 1, 2, 7, 4, 6,
                                5, 0, 3, 4, 7, 2, 1, 3, 0, 5,
                                6]

    @classmethod
    def send(cls, buffer):
        cls._serial.write(cls._DELIMITER_BYTE_PCS)
        for item in buffer:
            if (item == cls._DELIMITER_BYTE or item == cls._ESCAPE_BYTE):
                cls._serial.write(cls._ESCAPE_BYTE_PCS)
                cls._serial.write(cls._process(cls._escape(item)))
            else:
                cls._serial.write(cls._process(item))
        cls._serial.write(cls._DELIMITER_BYTE_PCS)

    @classmethod
    def receive(cls, buffer):
        while cls._serial.in_waiting:
            status, buffer = cls._receiveSM(buffer, ord(cls._serial.read()))
            if status:
                if cls._itemNum:
                    cls._itemNum = 0
                    return buffer

        return -1

    @classmethod
    def _receiveSM(cls, buffer, byte_in):
        if cls._state == cls._State.INIT:
            if byte_in == cls._DELIMITER_BYTE:
                cls._state = cls._State.NORMAL
            return False, buffer
        elif cls._state == cls._State.NORMAL:
            if byte_in == cls._DELIMITER_BYTE:
                return True, buffer
            if byte_in == cls._ESCAPE_BYTE:
                cls._state = cls._State.ESCAPE
                return False, buffer
            buffer[cls._itemNum] = byte_in
            cls._itemNum += 1
            return False, buffer
        elif cls._state == cls._State.ESCAPE:
            buffer[cls._itemNum] = cls._unescape(byte_in)
            cls._itemNum += 1
            cls._state = cls._State.NORMAL
            return False, buffer

    @classmethod
    def _doCRC(cls, message):
        return message * 8 + cls._CRC_CALCULATOR[message]

    @classmethod
    def _undoCRC(cls, crc_byte):
        message = (crc_byte & 0xf8) / 8
        crc = crc_byte & 0x07

        if cls._CRC_CALCULATOR[message] == crc:
            return message
        else:
            return -1

    @classmethod
    def _escape(cls, raw):
        return raw ^ cls._CONVERSION

    @classmethod
    def _unescape(cls, escaped):
        return escaped ^ cls._CONVERSION
    
    @classmethod
    def _process(cls, byte):
        return bytes([byte])
    
    class _State(enum.Enum):
        INIT = 0
        NORMAL = 1
        ESCAPE = 2
