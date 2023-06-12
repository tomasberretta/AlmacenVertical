# Hello World

#%%----------------------------------------------------------------
from pyModbusTCP.client import ModbusClient
import struct

# Configurar la comunicación con un controlador de motor (o server Modbus)
plc = ModbusClient(host= '192.168.1.4', port=502, timeout=2, debug=True)

plc.auto_open = False  #El canal TCP se mantiene cerrado por default
plc.auto_close = False #El canal TCP se mantiene cerrado por default

# Para que la comunicación funcione correctamente y no arroje error
# hace falta abrir y cerrar el canal de comunicación cada vez que se envía un error
# un mensaje de Modbus
if plc.open():  #se abre el canal de comunicación
    print("Entre")
    tx_pdu = struct.pack('>B', 0x11)
    response = plc.custom_request(tx_pdu) # se envía el mensaje Modbus
    unpacked = struct.unpack('>B', response)
    plc.close() #se cierra el canal de comunicación
