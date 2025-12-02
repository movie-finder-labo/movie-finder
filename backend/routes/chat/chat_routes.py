from flask import request, jsonify, Blueprint
from libs.services.openai_service import ask_openai
from libs.database.csv import InitializeMovieData
from libs.database.mongodb import MovieFinderDB
from libs.authentication import TokenRequired, DecodeToken

chat_bp = Blueprint("chat", __name__)

def error(err="A serverside error has occured", c: int = 500):
    return jsonify({
            "success": False,
            "error": str(err)
        }), c

@chat_bp.route('/ask', methods=['POST'])
@TokenRequired
def ask():
    """Handle chat messages with OpenAI"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return error("No message provided", 400)
        
        userMessage = data['message']
        token = DecodeToken(data.get('jwt'))
        db = MovieFinderDB()
        user = db.GetUserByUsername(token.get("username"))
        if not user:
            print("Failed to generate chat response: Failed to find user.")
            return error()
        
        userDataQuery = user.Querify()
        question = f"The user has written a message to you. Take the following preferences into consideration when answering: ({userDataQuery}). Avoid mentioning the preferences unless prompted, but give your suggestions. The user's message is the following: \"{userMessage}\""
        
        # Get response from OpenAI
        ai_response = ask_openai(question)
        
        try:
            # Grab the last 13 elements and restore their original order (movie data is reversed by default)
            data = list(InitializeMovieData().values())[-13:]
            data.reverse()
        except IndexError:
            pass
        except Exception as e:
            print(f"Failed to initialize movie data: {e}")
            return error()
        
        return jsonify({
            "success": True,
            "response": {"ai_response": ai_response, "data": data}
        }), 200
    except Exception as e:
        print(f"Failed to retrieve response: {e}")
        return error()