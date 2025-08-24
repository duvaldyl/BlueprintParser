from flask import Blueprint, render_template, request, jsonify, send_from_directory
import os
import shutil
from ..backend import parser

bp = Blueprint('main', __name__)

@bp.route('/')
def main():
    return render_template('index.html')

@bp.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        # Clear and recreate uploads and clips folders to prevent corruption/collision
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        clips_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'clips')
        
        # Remove and recreate uploads folder with error handling
        try:
            if os.path.exists(uploads_dir):
                shutil.rmtree(uploads_dir)
            os.makedirs(uploads_dir, exist_ok=True)
        except (OSError, PermissionError):
            # If we can't recreate, just ensure it exists
            os.makedirs(uploads_dir, exist_ok=True)
        
        # Remove and recreate clips folder with error handling
        try:
            if os.path.exists(clips_dir):
                shutil.rmtree(clips_dir)
            os.makedirs(clips_dir, exist_ok=True)
        except (OSError, PermissionError):
            # If we can't recreate, just ensure it exists
            os.makedirs(clips_dir, exist_ok=True)
        
        file = request.files['pdf']
        file.save(os.path.join(uploads_dir, 'blueprint.pdf'))

    return render_template('index.html')

@bp.route('/upload/<filename>')
def serve_uploaded_file(filename):
    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    return send_from_directory(uploads_dir, filename)

@bp.route('/clips/<filename>')
def serve_clips(filename):
    clips_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'clips')
    return send_from_directory(clips_dir, filename)

@bp.route('/save', methods=['POST'])
def save():
    if request.method == 'POST':
        try:
            uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
            clips_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'clips')
            blueprint_path = os.path.join(uploads_dir, 'blueprint.pdf')
            final_path = os.path.join(clips_dir, 'final.pdf')
            b = parser.BlueprintParser(blueprint_path, eps=110, min_samples=100)
            b.save_clips(clips_dir, final_path)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

@bp.route('/save/<filename>')
def download(filename):
    clips_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'clips')
    return send_from_directory(clips_dir, filename, as_attachment=True)

@bp.route('/delete/<filename>', methods=['DELETE'])
def delete_clip(filename):
    try:
        clips_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'clips')
        clip_path = os.path.join(clips_dir, filename)
        if os.path.exists(clip_path):
            os.remove(clip_path)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'File not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/autoclip/page', methods=['POST'])
def autoclip_page():
    try:
        data = request.get_json()
        page_number = data['pageNumber']
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        clips_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'clips')
        blueprint_path = os.path.join(uploads_dir, 'blueprint.pdf')
        autoclip_path = os.path.join(clips_dir, 'autoclip.pdf')
        b = parser.BlueprintParser(blueprint_path, eps=110, min_samples=100)
        # b.parse_page(page_number, clips_dir)
        b.auto_clip_page(page_number)
        b.save_clips(clips_dir, autoclip_path)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
