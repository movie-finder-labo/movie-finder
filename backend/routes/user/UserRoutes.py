from flask import request, jsonify, Blueprint
from libs.database.mongodb import MovieFinderDB
import bcrypt

user_bp = Blueprint("user", __name__, url_prefix="/user")

@user_bp.route("/register", methods=['POST'])
async def register():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')
    fullName = data.get('fullName')
    age = data.get('age')
    genres = data.get('genres')

    # DB connection
    db = MovieFinderDB("mongodb://localhost:27017", "MovieFinder")

    if not email or not password:
        return jsonify({'success': False, 'error': 'email and password are required'}), 400

    await db.CreateUser(email, password, fullName, age, genres)

    return jsonify({
        "success": True,
        "message": "User created successfully"
    }), 201

@user_bp.route("/login", methods=['POST'])
async def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "email and password required"
        }), 400
    
    # DB connection
    db = MovieFinderDB("mongodb://localhost:27017", "MovieFinderDB")

    user = await db.users.GetUserByEmail(email)
    if not user:
        return jsonify({
            "success": False,
            "message": "Invalid credentials"
        }), 401
    
    stored_hash = user["pwh"].encode("utf-8")
    if MovieFinderDB.verify_password(stored_hash,password):
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