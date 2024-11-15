import os
import flaskLLM
from flask import Flask, request, jsonify
from flask_cors import CORS


app = Flask(__name__)

CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000","https://miamibookfair2024.com/authors-chatbot"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Endpoint to handle incoming text
@app.route('/process_text', methods=['POST'])
def process_text():
    text = request.json.get('text') # type: ignore
    response = flaskLLM.ask_llm(text)
    print ("RESPONSE: ", response)
    
    return jsonify({"processed_text": response})


if __name__ == "__main__":
    # Get the port number from the environment variable or default to 5000
    port = int(os.environ.get("PORT", 5000))

    # Print the port number
    print(f"Running on port {port}")

    app.run(debug=False, host='0.0.0.0', port=port)