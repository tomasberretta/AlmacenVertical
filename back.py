from flask import Flask, request
from flask_cors import CORS, cross_origin

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
    amount = request.json.get('amount')
    size = request.json.get('size')

    if amount is None or size is None:
        return "Invalid request", 400

    result = execute_function(amount, size)

    return {
        'result': result
    }

if __name__ == '__main__':
    app.run()
