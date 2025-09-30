from flask import Flask, request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)

class User(object):
     username = None
     password_hash = None
@app.route("/", methods=["GET", "POST"])
def homepage():
    if request.method == "POST":
        project_name = request.form.get("project_name")
        print("User entered:", project_name)
        return render_template("website.html", project=project_name)

    return render_template("website.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    data = request.get_json()

    username = data['username']
    password = data['password']

    if not username or not password:
        return jsonify({'error': 'username and password are required'}), 400

    password_hash = generate_password_hash(password)

    new_user = User
    new_user.password_hash = password_hash
    new_user.username = username

@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']


app.run(host="0.0.0.0", port=80)