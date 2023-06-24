import os
import struct
import time

from dotenv import load_dotenv
from pyModbusTCP.client import ModbusClient

from logger import Logger

load_dotenv()

ON = 0xFF00  # to activate the coil
OFF = 0x0000  # to deactivate the coil
plc_coil_address = 0x0503  # Modbus Address Table DELTA PLC. E.g, ,0x0500 is Y0, 0x501 is Y1, and so on.


class FestoService:

    def __init__(self, logger: Logger):
        self._logger = logger

        # Motor Y
        self._logger.debug("Initializing Motor Y")
        motor_z = ModbusClient(timeout=2)
        motor_z.host = os.getenv("MOTOR_Y_HOST", '192.168.1.3')
        try:
            motor_z.port = int(os.getenv("MOTOR_Y_PORT", 502))
        except TypeError:
            motor_z.port = 502
        motor_z.debug = True

        motor_z.auto_open = False
        motor_z.auto_close = False
        self._motor_z = motor_z
        self._logger.debug(f"Motor Y initialized with host: {motor_z.host} and port: {motor_z.port}")

        # Motor X
        self._logger.debug("Initializing Motor X")
        motor_x = ModbusClient(timeout=2)
        motor_x.host = os.getenv("MOTOR_X_HOST", '192.168.1.4')
        try:
            motor_x.port = int(os.getenv("MOTOR_X_PORT", 502))
        except TypeError:
            motor_x.port = 502
        motor_x.debug = True

        motor_x.auto_open = False
        motor_x.auto_close = False
        self._motor_x = motor_x
        self._logger.debug(f"Motor X initialized with host: {motor_x.host} and port: {motor_x.port}")

        # Motor R
        self._logger.debug("Initializing Motor R")
        motor_r = ModbusClient(timeout=2)
        motor_r.host = os.getenv("MOTOR_R_HOST", '192.168.1.2')
        try:
            motor_r.port = int(os.getenv("MOTOR_R_PORT", 502))
        except TypeError:
            motor_r.port = 502

        motor_r.debug = True

        motor_r.auto_open = False
        motor_r.auto_close = False
        self._motor_r = motor_r
        self._logger.debug(f"Motor R initialized with host: {motor_r.host} and port: {motor_r.port}")

        # PLC
        self._logger.debug("Initializing PLC")
        plc = ModbusClient(timeout=2)
        plc.host = os.getenv("PLC_HOST", '192.168.1.5')
        try:
            plc.port = int(os.getenv("PLC_PORT", 502))
        except TypeError:
            plc.port = 502

        plc.debug = True

        plc.auto_open = False
        plc.auto_close = False
        self._plc = plc
        self._logger.debug(f"PLC initialized with host: {plc.host} and port: {plc.port}")

        self._motors = [self._motor_x, self._motor_z, self._motor_r]

    def _reset_flag(self, motor):
        # reset (rising edge)
        if motor.open():
            tx_pdu = struct.pack('>BHHBHHHH', 0x10, 0x0000, 0x0004, 0x08, 0x4B01, 0x00FA, 0x0000, 0x4E20)
            motor.custom_request(tx_pdu)
            motor.close()

        if motor.open():
            # reset (falling edge)
            tx_pdu = struct.pack('>BHHBHHHH', 0x10, 0x0000, 0x0004, 0x08, 0x4301, 0x00FA, 0x0000, 0x4E20)
            motor.custom_request(tx_pdu)
            motor.close()

    def motor_ready_by_index(self, index):
        motor = self._motors[index]
        return self._motor_ready(motor)

    def _motor_ready(self, motor):
        if motor.open():
            motor.read_holding_registers(0,
                                         4)  # 4: quantity of registers (with FESTO: only to options: 0x0004 or 0x0008)
            motor.close()
            time.sleep(1)

        # establish ready status
        if motor.open():
            tx_pdu = struct.pack('>BHHBHHHH', 0x10, 0x0000, 0x0004, 0x08, 0x0000, 0x00FA, 0x0000, 0x4E20)
            # tx_pdu = struct.pack('>BHHBH', 0x10, 0x0000, 0x0004, 0x08,0x0000)
            motor.custom_request(tx_pdu)
            motor.close()
            time.sleep(1)

        # enable drive
        if motor.open():
            tx_pdu = struct.pack('>BHHBHHHH', 0x10, 0x0000, 0x0004, 0x08, 0x0100, 0x00FA, 0x0000, 0x4E20)
            motor.custom_request(tx_pdu)
            motor.close()
            time.sleep(1)

        #  enable operation
        if motor.open():
            tx_pdu = struct.pack('>BHHBHHHH', 0x10, 0x0000, 0x0004, 0x08, 0x0300, 0x00FA, 0x0000, 0x4E20)
            motor.custom_request(tx_pdu)
            motor.close()
            time.sleep(1)

        self._reset_flag(motor)

        # Direct mode
        if motor.open():
            tx_pdu = struct.pack('>BHHBHHHH', 0x10, 0x0000, 0x0004, 0x08, 0x4301, 0x00FA, 0x0000, 0x4E20)
            motor.custom_request(tx_pdu)
            motor.close()
            time.sleep(1)

        self._homing(motor)
        return True

    def home_motor_by_index(self, motor_index):
        motor = self._motors[motor_index]
        return self._homing(motor)

    def _homing(self, motor):
        # homing (rising)
        if motor.open():
            tx_pdu = struct.pack('>BHHBHHHH', 0x10, 0x0000, 0x0004, 0x08, 0x4305, 0x00FA, 0x0000, 0x4E20)
            motor.custom_request(tx_pdu)
            motor.close()
            time.sleep(1)

        # homing (falling)
        if motor.open():
            tx_pdu = struct.pack('>BHHBHHHH', 0x10, 0x0000, 0x0004, 0x08, 0x4301, 0x00FA, 0x0000, 0x4E20)
            motor.custom_request(tx_pdu)
            motor.close()
            time.sleep(1)

        return True

    def get_motors_ready(self):
        self._motor_ready(self._motor_z)  # z
        self._motor_ready(self._motor_x)  # x
        self._motor_ready(self._motor_r)  # r
        time.sleep(10)
        self._move_motor(self._motor_r, 0x0000, 0xC350)

    def move_motor_by_index(self, motor_index, posH, posL):
        motor = self._motors[motor_index]
        return self._move_motor(motor, posH, posL)

    def _move_motor(self, motor, posH, posL):
        # positioning (1)
        if motor.open():
            tx_pdu = struct.pack('>BHHBHHHH', 0x10, 0x0000, 0x0004, 0x08, 0x4301, 0x00FA, posH, posL)  # 0x4E20
            motor.custom_request(tx_pdu)
            motor.close()
            time.sleep(1)

        # positioning  (2)
        if motor.open():
            tx_pdu = struct.pack('>BHHBHHHH', 0x10, 0x0000, 0x0004, 0x08, 0x4303, 0x00FA, posH, posL)
            motor.custom_request(tx_pdu)
            motor.close()
            time.sleep(10)

        # positioning (1)
        if motor.open():
            tx_pdu = struct.pack('>BHHBHHHH', 0x10, 0x0000, 0x0004, 0x08, 0x4301, 0x00FA, posH, posL)  # 0x4E20
            motor.custom_request(tx_pdu)
            motor.close()
            time.sleep(1)

        return True

    def move_to_box(self):
        self._move_motor(self._motor_z, 0x0003, 0x7460)  # posicion caja arriba
        time.sleep(10)
        self._move_motor(self._motor_x, 0x0002, 0x0F58)  # posicion caja horizontal
        time.sleep(10)
        self.close_gripper()

        self._homing(self._motor_x)
        # homing(motor_z)
        time.sleep(10)
        self._move_motor(self._motor_r, 0x0000, 0x9C40)  # posicion caja arriba

        time.sleep(10)
        self._move_motor(self._motor_r, 0x0000, 0xC350)
        self._move_motor(self._motor_x, 0x0002, 0x0F58)  # posicion caja horizontal
        self.open_gripper()
        self._homing(self._motor_x)
        self._homing(self._motor_z)

    def close_gripper(self):
        if self._plc.open():
            tx_pdu = struct.pack('>BHH', 0x05, plc_coil_address, ON)  # 0x05 : WRITE single coil ||
            self._plc.custom_request(tx_pdu)
            self._plc.close()
            self._logger.debug("Gripper open")

        time.sleep(2)
        return True

    def open_gripper(self):
        if self._plc.open():
            tx_pdu = struct.pack('>BHH', 0x05, plc_coil_address, OFF)  # 0x05 : WRITE single coil ||
            self._plc.custom_request(tx_pdu)
            self._plc.close()
            self._logger.debug("Gripper close")
        return True