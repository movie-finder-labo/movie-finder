from flask import Flask, render_template

app = Flask(__name__)

# Register blueprints
from routes.user.UserRoutes import user_bp
from routes.chat.chat_routes import chat_bp

app.register_blueprint(user_bp)
app.register_blueprint(chat_bp, url_prefix='/chat')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, port=5000)