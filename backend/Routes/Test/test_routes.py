from flask import Blueprint, render_template

test_bp = Blueprint("test", __name__)

@test_bp.route('/test')
def frontend_test():
    return render_template('test.html')