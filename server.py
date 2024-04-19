import os
from flask import Flask, request, jsonify
from Chat_Bot import Baggle_Bot
from collections import deque
import json
import pdb

conversations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conversations/")
os.makedirs(conversations_dir, exist_ok=True)

def delete_conversation_file(token_id):
    conversation_file_path = os.path.join(conversations_dir, f"{token_id}_conversation.json")
    if os.path.exists(conversation_file_path):
        os.remove(conversation_file_path)



app = Flask(__name__)

baggle_bot = Baggle_Bot()

@app.route('/baggle_chatbot', methods=['POST'])
def ask_question():
    data = request.get_json()
    user_input = data.get('user_input')
    token = data.get("token")
    if user_input == "end_convo":
        delete_conversation_file(token)
        return jsonify({'response': 'Thank you'})

    response = baggle_bot.question(token, user_input)
    
    new_response=response.replace("A:","").replace("RESPONSE:","").replace("ANSWER:","").strip()
    
    return jsonify({'response': new_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port="4848")