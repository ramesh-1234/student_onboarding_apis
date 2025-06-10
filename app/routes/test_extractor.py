from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import cv2
from werkzeug.utils import secure_filename
from app.utils.pan_extractor import extract_pan_photo_signature

test_bp = Blueprint('pan', __name__)


@test_bp.route('/test-extract', methods=['POST'])
def test_extract_pan_data():
    if 'pan_image' not in request.files:
        return jsonify({'status': 400, 'error': 'Missing PAN image file'}), 400

    pan_file = request.files['pan_image']
    upload_dir = 'static/test_uploads'
    os.makedirs(upload_dir, exist_ok=True)

    filename = secure_filename(pan_file.filename)
    pan_path = os.path.join(upload_dir, filename)
    pan_file.save(pan_path)

    try:
        face_crop, sig_crop = extract_pan_photo_signature(pan_path)

        face_path = os.path.join(upload_dir, f"face_{filename}")
        sig_path = os.path.join(upload_dir, f"sig_{filename}")

        cv2.imwrite(face_path, face_crop)
        cv2.imwrite(sig_path, sig_crop)

        return jsonify({
            'status': 200,
            'message': 'Extraction successful',
            'face_image_url': f"http://localhost:8000/{face_path}",
            'signature_image_url': f"http://localhost:8000/{sig_path}"
        })

    except Exception as e:
        return jsonify({'status': 500, 'error': f'Extraction failed: {str(e)}'}), 500
