from flask import request, jsonify, Blueprint
from services.openai_service import ask_openai

chat_bp = Blueprint("chat", __name__)

@chat_bp.route('/ask', methods=['POST'])
def ask():
    """Handle chat messages with OpenAI"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"success": False, "error": "No message provided"}), 400
        
        user_message = data['message']
        
        # Get response from OpenAI
        ai_response = ask_openai(user_message)
        
        return jsonify({
            "success": True,
            "response": ai_response
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500