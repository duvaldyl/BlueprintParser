import os
import shutil
import uuid
from datetime import datetime, timedelta

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

    # Create base directories for user sessions
    base_uploads_dir = os.path.join(os.path.dirname(__file__), 'user_sessions')
    os.makedirs(base_uploads_dir, exist_ok=True)
    
    # Clean up old session directories on startup (older than 24 hours)
    from .session_utils import cleanup_old_sessions
    cleanup_old_sessions()

    return app

