from flask import Blueprint, render_template, request, jsonify, send_from_directory
import os
import shutil
from ..backend import parser
from ..session_utils import ensure_session_directories, get_or_create_session_id, get_session_directories, cleanup_old_sessions

bp = Blueprint('main', __name__)

@bp.route('/')
def main():
    return render_template('index.html')

@bp.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        # Occasionally cleanup old sessions (10% chance)
        import random
        if random.random() < 0.1:
            cleanup_old_sessions()
            
        # Create session-specific directories
        uploads_dir, clips_dir = ensure_session_directories()
        
        file = request.files['pdf']
        file.save(os.path.join(uploads_dir, 'blueprint.pdf'))

    return render_template('index.html')

@bp.route('/upload/<filename>')
def serve_uploaded_file(filename):
    session_id = get_or_create_session_id()
    uploads_dir, _ = get_session_directories(session_id)
    return send_from_directory(uploads_dir, filename)

@bp.route('/clips/<filename>')
def serve_clips(filename):
    session_id = get_or_create_session_id()
    _, clips_dir = get_session_directories(session_id)
    return send_from_directory(clips_dir, filename)

@bp.route('/save', methods=['POST'])
def save():
    if request.method == 'POST':
        try:
            session_id = get_or_create_session_id()
            uploads_dir, clips_dir = get_session_directories(session_id)
            blueprint_path = os.path.join(uploads_dir, 'blueprint.pdf')
            final_path = os.path.join(clips_dir, 'final.pdf')
            b = parser.BlueprintParser(blueprint_path, eps=110, min_samples=100)
            b.save_clips(clips_dir, final_path)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

@bp.route('/save/<filename>')
def download(filename):
    session_id = get_or_create_session_id()
    _, clips_dir = get_session_directories(session_id)
    return send_from_directory(clips_dir, filename, as_attachment=True)

@bp.route('/delete/<filename>', methods=['DELETE'])
def delete_clip(filename):
    try:
        session_id = get_or_create_session_id()
        _, clips_dir = get_session_directories(session_id)
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
        session_id = get_or_create_session_id()
        uploads_dir, clips_dir = get_session_directories(session_id)
        blueprint_path = os.path.join(uploads_dir, 'blueprint.pdf')
        autoclip_path = os.path.join(clips_dir, 'autoclip.pdf')
        b = parser.BlueprintParser(blueprint_path, eps=110, min_samples=100)
        # b.parse_page(page_number, clips_dir)
        b.auto_clip_page(page_number)
        b.save_clips(clips_dir, autoclip_path)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
