from flask import Flask, request
from flask_cors import CORS, cross_origin
import main as robot

app = Flask(__name__)
cors=CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
@cross_origin()
def hello_world():
    return 'Hello, World!'

def execute_function(amount, size):
    try:
        amount = int(amount)
        size = int(size)
        result = amount * size
        return result
    except ValueError as e:
        print(f"Conversion error: {e}")
        return "Invalid amount or size"


@app.route('/execute', methods=['POST'])
def execute_endpoint():
    robot.move_to_box()
    amount = request.json.get('amount')
    size = request.json.get('size')

    if amount is None or size is None:
        return "Invalid request", 400

    result = execute_function(amount, size)

    return {
        'result': result
    }

@app.route('/ready', methods=['POST'])
def ready():
    robot.get_motors_ready()
    return {
        'result': True
    }

if __name__ == '__main__':
    app.run()
