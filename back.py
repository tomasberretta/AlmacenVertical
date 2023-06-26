import os
from logging.config import dictConfig
from flask import Flask, request
from flask_cors import CORS, cross_origin
from marshmallow import ValidationError

from festo_service import FestoService
from logger import FlaskLogger, ColorFormatter
from scale_service import ScaleService
from schemas import SendScaleRequestSchema, HomeMotorRequestSchema, ReadyMotorRequestSchema, MoveMotorRequestSchema
from util import validate_json_structure
from dotenv import load_dotenv
from waitress import serve

load_dotenv()

# Configure logging
dictConfig({
    'version': 1,
    'formatters': {'color': {
        '()': ColorFormatter
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'color'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})

# Configure Flask
app = Flask("Backend Server")
logger = FlaskLogger(app, "Backend Server")
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# For convenience
sizes = ['C', 'M', 'G']

# Initialize services
scale_service = ScaleService(logger)
festo_service = FestoService(logger, scale_service)


@app.route('/')
@cross_origin()
def hello_world():
    """Endpoint for testing purposes"""
    logger.debug(f"Entered /")
    return 'Hello, World!'


@app.route('/health', methods=['GET'])
@cross_origin()
def health():
    """Endpoint for checking health of the server"""
    logger.debug(f"Entered /health")
    return "Server is running", 200


@app.route('/execute', methods=['POST'])
@cross_origin()
def execute_endpoint():
    """Endpoint for executing an instruction"""
    logger.debug(f"Entered /execute moving to box")
    try:
        # Validate if the request has the correct structure
        validate_json_structure(request)
        logger.debug(f"Entered /execute with request: {request.json}")
        data = SendScaleRequestSchema().load(request.json)

        # Parse the instruction
        amount = data.get('amount')
        size_int = data.get('size')
        size = sizes[size_int]
        parsed_instruction = f"Instruction: {size} {amount}"

        # Send the instruction to the scale
        result = scale_service.send_to_scale(parsed_instruction)
        # Send the instruction to the robot
        festo_service.move_to_box(size_int)

        logger.info(f"Result for /execute: {result}")
        return {"result": result}, 200
    except ValidationError as e:
        logger.error(f'Error: {str(e)}')
        return {"error": str(e)}, 400
    except AttributeError as e:
        logger.error(f'Error: {str(e)}')
        return {"error": str(e)}, 400
    except Exception as e:
        logger.error(f'Error: {str(e)}')
        return {"error": {e}}, 500


@app.route('/ready', methods=['POST'])
@cross_origin()
def ready():
    """Endpoint for setting the motors to ready state"""
    logger.debug(f"Entered /ready")
    try:
        festo_service.get_motors_ready()
        return {"result": True}, 200
    except Exception as e:
        logger.error(f'Error: {str(e)}')
        return {"error": {e}}, 500


@app.route('/gripper/open', methods=['POST'])
@cross_origin()
def gripper_open():
    """Endpoint for opening the gripper"""
    logger.debug(f"Entered /gripper/open")
    try:
        festo_service.open_gripper()
        return {"result": True}, 200
    except Exception as e:
        logger.error(f'Error: {str(e)}')
        return {"error": {e}}, 500


@app.route('/gripper/close', methods=['POST'])
@cross_origin()
def gripper_close():
    """Endpoint for closing the gripper"""
    logger.debug(f"Entered /gripper/close")
    try:
        festo_service.close_gripper()
        return {"result": True}, 200
    except Exception as e:
        logger.error(f'Error: {str(e)}')
        return {"error": {e}}, 500


@app.route('/motor/home', methods=['POST'])
@cross_origin()
def motor_home():
    """Endpoint for homing a motor by index"""
    logger.debug(f"Entered /motor/home")
    try:
        # Validate if the request has the correct structure
        validate_json_structure(request)
        data = HomeMotorRequestSchema().load(request.json)
        logger.debug(f"Valid json structure request for /motor/home: {request.json}")

        # Parse the instruction
        index = data.get('index')

        # Send the instruction to the robot
        result = festo_service.home_motor_by_index(index)

        logger.info(f"Result for /motor/home: {result}")
        return {"result": result}, 200
    except ValidationError as e:
        logger.error(f'Error: {str(e)}')
        return {"error": str(e)}, 400
    except AttributeError as e:
        logger.error(f'Error: {str(e)}')
        return {"error": str(e)}, 400
    except Exception as e:
        logger.error(f'Error: {str(e)}')
        return {"error": {e}}, 500


@app.route('/motor/ready', methods=['POST'])
@cross_origin()
def motor_ready():
    """Endpoint for setting a motor to ready state by index"""
    logger.debug(f"Entered /motor/ready")
    try:
        # Validate if the request has the correct structure
        validate_json_structure(request)
        data = ReadyMotorRequestSchema().load(request.json)
        logger.debug(f"Valid json structure request for /motor/ready: {request.json}")

        # Parse the instruction
        index = data.get('index')

        # Send the instruction to the robot
        result = festo_service.motor_ready_by_index(index)

        logger.info(f"Result for /motor/ready: {result}")
        return {"result": result}, 200
    except ValidationError as e:
        logger.error(f'Error: {str(e)}')
        return {"error": str(e)}, 400
    except AttributeError as e:
        logger.error(f'Error: {str(e)}')
        return {"error": str(e)}, 400
    except Exception as e:
        logger.error(f'Error: {str(e)}')
        return {"error": {e}}, 500


@app.route('/motor/move', methods=['POST'])
@cross_origin()
def motor_move():
    """Endpoint for moving a motor by index"""
    logger.debug(f"Entered /motor/move")
    try:
        # Validate if the request has the correct structure
        validate_json_structure(request)
        data = MoveMotorRequestSchema().load(request.json)
        logger.debug(f"Valid json structure request for /motor/move: {request.json}")

        # Parse the instruction
        index = data.get('index')
        posH = int(data.get('posH'), 16)  # convert hex string to integer with base 16
        posL = int(data.get('posL'), 16)  # convert hex string to integer with base 16

        # Send the instruction to the robot
        result = festo_service.move_motor_by_index(index, posH, posL)

        logger.info(f"Result for /motor/move: {result}")
        return {"result": result}, 200
    except ValidationError as e:
        logger.error(f'Error: {str(e)}')
        return {"error": str(e)}, 400
    except AttributeError as e:
        logger.error(f'Error: {str(e)}')
        return {"error": str(e)}, 400
    except Exception as e:
        logger.error(f'Error: {str(e)}')
        return {"error": {e}}, 500


@app.route('/send-to-scale', methods=['POST'])
@cross_origin()
def send_to_scale_endpoint():
    """Endpoint for sending a request to the scale"""
    try:
        # Validate if the request has the correct structure
        validate_json_structure(request)
        data = SendScaleRequestSchema().load(request.json)
        logger.debug(f"Entered /send-to-scale with request: {request.json}")

        # Parse the instruction
        amount = data.get('amount')
        size_int = data.get('size')
        size = sizes[size_int]
        parsed_instruction = f"Instruction: {size} {amount}"

        # Send the instruction to the scale
        result = scale_service.send_to_scale(parsed_instruction)

        logger.info(f"Result: {result}")
        return {"result": result}, 200
    except ValidationError as e:
        logger.error(f'Error: {str(e)}')
        return {"error": str(e)}, 400
    except AttributeError as e:
        logger.error(f'Error: {str(e)}')
        return {"error": str(e)}, 400
    except Exception as e:
        logger.error(f'Error: {str(e)}')
        return {"error": {e}}, 500


if __name__ == '__main__':
    logger.info(f"Flask server starting at {os.getenv('FLASK_HOST')}:{os.getenv('FLASK_PORT')}")
    serve(app, host=os.getenv("FLASK_HOST"), port=os.getenv("FLASK_PORT"))
