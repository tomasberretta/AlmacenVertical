# Move two motos upside down.

# %%----------------------------------------------------------------
from pyModbusTCP.client import ModbusClient
import struct
import time

# Motor Y
motor_z = ModbusClient(timeout=2)
motor_z.host = '192.168.1.3'
motor_z.port = 502
motor_z.debug = True

motor_z.auto_open = False
motor_z.auto_close = False

# Motor X
motor_x = ModbusClient(timeout=2)
motor_x.host = '192.168.1.4'
motor_x.port = 502
motor_x.debug = True

motor_x.auto_open = False
motor_x.auto_close = False

# Motor R
motor_r = ModbusClient(timeout=2)
motor_r.host = '192.168.1.2'
motor_r.port = 502
motor_r.debug = True

motor_r.auto_open = False
motor_r.auto_close = False

# PLC
plc = ModbusClient(timeout=2)
plc.host = '192.168.1.5'
plc.port = 502
plc.debug = True

plc.auto_open = False
plc.auto_close = False


# %%-----------------------------

def reset_flag(motor):
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


def motor_ready(motor):
    if motor.open():
        motor.read_holding_registers(0, 4)  # 4: quantity of registers (with FESTO: only to options: 0x0004 or 0x0008)
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

    reset_flag(motor)

    # Direct mode
    if motor.open():
        tx_pdu = struct.pack('>BHHBHHHH', 0x10, 0x0000, 0x0004, 0x08, 0x4301, 0x00FA, 0x0000, 0x4E20)
        motor.custom_request(tx_pdu)
        motor.close()
        time.sleep(1)

    homing(motor)


# %%----------------------------------------------------------------

def homing(motor):
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

def get_motors_ready():
    motor_ready(motor_z)  # z
    motor_ready(motor_x)  # x
    motor_ready(motor_r)  # x
    time.sleep(10)
    move_motor(motor_r, 0x0000, 0xC350)


# %%----------------------------------------------------------------

#  One Motor movement at a time

def move_motor(motor, posH, posL):
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

def move_to_box():
    move_motor(motor_z, 0x0003, 0x7460)  # posicion caja arriba
    time.sleep(10)
    move_motor(motor_x, 0x0002, 0x0F58)  # posicion caja horizontal
    time.sleep(10)
    close_gripper()

    homing(motor_x)
    # homing(motor_z)
    time.sleep(10)
    move_motor(motor_r, 0x0000, 0x9C40)  # posicion caja arriba

    time.sleep(10)
    move_motor(motor_r, 0x0000, 0xC350)
    move_motor(motor_x, 0x0002, 0x0F58)  # posicion caja horizontal
    open_gripper()
    homing(motor_x)
    homing(motor_z)





# %%----------------------------------------------------------------

# move_motor(motor_z ,0x0000,0x4120)

# reset_flag(motor_z)
# %%----------------------------------------------------------------
# PC - PLC comunication
# write single coil

# From Modbus_Application_Protocol_V1_1b3, 6.5 05 (0x05) Write Single Coil, p. 17 (pdf)
# The requested ON/OFF state is specified by a constant in the request data field. A value of FF
# 00 hex requests the output to be ON. A value of 00 00 requests it to be OFF. All other values
# are illegal and will not affect the output.
#
ON = 0xFF00  # to activate the coil
OFF = 0x0000 # to deactivate the coil
plc_coil_address = 0x0503 # Modbus Address Table DELTA PLC. E.g, ,0x0500 is Y0, 0x501 is Y1, and so on.

# write single coil modbus function code


# close gripper
def close_gripper():
    if plc.open():
        tx_pdu = struct.pack('>BHH', 0x05, plc_coil_address, ON) #0x05 : WRITE single coil ||
        plc.custom_request(tx_pdu)
        plc.close()
        print("open")

    time.sleep(2)

# open gripper
def open_gripper():
    if plc.open():
        tx_pdu = struct.pack('>BHH', 0x05, plc_coil_address, OFF) #0x05 : WRITE single coil ||
        plc.custom_request(tx_pdu)
        plc.close()
        print("close")
