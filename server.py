from flask import Flask, request, jsonify

app = Flask(__name__)

# Middleware to process requests before reaching the endpoint
@app.before_request
def before_request_func():
    print("Middleware: Processing request")
    if request.endpoint == 'process_text' and 'text' not in request.json:
        return jsonify({"error": "text parameter is required"}), 400

# Endpoint to handle incoming text
@app.route('/process_text', methods=['POST'])
def process_text():
    text = request.json.get('text')
    response_text = text.upper()  # Example processing
    return jsonify({"processed_text": response_text})

# New endpoint that returns "Hello" on a GET request
@app.route('/', methods=['GET'])
def hello():
    return "Hello", 200

@app.route('/hello', methods=['GET'])
def main():
    return "Hello", 200


if __name__ == '__main__':
    app.run(debug=True)
