import os
import shutil
import uuid
from datetime import datetime, timedelta
from flask import session


def get_or_create_session_id():
    """Get existing session ID or create a new one."""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']


def get_session_directories(session_id):
    """Get the uploads and clips directories for a specific session."""
    base_dir = os.path.join(os.path.dirname(__file__), 'user_sessions', session_id)
    uploads_dir = os.path.join(base_dir, 'uploads')
    clips_dir = os.path.join(base_dir, 'clips')
    
    return uploads_dir, clips_dir


def create_session_directories(session_id):
    """Create session-specific directories."""
    uploads_dir, clips_dir = get_session_directories(session_id)
    
    # Create uploads directory
    try:
        if os.path.exists(uploads_dir):
            shutil.rmtree(uploads_dir)
        os.makedirs(uploads_dir, exist_ok=True)
    except (OSError, PermissionError) as e:
        print(f"Warning: Could not recreate uploads directory: {e}")
        os.makedirs(uploads_dir, exist_ok=True)
    
    # Create clips directory
    try:
        if os.path.exists(clips_dir):
            shutil.rmtree(clips_dir)
        os.makedirs(clips_dir, exist_ok=True)
    except (OSError, PermissionError) as e:
        print(f"Warning: Could not recreate clips directory: {e}")
        os.makedirs(clips_dir, exist_ok=True)
    
    return uploads_dir, clips_dir


def cleanup_old_sessions(max_age_hours=24):
    """Clean up session directories older than max_age_hours."""
    base_dir = os.path.join(os.path.dirname(__file__), 'user_sessions')
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    
    if not os.path.exists(base_dir):
        return
    
    for session_dir in os.listdir(base_dir):
        session_path = os.path.join(base_dir, session_dir)
        if os.path.isdir(session_path):
            # Check if directory is older than cutoff time
            dir_modified_time = datetime.fromtimestamp(os.path.getmtime(session_path))
            if dir_modified_time < cutoff_time:
                try:
                    shutil.rmtree(session_path)
                    print(f"Cleaned up old session directory: {session_dir}")
                except (OSError, PermissionError) as e:
                    print(f"Warning: Could not clean up session directory {session_dir}: {e}")


def ensure_session_directories():
    """Ensure session directories exist for the current session."""
    session_id = get_or_create_session_id()
    return create_session_directories(session_id)
