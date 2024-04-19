import os
from flask import Flask, request, jsonify
from Chat_Bot import Baggle_Bot  # Importing your Baggle_Bot class from Chat_Bot module
from collections import deque
import json
import pdb  # Importing pdb for debugging

# Directory to store conversation files
conversations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conversations/")
os.makedirs(conversations_dir, exist_ok=True)  # Creating the directory if it doesn't exist

# Function to delete conversation file
def delete_conversation_file(token_id):
    conversation_file_path = os.path.join(conversations_dir, f"{token_id}_conversation.json")
    if os.path.exists(conversation_file_path):
        os.remove(conversation_file_path)

# Creating a Flask web application instance
app = Flask(__name__)

# Creating an instance of Baggle_Bot
baggle_bot = Baggle_Bot()

# Route to handle POST requests to '/baggle_chatbot' endpoint
@app.route('/baggle_chatbot', methods=['POST'])
def ask_question():
    # Getting data from the request
    data = request.get_json()
    user_input = data.get('user_input')  # Getting user input from the request data
    token = data.get("token")  # Getting token from the request data
    
    # If user wants to end the conversation, delete the conversation file and return a response
    if user_input == "end_convo":
        delete_conversation_file(token)
        return jsonify({'response': 'Thank you'})

    # Asking a question to the Baggle_Bot instance
    response = baggle_bot.question(token, user_input)
    
    # Cleaning up the response by removing prefixes like "A:", "RESPONSE:", "ANSWER:", and stripping whitespace
    new_response=response.replace("A:","").replace("RESPONSE:","").replace("ANSWER:","").strip()
    
    # Returning the cleaned response as JSON
    return jsonify({'response': new_response})

# Running the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port="4848")
