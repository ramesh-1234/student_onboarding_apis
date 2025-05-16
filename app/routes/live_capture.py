import os
import base64
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app
from app.extensions import db
# Assuming you have a LiveImage model
from app.models import Application, Mobile, AadhaarDetails, LiveWebcamPhoto
from werkzeug.utils import secure_filename
live_capture_bp = Blueprint(
    'live_capture', __name__, url_prefix='/live-capture')


@live_capture_bp.route('/')
def capture_page():
    return render_template('live_capture.html')


@live_capture_bp.route('/upload', methods=['POST'])
def upload_live_image():
    application_number = request.form.get('application_number')

    if not application_number:
        return jsonify({'status': 400, 'error': 'Application number is required'}), 400

    image = request.files.get('image')
    if not image:
        return jsonify({'status': 400, 'error': 'Image is required'}), 400

    # Get application
    application = Application.query.filter_by(
        application_number=application_number).first()
    if not application:
        return jsonify({'status': 404, 'error': 'Application not found'}), 404

    mobile = application.mobile
    if not mobile:
        return jsonify({'status': 404, 'error': 'Mobile not found for this application'}), 404

    aadhaar = AadhaarDetails.query.filter_by(mobile_id=mobile.id).first()
    if not aadhaar:
        return jsonify({'status': 404, 'error': 'Aadhaar not found for this mobile'}), 404

    # Check if a live photo already exists
    live_photo = LiveWebcamPhoto.query.filter_by(
        mobile_id=mobile.id, aadhaar_id=aadhaar.id).first()

    # Save image
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    filename = f"{mobile.mobile}_{timestamp}.jpg"
    save_dir = os.path.join('uploads', 'live_image')
    os.makedirs(save_dir, exist_ok=True)
    image_path = os.path.join(save_dir, secure_filename(filename))
    image.save(image_path)

    # If previous photo exists, delete file and update record
    if live_photo:
        old_image_path = live_photo.image_path
        if old_image_path and os.path.exists(old_image_path):
            try:
                os.remove(old_image_path)
            except Exception as e:
                current_app.logger.warning(
                    f"Failed to remove old image file: {old_image_path}, error: {e}"
                )

        live_photo.image_path = image_path
        live_photo.created_at = datetime.utcnow()
    else:
        live_photo = LiveWebcamPhoto(
            mobile_id=mobile.id,
            aadhaar_id=aadhaar.id,
            image_path=image_path
        )
        db.session.add(live_photo)

    db.session.commit()

    return jsonify({
        'status': 201,
        'message': 'Live image uploaded and saved successfully',
        'data': {
            'photo_id': live_photo.id,
            'image_path': image_path,
            'public_url': f"/uploads/live_image/{filename}",
            'created_at': live_photo.created_at.isoformat(),
            'application_number': application.application_number
        }
    })


@live_capture_bp.route('/upload', methods=['GET'])
def get_uploaded_live_image():
    application_number = request.args.get('application_number')

    if not application_number:
        return jsonify({'status': 400, 'error': 'Application number is required'}), 400

    # Fetch application by application_number
    application = Application.query.filter_by(
        application_number=application_number).first()
    if not application:
        return jsonify({'status': 404, 'error': 'Application not found'}), 404

    mobile = application.mobile
    if not mobile:
        return jsonify({'status': 404, 'error': 'Mobile not found for this application'}), 404

    aadhaar = AadhaarDetails.query.filter_by(mobile_id=mobile.id).first()
    if not aadhaar:
        return jsonify({'status': 404, 'error': 'Aadhaar not found for this mobile'}), 404

    # Get latest live photo for this mobile and aadhaar
    photo = LiveWebcamPhoto.query.filter_by(
        mobile_id=mobile.id,
        aadhaar_id=aadhaar.id
    ).order_by(LiveWebcamPhoto.created_at.desc()).first()

    if not photo:
        return jsonify({'status': 404, 'error': 'No live photo found for the given application'}), 404

    return jsonify({
        'status': 200,
        'message': 'Live photo retrieved successfully',
        'data': {
            'photo_id': photo.id,
            'image_path': photo.image_path,
            'public_url': f"http://localhost:8000/uploads/live_image/{os.path.basename(photo.image_path)}",
            'created_at': photo.created_at.isoformat(),
            'application_number': application.application_number
        }
    }), 200
