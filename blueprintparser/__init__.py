import os
import shutil

from flask import Flask
from .routes import clip 
from .routes import main 


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, 
                instance_relative_config=True, 
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), 'static'))

    app.register_blueprint(main.bp)
    app.register_blueprint(clip.bp)

    # Use environment variable for SECRET_KEY, fallback to 'dev' for development
    secret_key = os.environ.get('SECRET_KEY', 'dev')
    
    app.config.from_mapping(
        SECRET_KEY=secret_key,
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        # Production settings
        DEBUG=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true',
        TESTING=False,
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Clear and recreate uploads and clips folders to prevent corruption/collision
    uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    clips_dir = os.path.join(os.path.dirname(__file__), 'clips')
    
    # Remove and recreate uploads folder with error handling
    try:
        if os.path.exists(uploads_dir):
            shutil.rmtree(uploads_dir)
        os.makedirs(uploads_dir, exist_ok=True)
    except (OSError, PermissionError) as e:
        print(f"Warning: Could not recreate uploads directory: {e}")
        # Try to create if it doesn't exist
        os.makedirs(uploads_dir, exist_ok=True)
    
    # Remove and recreate clips folder with error handling
    try:
        if os.path.exists(clips_dir):
            shutil.rmtree(clips_dir)
        os.makedirs(clips_dir, exist_ok=True)
    except (OSError, PermissionError) as e:
        print(f"Warning: Could not recreate clips directory: {e}")
        # Try to create if it doesn't exist
        os.makedirs(clips_dir, exist_ok=True)

    return app

