import test
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Endpoint to handle incoming text
@app.route('/process_text', methods=['POST'])
def process_text():
    text = request.json.get('text')
    response = test.ask_llm(text)
    print ("RESPONSE: ", response)
    
    return jsonify({"processed_text": response})


if __name__ == "__main__":
    # Get the port number from the environment variable or default to 5000
    port = int(os.environ.get("PORT", 2375))

    # Print the port number
    print(f"Running on port {port}")

    app.run(debug=False, host='0.0.0.0', port=port)