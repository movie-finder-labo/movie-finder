from flask import request, jsonify, Blueprint
from backend.libs.database.mongodb import MovieFinderDB

user_bp = Blueprint("user", __name__, url_prefix="/user")

@user_bp.route("/register", methods=['POST'])
async def register():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    fullName = data.get('fullName')
    age = data.get('age')
    genres = data.get('genres')

    # DB connection
    db = MovieFinderDB("mongodb://localhost:27017", "MovieFinder")

    if not username or not password:
        return jsonify({'success': False, 'error': 'Username and password are required'}), 400

    await db.CreateUser(username, password, fullName, age, genres)

    return jsonify({
        "success": True,
        "message": "User created successfully"
    }), 201

@user_bp.route("/login", methods=['POST'])
async def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # DB connection
    db = MovieFinderDB("mongodb://localhost:27017", "MovieFinderDB")

    user = await db.users.GetUserByUsername(username)

    if user and user['password'] == password:
        return jsonify({
            "success": True,
            "message": "Login successful"
        })
    else:
        return jsonify({
            "success": False,
            "message": "Invalid credentials"
        }), 401

@user_bp.route("/logout", methods=['POST'])
def logout():
    return jsonify({"success": True, "message": "Logged out"})