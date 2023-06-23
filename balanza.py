import time

import serial

# port = '/dev/cu.usbmodem11101'  # Make sure this is the correct port for your Arduino
port = 'COM9'
baudrate = 9600
timeout = 10

# Open serial connection to Arduino
try:
    ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    exit()

while True:
    # Get user input
    input_value = input("Ingrese el tipo y la cantidad de clavos (por ejemplo: C 25) o S para frenar la medición: ")

    # Exit loop if user inputs 'S'
    if input_value.upper() == 'S':
        break

    # Split input into parts
    input_parts = input_value.split()

    # Check if the input format is correct
    if len(input_parts) != 2:
        print("Invalid input format. Please follow the format (e.g., C 25).")
        continue

    input_article, input_number = input_parts

    # Check if the number part is an integer
    try:
        number = int(input_number)
    except ValueError:
        print('Invalid number received.')
        continue

    # Build output string and encode to bytes
    a = input("Enter \"Instruction: C 25\"")
    output_value = a + '\n'
    output_bytes = output_value.encode()

    # Send data through serial port
    ser.write(output_bytes)
    print(f"Sent to Arduino: {output_value.strip()}")
    time.sleep(5)
    print("Waiting for Arduino to be ready...")

    response_serial = ""
    while response_serial != "OK":
        try:
            response_serial = ser.readline().decode().strip()
        except Exception as e:
            pass
        print(response_serial)
        if response_serial != "OK":
            print("Waiting for Arduino to be ready...")
    time.sleep(5)
    print(f"Got: {output_value}")

# Close serial connection
ser.close()
