from flask import Blueprint, render_template, request
import os

bp = Blueprint('main', __name__)

@bp.route('/')
def main():
    return render_template('index.html')

@bp.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        os.makedirs('blueprintparser/static/uploads', exist_ok=True)
        file = request.files['pdf']
        file.save('blueprintparser/static/uploads/blueprint.pdf')

    return render_template('index.html')
