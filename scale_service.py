import os
import time
import serial
from logger import Logger
from mockdata import get_serial_mock
from dotenv import load_dotenv

load_dotenv()

# port = '/dev/cu.usbmodem11101' # Arduino port for Mac
# port = 'COM9' # Arduino port for Windows

port = os.getenv("ARDUINO_PORT", "/dev/cu.usbmodem11101")
try:
    baud_rate = int(os.getenv("ARDUINO_BAUD-RATE", 9600))
except TypeError:
    baud_rate = 9600
try:
    timeout = int(os.getenv(" ARDUINO_TIMEOUT", 10))
except TypeError:
    timeout = 10


class ScaleService:

    def __init__(self, logger: Logger):
        """Scale Service initialization"""
        self._logger = logger
        try:
            if os.getenv("MOCK") == "True":
                # Only for testing purposes
                self._ser = get_serial_mock()
            else:
                self._ser = serial.Serial(port, baudrate=baud_rate, timeout=timeout)
        except serial.SerialException as e:
            self._logger.error(f"Error opening serial port: {e}")
            exit(1)
        self._logger.info(f"ScaleService initialized with port: {port}, baud-rate: {baud_rate}, timeout: {timeout}")

    def send_to_scale(self, instruction):
        """Function to send instruction to the scale"""

        output_value = instruction + '\n'
        output_bytes = output_value.encode()

        self._ser.write(output_bytes)
        self._logger.info(f"Sent to Arduino: {output_value.strip()}")
        time.sleep(5)
        return f"Sent: {output_value.strip()}"

    def read_from_scale(self):
        """Function to read the weight or serial port from the scale"""
        return self._ser.readline().decode().strip()

    def stop_scale_connection(self):
        """Function to close the serial port"""
        self._ser.close()
        self._logger.info("Serial connection closed")
