import os
from flask import Flask, request, jsonify
from Chat_Bot import Baggle_Bot
from collections import deque
import json
import pdb

# conversations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conversations/")
# os.makedirs(conversations_dir, exist_ok=True)

# # delete the all conversation
# def delete_conversation_file(token_id):
#     conversation_file_path = os.path.join(conversations_dir, f"{token_id}_conversation.json")
#     if os.path.exists(conversation_file_path):
#         os.remove(conversation_file_path)



app = Flask(__name__)

baggle_bot = Baggle_Bot()

# Route for baggle  bot's functionality
@app.route('/baggle_chatbot', methods=['POST'])
def ask_question():
    data = request.get_json()
   
    if 'user_input' not in data:
        return jsonify({'msg':"Please Provide question!"}),400
    if 'conversation_list' not in data:
        return jsonify({'msg':"Please Provide conversatoin list!"}),400
    
    user_input = data.get('user_input')
    conversation = data.get("conversation_list")
    if not conversation:
        conversation =[]
    

    response = baggle_bot.question(conversation, user_input)
    
    new_response=response.replace("A:","").replace("RESPONSE:","").replace("ANSWER:","").strip()
    
    return jsonify({'response': new_response}),200

# Running the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port="8000" ,debug=True)