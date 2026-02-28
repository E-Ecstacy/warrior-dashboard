"""Main Routes"""
from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    """Main dashboard"""
    return render_template('index.html')
