from flask import request, jsonify, Blueprint
from libs.database.mongodb import MovieFinderDB, PWHash, DuplicateUsernameError
from libs.authentication import TokenRequired, CreateToken, DecodeToken
from libs.database.csv import InitializeMovieData

user_bp = Blueprint("user", __name__, url_prefix="/user")

@user_bp.route("/register", methods=['POST'])
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


@user_bp.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    db = MovieFinderDB()

    user = db.GetUserByUsername(username)
    print(user.Querify())

    if user and user.pwh == PWHash(str(password).encode(), user.salt):
        token = CreateToken(username)
        return jsonify({
            "success": True,
            "message": "Login successful",
            "response": {
                "jwt": token
            }
        })
    else:
        return jsonify({
            "success": False,
            "error": "Invalid credentials"
        }), 401

@user_bp.route("/ratemovie", methods=['POST'])
@TokenRequired
def ratemovie():
    data = request.get_json()
    try:
        token = DecodeToken(data.get('jwt'))
    except Exception:
        print("User tried using bad token")
        return jsonify({'success': False, 'error': "Bad token"}), 400
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
        return jsonify({'success': False, 'error': "Missing user"}), 400
    try:
        user.RateMovie(movieId, rating)
    except LookupError as err:
        print(f"Failed to rate movie: {err}")
        return jsonify({'success': False, 'message': err})
        
    return jsonify({'success': True, 'message': "Movie Successfully rated"})

@user_bp.route("/logout", methods=['POST'])
def logout():
    return jsonify({"success": True, "message": "Logged out"})