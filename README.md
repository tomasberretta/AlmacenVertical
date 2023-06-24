# Almacen Vertical
This project is a prototype of a system that can handle different sizes and amounts of products using a motorized gripper and a scale. The system consists of the following components:

- A Festo CMMO controller motor that controls the movement of the gripper along two axes and one for rotation (X, Z and R).
- A PLC that controls the opening and closing of the gripper.
- An Arduino that communicates with a HX711.h module to read the weight of the product on the scale.
- A backend server written in Python using Flask that provides a REST API to control the motors and the gripper actions and also send information to the scale or execute the whole process end to end.
- A frontend web page written in HTML that allows the user to interact with the system through the backend API.

The system can perform the following tasks:

- Move the gripper to a specific position along any axis.
- Open or close the gripper.
- Move the gripper to its home or ready position.
- Move the product from a shelf to a scale and read its weight.
- Execute a predefined sequence of actions based on the size and amount of the product.

## Prerequisites
- Python 3.10.0
- pip 20.2.4

## Installation
```bash
pip install -r requirements.txt
```
## Environment variables
There are 14 environment variables that need to be set:
- FLASK_HOST
- FLASK_PORT
- ARDUINO_PORT
- ARDUINO_BAUD-RATE
- ARDUINO_TIMEOUT
- MOCK
- MOTOR_Y_HOST
- MOTOR_Y_PORT
- MOTOR_X_HOST
- MOTOR_X_PORT
- MOTOR_R_HOST
- MOTOR_R_PORT
- PLC_HOST
- PLC_PORT

Their default values are on the `.env` file and are:
- FLASK_HOST = 127.0.0.1
- FLASK_PORT = 5000
- ARDUINO_PORT = COM9
- ARDUINO_BAUD-RATE = 9600
- ARDUINO_TIMEOUT = 10
- MOCK=False
- MOTOR_Y_HOST=192.168.1.3
- MOTOR_Y_PORT=502
- MOTOR_X_HOST=192.168.1.4
- MOTOR_X_PORT=502
- MOTOR_R_HOST=192.168.1.2
- MOTOR_R_PORT=502
- PLC_HOST=192.168.1.5
- PLC_PORT=502

## Starting venv and server

If running on Windows:

```bash
venv/Scripts/activate.bat
python start.py
```

Otherwise:
```bash
source venv/bin/activate
python start.py
```

## API
### Health check 
`/health`

This endpoint is used to check if the server is running.
```bash
curl -X GET http://<FLASK_HOST>:<FLASK_PORT>/health
```

### Execute
`/execute`

This endpoint is used to execute a command to move the motors and the gripper according to the size and amount of the product, and set the scale to wait for those fields, weigh them and then separate them accordingly.

``` bash
curl -X POST http://<FLASK_HOST>:<FLASK_PORT>/execute -H "Content-Type: application/json" -d '{"size": "C", "amount": 10}'
```

The JSON body must have the following fields:

- `size`: a string that indicates the size of the product. It can be one of "C", "M" or "G".
- `amount`: an integer that indicates the amount of the product. It must be between 0 and 100.

### Ready
`/ready`

This endpoint is used to check if the system is ready to execute a command.

``` bash
curl -X POST http://<FLASK_HOST>:<FLASK_PORT>/ready -H "Content-Type: application/json" -d '{}'
```

The JSON body must be empty.

### Gripper open
`/gripper/open`

This endpoint is used to open the gripper.

``` bash
curl -X POST http://<FLASK_HOST>:<FLASK_PORT>/gripper/open -H "Content-Type: application/json" -d '{}'
```

The JSON body must be empty.

### Gripper close
`/gripper/close`

This endpoint is used to close the gripper.

``` bash
curl -X POST http://<FLASK_HOST>:<FLASK_PORT>/gripper/close -H "Content-Type: application/json" -d '{}'
```

The JSON body must be empty.

### Motor home
`/motor/home`

This endpoint is used to move a motor to its home position.

``` bash
curl -X POST http://<FLASK_HOST>:<FLASK_PORT>/motor/home -H "Content-Type: application/json" -d '{"index": 0}'
```

The JSON body must have the following field:

- `index`: an integer that indicates the index of the motor. It can be 0, 1 or 2.

### Motor ready
`/motor/ready`

This endpoint is used to move a motor to its ready position.

``` bash
curl -X POST http://<FLASK_HOST>:<FLASK_PORT>/motor/ready -H "Content-Type: application/json" -d '{"index": 0}'
```

The JSON body must have the following field:

- `index`: an integer that indicates the index of the motor. It can be 0, 1 or 2.

### Motor move
`/motor/move`

This endpoint is used to move a motor to a specific position.

``` bash
curl -X POST http://<FLASK_HOST>:<FLASK_PORT>/motor/move -H "Content-Type: application/json" -d '{"index": 0, "posH": "0x0000", "posL": "0x0000"}'
```

The JSON body must have the following fields:

- `index`: an integer that indicates the index of the motor. It can be 0, 1 or 2.
- `posH`: a string that represents a hexadecimal value for the high byte of the position. It must have a 0x prefix and four digits.
- `posL`: a string that represents a hexadecimal value for the low byte of the position. It must have a 0x prefix and four digits.

### Send to scale
`/send-to-scale`

This endpoint is used to send a command to the scale and read its weight.

``` bash
curl -X POST http://<FLASK_HOST>:<FLASK_PORT>/send-to-scale -H "Content-Type: application/json" -d '{"size": "C", "amount": 10}'
```

The JSON body must have the following fields:

- `size`: a string that indicates the size of the product. It can be one of "C", "M" or "G".
- `amount`: an integer that indicates the amount of the product. It must be between 0 and 100.