from flask import Blueprint, request, jsonify, render_template, current_app
from app.models import Application, ESignatureUpload
from app.extensions import db
from werkzeug.utils import secure_filename
import os
from datetime import datetime

esignature_bp = Blueprint('esignature', __name__, url_prefix='/esignature')


@esignature_bp.route('/')
def esignature_form():
    return render_template('esignature_form.html')


@esignature_bp.route('/upload', methods=['POST'])
def upload_esignature():
    application_number = request.form.get('application_number')
    image = request.files.get('image')

    if not application_number or not image:
        return jsonify({'status': 400, 'error': 'Application number and image are required'}), 400

    application = Application.query.filter_by(
        application_number=application_number).first()
    if not application:
        return jsonify({'status': 404, 'error': 'Application not found'}), 404

    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    filename = f"{application_number}_{timestamp}.jpg"
    save_dir = os.path.join('uploads', 'esignature')
    os.makedirs(save_dir, exist_ok=True)
    image_path = os.path.join(save_dir, secure_filename(filename))
    image.save(image_path)

    signature = ESignatureUpload.query.filter_by(
        application_id=application.id).first()
    if signature:
        old_image_path = signature.image_path
        if old_image_path and os.path.exists(old_image_path):
            try:
                os.remove(old_image_path)
            except Exception as e:
                current_app.logger.warning(
                    f"Failed to remove old e-signature image: {old_image_path}, error: {e}")

        signature.image_path = image_path
        signature.modified_at = datetime.utcnow()
    else:
        signature = ESignatureUpload(
            application_id=application.id,
            image_path=image_path,
            created_at=datetime.utcnow(),
            modified_at=datetime.utcnow()
        )
        db.session.add(signature)

    db.session.commit()

    return jsonify({
        'status': 201,
        'message': 'E-signature uploaded successfully',
        'data': {
            'application_number': application.application_number,
            'image_path': signature.image_path,
            'public_url': f"http://localhost:8000/uploads/esignature/{os.path.basename(signature.image_path)}",
            'created_at': signature.created_at.isoformat(),
            'modified_at': signature.modified_at.isoformat()
        }
    })


@esignature_bp.route('/get', methods=['GET'])
def get_esignature():
    application_number = request.args.get('application_number')

    if not application_number:
        return jsonify({'status': 400, 'error': 'Application number is required'}), 400

    application = Application.query.filter_by(
        application_number=application_number).first()
    if not application:
        return jsonify({'status': 404, 'error': 'Application not found'}), 404

    signature = ESignatureUpload.query.filter_by(
        application_id=application.id).first()
    if not signature:
        return jsonify({'status': 404, 'error': 'E-signature not found'}), 404

    return jsonify({
        'status': 200,
        'message': 'E-signature retrieved successfully',
        'data': {
            'application_number': application.application_number,
            'image_path': signature.image_path,
            'public_url': f"http://localhost:8000/uploads/esignature/{os.path.basename(signature.image_path)}",
            'created_at': signature.created_at.isoformat(),
            'modified_at': signature.modified_at.isoformat()
        }
    })


@esignature_bp.route('/update', methods=['PUT'])
def update_esignature():
    application_number = request.form.get('application_number')
    image = request.files.get('image')

    if not application_number or not image:
        return jsonify({'status': 400, 'error': 'Application number and image are required'}), 400

    application = Application.query.filter_by(
        application_number=application_number).first()
    if not application:
        return jsonify({'status': 404, 'error': 'Application not found'}), 404

    signature = ESignatureUpload.query.filter_by(
        application_id=application.id).first()
    if not signature:
        return jsonify({'status': 404, 'error': 'E-signature not found'}), 404

    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    filename = f"{application_number}_{timestamp}.jpg"
    save_dir = os.path.join('uploads', 'esignature')
    os.makedirs(save_dir, exist_ok=True)
    image_path = os.path.join(save_dir, secure_filename(filename))
    image.save(image_path)

    if os.path.exists(signature.image_path):
        os.remove(signature.image_path)

    signature.image_path = image_path
    signature.modified_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'status': 200, 'message': 'E-signature updated successfully'})


@esignature_bp.route('/delete', methods=['DELETE'])
def delete_esignature():
    application_number = request.args.get('application_number')

    if not application_number:
        return jsonify({'status': 400, 'error': 'Application number is required'}), 400

    application = Application.query.filter_by(
        application_number=application_number).first()
    if not application:
        return jsonify({'status': 404, 'error': 'Application not found'}), 404

    signature = ESignatureUpload.query.filter_by(
        application_id=application.id).first()
    if not signature:
        return jsonify({'status': 404, 'error': 'E-signature not found'}), 404

    if os.path.exists(signature.image_path):
        os.remove(signature.image_path)

    db.session.delete(signature)
    db.session.commit()

    return jsonify({'status': 200, 'message': 'E-signature deleted successfully'})
