import os
import struct
import time

from dotenv import load_dotenv
from pyModbusTCP.client import ModbusClient

from logger import Logger
from scale_service import ScaleService

load_dotenv()

ON = 0xFF00  # to activate the coil
OFF = 0x0000  # to deactivate the coil
plc_coil_address = 0x0503  # Modbus Address Table DELTA PLC. E.g, ,0x0500 is Y0, 0x501 is Y1, and so on.


class FestoService:

    def __init__(self, logger: Logger, scale_service: ScaleService):
        """Festo Service initialization"""

        self._logger = logger
        self._scale_service = scale_service

        # Initialize Motor Z with it corresponding connection parameters
        self._logger.debug("Initializing Motor Y")
        motor_z = ModbusClient(timeout=2)
        motor_z.host = os.getenv("MOTOR_Y_HOST", '192.168.1.3')
        try:
            motor_z.port = int(os.getenv("MOTOR_Y_PORT", 502))
        except TypeError:
            motor_z.port = 502
        motor_z.debug = False
        motor_z.auto_open = False
        motor_z.auto_close = False
        self._motor_z = motor_z
        self._logger.debug(f"Motor Y initialized with host: {motor_z.host} and port: {motor_z.port}")

        # Initialize Motor X with it corresponding connection parameters
        self._logger.debug("Initializing Motor X")
        motor_x = ModbusClient(timeout=2)
        motor_x.host = os.getenv("MOTOR_X_HOST", '192.168.1.4')
        try:
            motor_x.port = int(os.getenv("MOTOR_X_PORT", 502))
        except TypeError:
            motor_x.port = 502
        motor_x.debug = False
        motor_x.auto_open = False
        motor_x.auto_close = False
        self._motor_x = motor_x
        self._logger.debug(f"Motor X initialized with host: {motor_x.host} and port: {motor_x.port}")

        # Initialize Motor R with it corresponding connection parameters
        self._logger.debug("Initializing Motor R")
        motor_r = ModbusClient(timeout=2)
        motor_r.host = os.getenv("MOTOR_R_HOST", '192.168.1.2')
        try:
            motor_r.port = int(os.getenv("MOTOR_R_PORT", 502))
        except TypeError:
            motor_r.port = 502
        motor_r.debug = False
        motor_r.auto_open = False
        motor_r.auto_close = False
        self._motor_r = motor_r
        self._logger.debug(f"Motor R initialized with host: {motor_r.host} and port: {motor_r.port}")

        # Initialize PLC with it corresponding connection parameters
        self._logger.debug("Initializing PLC")
        plc = ModbusClient(timeout=2)
        plc.host = os.getenv("PLC_HOST", '192.168.1.5')
        try:
            plc.port = int(os.getenv("PLC_PORT", 502))
        except TypeError:
            plc.port = 502
        plc.debug = False
        plc.auto_open = False
        plc.auto_close = False
        self._plc = plc
        self._logger.debug(f"PLC initialized with host: {plc.host} and port: {plc.port}")

        # Add motors to list for easy access
        self._motors = [self._motor_x, self._motor_z, self._motor_r]

        # Predefined boxes Z positions
        self._boxes_z = [(0x0003, 0x70AA), (0x0005, 0x2A44), (0x0006, 0xD600)]

        # Predefined boxes X positions
        self._boxes_x = (0x0002, 0x0F58)

    def _reset_flag(self, motor):
        """Function to reset the flag of the motor"""

        # reset (rising edge)
        if motor.open():
            tx_pdu = struct.pack('>BHHBHHHH', 0x10, 0x0000, 0x0004, 0x08, 0x4B01, 0x00FA, 0x0000, 0x4E20)
            motor.custom_request(tx_pdu)
            motor.close()
            self._logger.debug("Set reset bit on")

        # reset (falling edge)
        if motor.open():
            tx_pdu = struct.pack('>BHHBHHHH', 0x10, 0x0000, 0x0004, 0x08, 0x4301, 0x00FA, 0x0000, 0x4E20)
            motor.custom_request(tx_pdu)
            motor.close()
            self._logger.debug("Set reset bit off")


    def motor_ready_by_index(self, index):
        """Function to set the motor to ready state by index calling the _motor_ready function"""

        motor = self._motors[index]
        self._logger.debug(f"Setting ready to motor in index [{index}]")
        return self._motor_ready(motor)

    def _motor_ready(self, motor):
        """Function to set the motor to ready state"""

        if motor.open():
            motor.read_holding_registers(0, 4)  # 4: quantity of registers (with FESTO: only to options: 0x0004 or 0x0008)
            motor.close()
            time.sleep(1)
            self._logger.debug(f"Ready function - Read registers 0, 4")


        # establish ready status
        if motor.open():
            tx_pdu = struct.pack('>BHHBHHHH', 0x10, 0x0000, 0x0004, 0x08, 0x0000, 0x00FA, 0x0000, 0x4E20)
            motor.custom_request(tx_pdu)
            motor.close()
            time.sleep(1)
            self._logger.debug(f"Ready function - Establish ready status")


        # enable drive
        if motor.open():
            tx_pdu = struct.pack('>BHHBHHHH', 0x10, 0x0000, 0x0004, 0x08, 0x0100, 0x00FA, 0x0000, 0x4E20)
            motor.custom_request(tx_pdu)
            motor.close()
            time.sleep(1)
            self._logger.debug(f"Ready function - Enable drive")


        #  enable operation
        if motor.open():
            tx_pdu = struct.pack('>BHHBHHHH', 0x10, 0x0000, 0x0004, 0x08, 0x0300, 0x00FA, 0x0000, 0x4E20)
            motor.custom_request(tx_pdu)
            motor.close()
            time.sleep(1)
            self._logger.debug(f"Ready function - Enable operation")


        # Just in case, reset flag
        self._reset_flag(motor)

        # Direct mode
        if motor.open():
            tx_pdu = struct.pack('>BHHBHHHH', 0x10, 0x0000, 0x0004, 0x08, 0x4301, 0x00FA, 0x0000, 0x4E20)
            motor.custom_request(tx_pdu)
            motor.close()
            time.sleep(1)
            self._logger.debug(f"Ready function - Direct mode")

        # Finally, home the motor
        self._homing(motor)
        return True

    def home_motor_by_index(self, motor_index):
        """Function to home the motor by index calling the _homing function"""
        self._logger.debug(f"Setting home to motor in index [{motor_index}]")
        motor = self._motors[motor_index]
        return self._homing(motor)

    def _homing(self, motor):
        """Function to home the motor"""
        self._logger.debug(f"Started homing on motor")

        # homing (rising)
        if motor.open():
            tx_pdu = struct.pack('>BHHBHHHH', 0x10, 0x0000, 0x0004, 0x08, 0x4305, 0x00FA, 0x0000, 0x4E20)
            motor.custom_request(tx_pdu)
            motor.close()
            time.sleep(1)
            self._logger.debug(f"Homing bit on")

        # homing (falling)
        if motor.open():
            tx_pdu = struct.pack('>BHHBHHHH', 0x10, 0x0000, 0x0004, 0x08, 0x4301, 0x00FA, 0x0000, 0x4E20)
            motor.custom_request(tx_pdu)
            motor.close()
            time.sleep(1)
            self._logger.debug(f"Homing bit off")

        return True

    def get_motors_ready(self):
        """Function to set all the motors to ready state"""
        self._motor_ready(self._motor_z)  # z motor
        self._motor_ready(self._motor_x)  # x motor
        self._motor_ready(self._motor_r)  # r motor
        time.sleep(10)

        # Move R motor to better position for gripping boxes
        self._move_motor(self._motor_r, 0x0000, 0xC350)
        self._logger.info("Motors are ready")

    def move_motor_by_index(self, motor_index, posH, posL):
        """Function to move the motor by index calling the _move_motor function"""
        motor = self._motors[motor_index]
        return self._move_motor(motor, posH, posL)

    def _move_motor(self, motor, posH, posL, velocity=0x00FF):
        """Function to move the motor"""

        # positioning (1)
        if motor.open():
            tx_pdu = struct.pack('>BHHBHHHH', 0x10, 0x0000, 0x0004, 0x08, 0x4301, velocity, posH, posL)
            motor.custom_request(tx_pdu)
            motor.close()
            self._logger.debug("Move motor function - Positioning 1")
            time.sleep(1)


        # positioning  (2)
        if motor.open():
            tx_pdu = struct.pack('>BHHBHHHH', 0x10, 0x0000, 0x0004, 0x08, 0x4303, velocity, posH, posL)
            motor.custom_request(tx_pdu)
            motor.close()
            self._logger.debug("Move motor function - Positioning 2")
            time.sleep(10)


        # positioning (1)
        if motor.open():
            tx_pdu = struct.pack('>BHHBHHHH', 0x10, 0x0000, 0x0004, 0x08, 0x4301, velocity, posH, posL)
            motor.custom_request(tx_pdu)
            motor.close()
            self._logger.debug("Move motor function - Positioning 1")
            time.sleep(1)

        return True

    def move_to_box(self, index):
        """Function to move the robot to the box in the index position"""
        self._logger.debug(f"Start move to box in index [{index}]")

        # Get the z coordinates of the box
        z_coordinate = self._boxes_z[index]

        # Go to the box
        self._move_motor(self._motor_z, z_coordinate[0], z_coordinate[1])
        time.sleep(30)
        self._move_motor(self._motor_x, self._boxes_x[0], self._boxes_x[1])
        time.sleep(10)

        # Grip the box
        self.close_gripper()

        # Take out the box
        self._homing(self._motor_x)
        time.sleep(20)

        # Move the box to the delivery position
        self._move_motor(self._motor_z, 0x0004, 0x93E0)
        time.sleep(10)

        # Rotate the box to deliver products
        self._move_motor(self._motor_r, 0x0000, 0x4A38, 0x0020)

        # Start the communication with the scale to wait for the weight to be 'OK'
        response_serial = 'Started'
        while response_serial != "OK":
            try:
                response_serial = self._scale_service.read_from_scale()
                self._logger.debug(f"Got from serial port: {response_serial}")
            except ValueError:
                self._logger.debug(f"Got non-parseable bytes from serial port")
            if response_serial != "OK":
                self._logger.debug("Waiting for Arduino to be ready...")

        # Rotate the box to the original position
        self._move_motor(self._motor_r, 0x0000, 0xC350, 0x0032)
        time.sleep(10)

        # Move the box to the original position
        self._move_motor(self._motor_z, z_coordinate[0], z_coordinate[1])
        time.sleep(10)
        self._move_motor(self._motor_x, self._boxes_x[0], self._boxes_x[1])
        time.sleep(10)

        # Release the box
        self.open_gripper()

        # Move the robot to the original position
        self._homing(self._motor_x)
        time.sleep(20)
        self._homing(self._motor_z)
        time.sleep(20)

        self._logger.info(f"Finished move to box in index [{index}]")

    def close_gripper(self):
        # Function to close the gripper
        if self._plc.open():
            tx_pdu = struct.pack('>BHH', 0x05, plc_coil_address, ON)  # 0x05 : WRITE single coil ||
            self._plc.custom_request(tx_pdu)
            self._plc.close()
            self._logger.debug("Gripper close")
        time.sleep(2)
        return True

    def open_gripper(self):
        # Function to open the gripper
        if self._plc.open():
            tx_pdu = struct.pack('>BHH', 0x05, plc_coil_address, OFF)  # 0x05 : WRITE single coil ||
            self._plc.custom_request(tx_pdu)
            self._plc.close()
            self._logger.debug("Gripper open")
        time.sleep(2)
        return True
