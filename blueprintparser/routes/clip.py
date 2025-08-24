from flask import (
    Blueprint, render_template, request, jsonify
)
import os

from ..backend import parser
from ..session_utils import get_or_create_session_id, get_session_directories

bp = Blueprint('clip', __name__)

@bp.route('/clip', methods=('GET', 'POST'))
def clip():
    if request.method == 'POST':
        try:
            session_id = get_or_create_session_id()
            uploads_dir, clips_dir = get_session_directories(session_id)
            blueprint_path = os.path.join(uploads_dir, 'blueprint.pdf')
            b = parser.BlueprintParser(blueprint_path, eps=110, min_samples=100)
            data = request.get_json()
            x0 = data['startX']
            y0 = data['startY']
            x1 = data['endX']
            y1 = data['endY']
            
            # Get sizing options
            sizing_mode = data.get('sizingMode', 'bounding-box')
            fixed_width = data.get('fixedWidth')
            fixed_height = data.get('fixedHeight')

            uuid_tag = b.clip_region(
                data['pageNumber']-1, 
                (x0, y0, x1, y1), 
                data['scale'],
                sizing_mode=sizing_mode,
                fixed_width=fixed_width,
                fixed_height=fixed_height,
                clips_dir=clips_dir
            )
            return jsonify({'success': True, 'uuid': uuid_tag})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    return render_template('register.html')


