from flask import (
    Blueprint, render_template, request, jsonify
)

from . import parser

bp = Blueprint('clip', __name__)

@bp.route('/clip', methods=('GET', 'POST'))
def clip():
    if request.method == 'POST':
        try:
            b = parser.BlueprintParser('./blueprintparser/static/uploads/blueprint.pdf', eps=110, min_samples=100)
            data = request.get_json()
            x0 = data['startX']
            y0 = data['startY']
            x1 = data['endX']
            y1 = data['endY']

            b.clip_region(data['pageNumber']-1, (x0, y0, x1, y1), data['scale'])
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500


    return render_template('register.html')


