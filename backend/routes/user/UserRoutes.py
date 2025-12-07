from flask import request, jsonify, render_template, Blueprint
from libs.database.mongodb import MovieFinderDB, PWHash, DuplicateUsernameError
from libs.authentication import TokenRequired, CreateToken, DecodeToken, TryFreeToken
from libs.database.csv import InitializeMovieData

user_bp = Blueprint("user", __name__, url_prefix="/user")

@user_bp.route("/profile", endpoint="profile_page")
def profile():
    """Profile page route"""
    return render_template("profile.html")

@user_bp.route("/register", methods=['POST'], endpoint="register_user")
def register():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    age = data.get('age')
    genres = data.get('genres')
    db = MovieFinderDB()

    if not username or not password:
        return jsonify({'success': False, 'error': 'Username and password are required'}), 400

    try:
        db.CreateUser(username, password, age, genres)
        token = CreateToken(username)
    except DuplicateUsernameError:
        print(f"Failed to register user: User already exists.")
        return jsonify({'success': False, 'error': 'User already exists'}), 400
    except Exception as e:
        print(f"Failed to register user: {e}")
        return jsonify({'success': False, 'error': "An unknown serverside error has occured"}), 400
    return jsonify({"success":True, "message": "Registration successful", "response": {"jwt": token}}), 200


@user_bp.route("/login", methods=['POST'], endpoint="login_user")
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    db = MovieFinderDB()

    user = db.GetUserByUsername(username)

    if user and user.pwh == PWHash(str(password).encode(), user.salt):
        token = CreateToken(username)
        return jsonify({
            "success": True,
            "message": "Login successful",
            "response": {
                "jwt": token
            }
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": "Invalid credentials"
        }), 403

@user_bp.route("/ratemovie", methods=['POST'])
def ratemovie():
    data = request.get_json()
    try:
        token = DecodeToken(data.get('jwt'))
    except Exception:
        print("User tried using bad token")
        return jsonify({'success': False, 'error': "Bad token"}), 401
    movieId = data.get('movieId')
    rating = data.get('rating')
    movieData = InitializeMovieData()
    if not rating:
        return jsonify({'success': False, 'error': "Bad rating"}), 400
    if not movieId or not movieData.get(str(movieId)):
        return jsonify({'success': False, 'error': "Movie does not exist"}), 400
    db = MovieFinderDB()
    user = db.GetUserByUsername(token.get("username"))
    if not user:
        return jsonify({'success': False, 'error': "Missing user"}), 401
    try:
        if not user.RateMovie(movieId, rating):
            return jsonify({'success': False, 'error': "Failed to rate the movie"})
    except LookupError as err:
        print(f"Failed to rate movie: {err}")
        return jsonify({'success': False, 'error': err})
    return jsonify({'success': True, 'message': "Movie Successfully rated"}), 200

@user_bp.route("/fetchmovies", methods=['POST'], endpoint="fetchmovies")
@TokenRequired
def fetchmovies():
    try:
        # Grab the last 13 elements and restore their original order (movie data is reversed by default)
        data = list(InitializeMovieData().values())[-13:]
        data.reverse()
    except IndexError:
        pass
    except Exception as e:
        print(f"Failed to initialize movie data: {e}")
        return jsonify({'success': False, 'error': "A serverside error has occured."})
    return jsonify({'success': True, 'message': "Successfully fetched movie data", 'response': {
        'movieData': data
    }}), 200

@user_bp.route("/delete", methods=['POST'], endpoint="delete_account")
@TokenRequired
def delete_account():
    """Delete user account"""
    data = request.get_json()
    
    try:
        token = DecodeToken(data.get('jwt'))
    except Exception:
        return jsonify({'success': False, 'error': "Bad token"}), 400
    
    confirmation = data.get('confirmation')
    
    if confirmation != "DELETE":
        return jsonify({'success': False, 'error': "Confirmation required"}), 400
    
    db = MovieFinderDB()
    username = token.get("username")
    
    try:
        # Delete user from database
        success = db.DeleteUser(username)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Account deleted successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to delete account"
            }), 400
            
    except Exception as e:
        print(f"Failed to delete account: {e}")
        return jsonify({'success': False, 'error': "An error occurred while deleting account"}), 400

@user_bp.route("/logout", methods=['POST'], endpoint="logout_user")
@user_bp.route("/fetchratings", methods=['POST'])
def fetchratings():
    data = request.get_json()
    try:
        token = DecodeToken(data.get('jwt'))
    except Exception:
        print("User tried using bad token")
        return jsonify({'success': False, 'error': "Bad token"}), 401
    db = MovieFinderDB()
    user = db.GetUserByUsername(token.get('username'))
    if not user:
        return jsonify({'success': False, 'error': "User does not exist"}), 401
    return jsonify({'success': True, 'message': "Successfully fetched user ratings", 'response': {
        'ratingsData': user.ratings
    }}), 200
    
@user_bp.route("/logout", methods=['GET'])
def logout():
    data = request.get_json()
    try:
        token = DecodeToken(data.get('jwt'))
    except Exception:
        print("User tried using bad token")
        return jsonify({'success': False, 'error': "Bad token"}), 401
    if TryFreeToken(token.get('username')):
        return jsonify({'success': True, 'message': f"Successfully logged user {token.get('username')} out"}), 200
    else:
        return jsonify({'success': False, 'error': "User is not logged in"}), 403