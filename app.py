from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

OPENAI_API_KEY = 'your_openai_api_key'

@app.route('/api/openai', methods=['POST'])
def call_openai():
    # Get the data from the frontend (client-side)
    user_input = request.json.get('user_input')

    # Prepare the request payload for OpenAI
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}',
    }
    data = {
        'model': 'gpt-3.5-turbo',  # Replace with the model you're using
        'messages': [{'role': 'user', 'content': user_input}],
    }

    # Make a POST request to the OpenAI API
    response = requests.post('https://api.openai.com/v1/chat/completions', json=data, headers=headers)

    # Return the response from OpenAI API back to the frontend
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(debug=True)
