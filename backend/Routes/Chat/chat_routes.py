from flask import request, jsonify, Blueprint
from services.openai_service import ask_openai
from backend.moviefinder.csv import InitializeMovieData

chat_bp = Blueprint("chat", __name__)

def error(err: str, c: int = 500):
    return jsonify({
            "success": False,
            "error": str(err)
        }), c

@chat_bp.route('/ask', methods=['POST'])
def ask():
    """Handle chat messages with OpenAI"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return error("No message provided", 400)
        
        user_message = data['message']
        
        # Get response from OpenAI
        ai_response = ask_openai(user_message)
        
        try:
            # Grab the last 13 elements and restore their original order (movie data is reversed by default)
            data = list(InitializeMovieData().values())[-15:]
            data.reverse()
        except IndexError:
            pass
        except Exception as e:
            print(f"Failed to initialize movie data: {e}")
            return error("A serverside error has occured")
        
        return jsonify({
            "success": True,
            "response": {"ai_response": ai_response, "data": data}
        }), 200
    except Exception as e:
        print(f"Failed to retrieve response: {e}")
        return error("A serverside error has occured")