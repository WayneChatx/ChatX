# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging
from xai_grok_sdk import XAI
import pytz
from datetime import datetime

app = Flask(__name__, static_url_path='', static_folder='static')
CORS(app)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Hardcoded API key - only for testing, do not use in production
XAI_API_KEY = 'xai-S2TOB7UdKoCQtuWTPp1UlJw3qrE55RSNjMYCpvasF44bio52Aee89nJQnbcCkPLCkYdaNob6VjCkFsQK'
xai_client = XAI(api_key=XAI_API_KEY, model="grok-2-1212")
conversation_history = {}

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/greet', methods=['POST'])
def greet():
    user_lang = request.headers.get('Accept-Language', 'en').split(',')[0][:2]
    greetings = {
        'en': "Hello, how can I assist you today?",
        'es': "Hola, ¿cómo puedo ayudarte hoy?",
        'fr': "Bonjour, comment puis-je vous aider aujourd'hui?",
        'zh': "今天可以幫你什麼？"
    }
    return jsonify({"greeting": greetings.get(user_lang, greetings['en'])})

@app.route('/chat', methods=['POST'])
def chat():
    if request.method != 'POST':
        logger.error("Incorrect HTTP method used for chat")
        return jsonify({"error": "Method not allowed, use POST"}), 405
    
    user_message = request.json.get('message')
    session_id = request.headers.get('session-id', 'default-session')
    
    if session_id not in conversation_history:
        conversation_history[session_id] = {
            'history': [],
            'user_info': {}
        }

    # Removed GeoIP lookup, just storing IP and time
    user_ip = request.remote_addr
    conversation_history[session_id]['user_info'] = {
        'ip': user_ip,
        'time': datetime.now(pytz.utc),
    }

    conversation_history[session_id]['history'].append({"role": "user", "content": user_message})
    try:
        system_message = f"You are Wayne A.I., a sample chatbot by Wayne Sung in Taiwan. The user's IP is {user_ip} and the current UTC time is {conversation_history[session_id]['user_info']['time'].strftime('%Y-%m-%d %H:%M:%S %Z')}. Be caring and humorous. Use a Christian tone only when the user explicitly seeks prayer, comfort, or companionship. Otherwise, maintain a neutral, friendly tone."
        
        messages = [
            {"role": "system", "content": system_message},
            *conversation_history[session_id]['history']
        ]
        logger.debug(f"API Call Payload: {messages}")  # Log the payload for debugging
        
        response = xai_client.invoke(
            messages=messages
        )
        ai_response = response.choices[0].message.content if response.choices else "No response from AI"
        conversation_history[session_id]['history'].append({"role": "assistant", "content": ai_response})
        
        return jsonify({
            "response": ai_response, 
            "user_info": conversation_history[session_id]['user_info']
        })
    except Exception as e:
        logger.exception("An error occurred while processing the chat")
        return jsonify({"error": str(e), "response": "I'm having trouble understanding that. Could you try again?"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)