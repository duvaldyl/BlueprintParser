from flask import Blueprint, render_template, request, jsonify, send_from_directory
import os
from . import parser

bp = Blueprint('main', __name__)

@bp.route('/')
def main():
    return render_template('index.html')

@bp.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        os.makedirs('blueprintparser/uploads', exist_ok=True)
        os.makedirs('blueprintparser/clips', exist_ok=True)
        file = request.files['pdf']
        file.save('blueprintparser/uploads/blueprint.pdf')

    return render_template('index.html')

@bp.route('/upload/<filename>')
def serve_uploaded_file(filename):
    return send_from_directory('uploads', filename)

@bp.route('/clips/<filename>')
def serve_clips(filename):
    return send_from_directory('clips', filename)

@bp.route('/save', methods=['POST'])
def save():
    if request.method == 'POST':
        try:
            b = parser.BlueprintParser("./blueprintparser/uploads/blueprint.pdf", eps=110, min_samples=100)
            b.save_clips('./blueprintparser/clips', './blueprintparser/clips/final.pdf')
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

@bp.route('/save/<filename>')
def download(filename):
    return send_from_directory('clips', filename, as_attachment=True)

