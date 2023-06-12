import serial, time

# ConfiguraciÃ³n de la comunicaciÃ³n serial con Arduino
port = '/dev/cu.usbmodem1101'  # Cambiar al puerto adecuado // este es el de mas lejos de la pantalla
baudrate = 9600  # Must match the baud rate in the Arduino sketch
timeout = 10  # Timeout for serial communication (in seconds)

article_identifier = ['C', 'M', 'G']  # 1 ,2, 3
# Open the serial port
ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)

# Create an empty array to store the values
sensor_values = []

# Pedir al usuario que ingrese el identificador y el número de clavos solicitados
input_value = input("Ingrese el tipo y la cantidad de clavos (por ejemplo: C 25) o S para frenar la medición: ")

# Separar la cadena de entrada en dos partes
input_parts = input_value.split()  # Usar un espacio como separador
input_article = input_parts[0]  # La primera parte es el identificador
input_number = input_parts[1]  # La segunda parte es el número

while input_value != 'S':
    # # Read a line from the serial port
    # line = ser.readline().decode().strip()

    # Convertir el número en un entero
    number = int(input_number)

    # Convertir el identificador y el número en una cadena de bytes
    output_value =   str(
        number)+ " " + str(input_article) + '\n'  # Convertir el identificador y el número en una cadena y agregar el fin de línea
    output_bytes = output_value.encode()  # Codificar la cadena en bytes

    # Escribir los bytes al puerto serial
    ser.write(output_bytes)  # Enviar los bytes al puerto serial

    # Parse the line as an integer value
    try:
        # sensorValue = int(line)
        # print('Numero de clavos:', sensorValue)
        #
        # # Append the value to the array
        # sensor_values.append(sensorValue)

        # Escribir un valor al puerto serial
        ser.write(output_bytes)  # Enviar 25 como clavos solicitados

    except ValueError:
        # print('Invalid data received:', line)
        print('Invalid data received:')

    # Pedir al usuario que ingrese el identificador y el número de clavos solicitados
    input_value = input("Ingrese el tipo y la cantidad de clavos (por ejemplo: C 25) o S para frenar la medición: ")

    # Separar la cadena de entrada en dos partes
    input_parts = input_value.split()  # Usar un espacio como separador
    input_article = input_parts[0]  # La primera parte es el identificador
    input_number = input_parts[1]  # La segunda parte es el número

# Close the serial port
ser.close()
