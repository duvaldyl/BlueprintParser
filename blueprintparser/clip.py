from flask import (
    Blueprint, render_template, request, jsonify
)

from . import parser

bp = Blueprint('clip', __name__)

@bp.route('/clip', methods=('GET', 'POST'))
def clip():
    if request.method == 'POST':
        try:
            b = parser.BlueprintParser('./blueprintparser/uploads/blueprint.pdf', eps=110, min_samples=100)
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
                fixed_height=fixed_height
            )
            return jsonify({'success': True, 'uuid': uuid_tag})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    return render_template('register.html')


