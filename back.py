import os
# import main as robot
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

app = Flask("Backend Server")
logger = FlaskLogger(app, "Backend Server")
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

scale_service = ScaleService(logger)
festo_service = FestoService(logger)


@app.route('/')
@cross_origin()
def hello_world():
    logger.debug(f"Entered /")
    return 'Hello, World!'


@app.route('/health', methods=['GET'])
@cross_origin()
def health():
    logger.debug(f"Entered /health")
    return "Server is running", 200


def execute_function(amount, size):
    try:
        amount = int(amount)
        size = int(size)
        result = amount * size
        return result
    except ValueError as e:
        logger.error(f"Conversion error: {e}")
        return "Invalid amount or size"


@app.route('/execute', methods=['POST'])
@cross_origin()
def execute_endpoint():
    logger.debug(f"Entered /execute moving to box")

    try:
        validate_json_structure(request)
        logger.debug(f"Entered /execute with request: {request.json}")
        data = SendScaleRequestSchema().load(request.json)
        amount = data.get('amount')
        size = data.get('size')
        parsed_instruction = f"Instruction: {size} {amount}"


        # TODO. Check if data should be sent to scale here
        # TODO. finish route
        festo_service.move_to_box()  # TODO. according to the request move to specific box
        # robot.move_to_box()  # TODO. Check if this is needed
        result = execute_function(amount, size)
        result = scale_service.send_to_scale(parsed_instruction) # TODO. Check if this should only be a read


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
    logger.debug(f"Entered /ready")
    try:
        # robot.get_motors_ready() TODO. Check if this is needed
        festo_service.get_motors_ready()
        return {"result": True}, 200
    except Exception as e:
        logger.error(f'Error: {str(e)}')
        return {"error": {e}}, 500


@app.route('/gripper/open', methods=['POST'])
@cross_origin()
def gripper_open():
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
    logger.debug(f"Entered /motor/home")
    try:
        validate_json_structure(request)
        data = HomeMotorRequestSchema().load(request.json)
        logger.debug(f"Valid json structure request for /motor/home: {request.json}")
        index = data.get('index')
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
    logger.debug(f"Entered /motor/ready")
    try:
        validate_json_structure(request)
        data = ReadyMotorRequestSchema().load(request.json)
        logger.debug(f"Valid json structure request for /motor/ready: {request.json}")
        index = data.get('index')
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
    logger.debug(f"Entered /motor/move")
    try:
        validate_json_structure(request)
        data = MoveMotorRequestSchema().load(request.json)
        logger.debug(f"Valid json structure request for /motor/move: {request.json}")
        index = data.get('index')
        posH = int(data.get('posH'), 16)  # convert hex string to integer with base 16
        posL = int(data.get('posL'), 16)  # convert hex string to integer with base 16
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
    try:
        validate_json_structure(request)
        data = SendScaleRequestSchema().load(request.json)
        logger.debug(f"Entered /send-to-scale with request: {request.json}")
        amount = data.get('amount')
        size = data.get('size')
        parsed_instruction = f"Instruction: {size} {amount}"
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
