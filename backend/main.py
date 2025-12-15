from flask import Flask, render_template, send_from_directory
from dotenv import load_dotenv
from os import getenv, path
from libs.database.csv import InitializeMovieData

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
    load_dotenv()
    InitializeMovieData() # First initialization
    app.config['secrect_key'] = getenv("FLASK_SECRET_KEY")
    app.run(threaded=True, debug=True, port=5000)