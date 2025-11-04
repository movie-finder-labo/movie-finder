from flask import Flask, render_template

app = Flask(__name__)

# Register blueprints
from Routes.Chat.chat_routes import chat_bp
from Routes.Test.test_routes import test_bp  # Add this line

app.register_blueprint(chat_bp, url_prefix='/chat')
app.register_blueprint(test_bp)  # Add this line

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, port=5000)
