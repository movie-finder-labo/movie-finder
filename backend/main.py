from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a random secret key

# Register blueprints
from Routes.User.UserRoutes import user_bp
from Routes.Homepage.Homepage import homepage_bp
from Routes.Chat.chat_routes import chat_bp

app.register_blueprint(user_bp)
app.register_blueprint(homepage_bp)
app.register_blueprint(chat_bp, url_prefix='/chat')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, port=5000)
