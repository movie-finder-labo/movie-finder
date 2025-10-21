from flask import render_template, Blueprint

homepage_bp = Blueprint("homepage", __name__)

@homepage_bp.route("/home")
def homepage():
    return render_template("homepage.html")