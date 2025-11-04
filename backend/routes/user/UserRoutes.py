from flask import request, jsonify, Blueprint

user_bp = Blueprint("user", __name__, url_prefix="/user")

# Simple in-memory storage for demo
users_db = {}


@user_bp.route("/register", methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    fullName = data.get('fullName')
    age = data.get('age')
    genres = data.get('genres')

    if not username or not password:
        return jsonify({'success': False, 'error': 'Username and password are required'}), 400

    if username in users_db:
        return jsonify({'success': False, 'error': 'User already exists'}), 400

    # Store user in memory
    users_db[username] = {
        'password': password,
        'fullName': fullName,
        'age': age,
        'genres': genres
    }

    return jsonify({
        "success": True,
        "message": "User created successfully"
    }), 201


@user_bp.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = users_db.get(username)

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