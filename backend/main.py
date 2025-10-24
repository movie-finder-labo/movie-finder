from flask import Flask

# Blueprints
from Routes.User.UserRoutes import user_bp
from Routes.Homepage.Homepage import homepage_bp
import asyncio

app = Flask(__name__)

app.register_blueprint(user_bp)  # User routes
app.register_blueprint(homepage_bp) # Homepage routes

if __name__ == "__main__":
    app.run(debug=True)