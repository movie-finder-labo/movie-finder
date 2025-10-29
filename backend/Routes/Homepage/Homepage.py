from flask import render_template, Blueprint


homepage_bp = Blueprint("homepage", __name__, url_prefix="/")

@homepage_bp.route("/")
def homepage():
    return render_template("homepage.html")

