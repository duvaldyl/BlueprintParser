from flask import Blueprint, render_template, request, jsonify, send_from_directory
import os
import shutil
from . import parser

bp = Blueprint('main', __name__)

@bp.route('/')
def main():
    return render_template('index.html')

@bp.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        # Clear and recreate uploads and clips folders to prevent corruption/collision
        uploads_dir = 'blueprintparser/uploads'
        clips_dir = 'blueprintparser/clips'
        
        # Remove and recreate uploads folder
        if os.path.exists(uploads_dir):
            shutil.rmtree(uploads_dir)
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Remove and recreate clips folder
        if os.path.exists(clips_dir):
            shutil.rmtree(clips_dir)
        os.makedirs(clips_dir, exist_ok=True)
        
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

@bp.route('/delete/<filename>', methods=['DELETE'])
def delete_clip(filename):
    try:
        clip_path = os.path.join('blueprintparser/clips', filename)
        if os.path.exists(clip_path):
            os.remove(clip_path)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'File not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

