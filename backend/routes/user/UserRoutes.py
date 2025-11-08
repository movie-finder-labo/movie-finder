from flask import request, jsonify, Blueprint
from libs.database.mongodb import MovieFinderDB, User, PWHash, DuplicateUsername

user_bp = Blueprint("user", __name__, url_prefix="/user")

@user_bp.route("/register", methods=['POST'])
async def register():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    fullName = data.get('fullName')
    age = data.get('age')
    genres = data.get('genres')
    db = MovieFinderDB()

    if not username or not password:
        return jsonify({'success': False, 'error': 'Username and password are required'}), 400

    try:
        user = await db.CreateUser(username, password, age, genres)
    except DuplicateUsername:
        print(f"Failed to register user: User already exists.")
        return jsonify({'success': False, 'error': 'User already exists'}), 400
    except Exception as e:
        print(f"Failed to register user: {e}.")
        return jsonify({'success': False, 'error': "An unknown serverside error has occured"}), 400

    print(f"User created: {user}")

    return jsonify({
        "success": True,
        "message": "User created successfully"
    }), 201


@user_bp.route("/login", methods=['POST'])
async def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    db = MovieFinderDB()

    user = await db.GetUserByUsername(username)

    if user and user.pwh == PWHash(str(password).encode(), user.salt):
        return jsonify({
            "success": True,
            "message": "Login successful",
            "response": {
                "username": user.username,
                "age": user.age,
                "genres": user.genres,
                "created": user.created,
            }
        })
    else:
        return jsonify({
            "success": False,
            "message": "Invalid credentials"
        }), 401


@user_bp.route("/logout", methods=['POST'])
def logout():
    return jsonify({"success": True, "message": "Logged out"})