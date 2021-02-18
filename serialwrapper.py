#!/usr/bin/env python3
"""Serial Protocol Library"""

import enum
import serial
import numpy as np

class SerialWrapper:
    """Class containing usage methods of the Serial Protocol"""

    @classmethod
    def begin(cls, serial_port, baud_rate):
        """Initialized the serial port and defines important data"""
        cls._serial = serial.Serial(serial_port, baud_rate)

        cls._CRC_CALCULATOR = [0,
                               3, 6, 5, 7, 4, 1, 2, 5, 6, 3,
                               0, 2, 1, 4, 7, 1, 2, 7, 4, 6,
                               5, 0, 3, 4, 7, 2, 1, 3, 0, 5,
                               6]

        cls._PACKET_DELIMITER_BYTE = 0x1f
        cls._PACKET_DELIMITER_BYTE_PCS = cls._process(cls._PACKET_DELIMITER_BYTE)
        cls._ITEM_DELIMITER_BYTE = 0x1d
        cls._ITEM_DELIMITER_BYTE_PCS = cls._process(cls._ITEM_DELIMITER_BYTE)
        cls._ESCAPE_BYTE = 0x1e
        cls._ESCAPE_BYTE_PCS = cls._process(cls._ESCAPE_BYTE)
        cls._CONVERSION = 0x10
        cls._ITEM_BIT_LEN = 5
        cls._MAX_ITEM_BYTES = 7
        cls._state = cls._State.INIT
        cls._itemNum = 0
        cls._item = 0

    @classmethod
    def send(cls, packet):
        """Sends packet with protocol"""
        cls._serial.write(cls._PACKET_DELIMITER_BYTE_PCS)
        for item in packet:
            if item < 0:
                itemByte = (abs(item) << 1) + 1
            else:
                itemByte = abs(item) << 1

            itemBytes = np.zeros(cls._MAX_ITEM_BYTES, dtype=np.uint8)
            bytesNum = 0

            for bytesNum in range(cls._MAX_ITEM_BYTES):
                itemBytes[bytesNum] = itemByte & 0x1f
                itemByte = itemByte >> cls._ITEM_BIT_LEN

            for bytesNum in range(bytesNum, -1, -1):
                if itemBytes[bytesNum] != 0:
                    break

            for byteIndex in range(bytesNum, -1, -1):
                cls._write(itemBytes[byteIndex])

            cls._serial.write(cls._ITEM_DELIMITER_BYTE_PCS)
        cls._serial.write(cls._PACKET_DELIMITER_BYTE_PCS)

    @classmethod
    def receive(cls, packet):
        """Receive packet with protocol"""
        while cls._serial.in_waiting:
            message = cls._unprocess(cls._serial.read())
            if message != -1:
                status, packet = cls._receiveSM(packet, message)
                if status:
                    if cls._itemNum:
                        itemNum = cls._itemNum
                        cls._itemNum = 0
                        return packet, itemNum
            else:
                cls._state = cls._State.INIT
                cls._itemNum = 0
                cls._item = 0

        return -1

    @classmethod
    def _write(cls, item):
        if (item == cls._PACKET_DELIMITER_BYTE or item == cls._ITEM_DELIMITER_BYTE or item == cls._ESCAPE_BYTE):
            cls._serial.write(cls._ESCAPE_BYTE_PCS)
            cls._serial.write(cls._process(cls._escape(item)))
        else:
            cls._serial.write(cls._process(item))

    @classmethod
    def _receiveSM(cls, buffer, byte_in):
        """Facilitate protocol with state machine"""
        if cls._state == cls._State.INIT:
            if byte_in == cls._PACKET_DELIMITER_BYTE:
                cls._state = cls._State.NORMAL
            return False, buffer
        elif cls._state == cls._State.NORMAL:
            if byte_in == cls._PACKET_DELIMITER_BYTE:
                return True, buffer
            if byte_in == cls._ITEM_DELIMITER_BYTE:
                if cls._item & 0x1:
                    buffer[cls._itemNum] = (cls._item >> 1) * -1
                    cls._itemNum += 1
                else:
                    buffer[cls._itemNum] = cls._item >> 1
                    cls._itemNum += 1
                cls._item = 0
                return False, buffer
            if byte_in == cls._ESCAPE_BYTE:
                cls._state = cls._State.ESCAPE
                return False, buffer
            cls._item = cls._item << cls._ITEM_BIT_LEN
            cls._item += byte_in
            return False, buffer
        elif cls._state == cls._State.ESCAPE:
            cls._item = cls._item << cls._ITEM_BIT_LEN
            cls._item += cls._unescape(byte_in)
            cls._state = cls._State.NORMAL
            return False, buffer

    @classmethod
    def _doCRC(cls, message):
        """Add CRC to message"""
        return message * 8 + cls._CRC_CALCULATOR[message]

    @classmethod
    def _undoCRC(cls, crc_byte):
        """Remove CRC and check for corruption"""
        message = (crc_byte & 0xf8) // 8
        crc = crc_byte & 0x07

        if cls._CRC_CALCULATOR[message] == crc:
            return message
        else:
            print("[WARNING] CORRUPT BYTE DETECTED")
            return -1

    @classmethod
    def _escape(cls, raw):
        """XOR byte with predefined mask"""
        return raw ^ cls._CONVERSION

    @classmethod
    def _unescape(cls, escaped):
        """XOR byte with predefined mask"""
        return escaped ^ cls._CONVERSION

    @classmethod
    def _process(cls, byte):
        """Convert to byte with CRC"""
        return bytes([cls._doCRC(byte)])

    @classmethod
    def _unprocess(cls, byte):
        """Convert to number and undo CRC"""
        return cls._undoCRC(ord(byte))

    @classmethod
    def getSerial(cls):
        """Procide serial object"""
        return cls._serial

    class _State(enum.Enum):
        """Enum for states of Serial protocol"""
        INIT = 0
        NORMAL = 1
        ESCAPE = 2
