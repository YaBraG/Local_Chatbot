import test

from flask import Flask, request, jsonify

app = Flask(__name__)

# Middleware to process requests before reaching the endpoint

response = ""

@app.before_request
def before_request_func():
    print("Middleware: Processing request")
    
    
    
# Endpoint to handle incoming text
@app.route('/process_text', methods=['POST'])
def process_text():
    text = request.json.get('text')
    response = test.ask_llm(text)
    print ("RESPONSE: ", response)
    
    return jsonify({"processed_text": response})

# New endpoint that returns "Hello" on a GET request
@app.route('/', methods=['GET'])
def hello():
    return "Hello", 200

if __name__ == '__main__':
    app.run(debug=False)
