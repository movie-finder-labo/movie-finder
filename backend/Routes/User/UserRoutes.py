from flask import request, jsonify, render_template, Blueprint

from backend.moviefinder.mongodb import MovieFinderDB

user_bp = Blueprint("user_bp", __name__, url_prefix="/")

@user_bp.route('/')
def homepage():
    return render_template("homepage.html")
user_bp = Blueprint("user", __name__, url_prefix="/user")

@user_bp.route("/register", methods=['GET', 'POST'])
async def register():
    if request.method == "GET":
        return render_template("userRegistration.html")

    elif request.method == "POST":
        db = MovieFinderDB("localhost:27017", "MovieFinder")
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return jsonify({'Error': 'Username and password are required'}), 400

        try:
            user_id = await db.CreateUser(username, pwh=password)
            return jsonify({"message": "User created", "id": str(user_id)}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400


@user_bp.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']