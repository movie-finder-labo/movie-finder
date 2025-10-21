from flask import request, jsonify, render_template, Blueprint, session, redirect, url_for
import asyncio

user_bp = Blueprint("user", __name__)

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template("index.html")  # This will show the login modal
    elif request.method == "POST":
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # TODO: Add actual authentication logic
        if username and password:
            session['user'] = username
            return jsonify({"success": True, "message": "Login successful"})
        return jsonify({"success": False, "message": "Invalid credentials"})

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # TODO: Add actual registration logic
    if username and password:
        return jsonify({"success": True, "message": "Registration successful"})
    return jsonify({"success": False, "message": "Registration failed"})

@user_bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))