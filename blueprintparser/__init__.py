import os
import shutil

from flask import Flask
from .routes import clip 
from .routes import main 


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, template_folder="./templates")

    app.register_blueprint(main.bp)
    app.register_blueprint(clip.bp)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
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
    
    # Remove and recreate uploads folder
    if os.path.exists(uploads_dir):
        shutil.rmtree(uploads_dir)
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Remove and recreate clips folder
    if os.path.exists(clips_dir):
        shutil.rmtree(clips_dir)
    os.makedirs(clips_dir, exist_ok=True)

    return app

