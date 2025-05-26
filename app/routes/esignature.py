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


# @esignature_bp.route('/upload', methods=['POST'])
# def upload_esignature():
#     application_number = request.form.get('application_number')
#     # optional if esign_image is used
#     esign_canvas = request.files.get('esign_canvas')
#     # optional if esign_canvas is used
#     esign_image = request.files.get('esign_image')
#     pan_image = request.files.get('pan_image')        # required

#     if not application_number or not pan_image or not (esign_canvas or esign_image):
#         return jsonify({
#             'status': 400,
#             'error': 'Application number, PAN image, and one e-signature (image or canvas) are required.'
#         }), 400

#     application = Application.query.filter_by(
#         application_number=application_number).first()
#     if not application:
#         return jsonify({'status': 404, 'error': 'Application not found'}), 404

#     timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')

#     # --- Save e-signature ---
#     esign_dir = os.path.join('uploads', 'esignature')
#     os.makedirs(esign_dir, exist_ok=True)

#     if esign_canvas:
#         esign_file = esign_canvas
#         esign_filename = f"{application_number}_canvas_{timestamp}.png"
#     else:
#         esign_file = esign_image
#         esign_filename = f"{application_number}_upload_{timestamp}.jpg"

#     esign_path = os.path.join(esign_dir, secure_filename(esign_filename))
#     esign_file.save(esign_path)

#     # --- Save PAN card ---
#     pan_dir = os.path.join('uploads', 'pan')
#     os.makedirs(pan_dir, exist_ok=True)
#     pan_filename = f"{application_number}_pan_{timestamp}.jpg"
#     pan_path = os.path.join(pan_dir, secure_filename(pan_filename))
#     pan_image.save(pan_path)

#     # --- Save to DB ---
#     signature = ESignatureUpload.query.filter_by(
#         application_id=application.id).first()

#     if signature:
#         # Remove old files
#         if signature.image_path and os.path.exists(signature.image_path):
#             try:
#                 os.remove(signature.image_path)
#             except Exception as e:
#                 current_app.logger.warning(
#                     f"Failed to remove old e-signature: {e}")

#         if signature.pan_image_path and os.path.exists(signature.pan_image_path):
#             try:
#                 os.remove(signature.pan_image_path)
#             except Exception as e:
#                 current_app.logger.warning(
#                     f"Failed to remove old PAN image: {e}")

#         # Update paths
#         signature.image_path = esign_path
#         signature.pan_image_path = pan_path
#         signature.modified_at = datetime.utcnow()
#     else:
#         signature = ESignatureUpload(
#             application_id=application.id,
#             image_path=esign_path,
#             pan_image_path=pan_path,
#             esign_image_path=esign_path,
#             created_at=datetime.utcnow(),
#             modified_at=datetime.utcnow()
#         )
#         db.session.add(signature)

#     db.session.commit()

#     return jsonify({
#         'status': 201,
#         'message': 'E-signature and PAN card uploaded successfully',
#         'data': {
#             'application_number': application.application_number,
#             'image_path': signature.image_path,
#             'pan_image_path': signature.pan_image_path,
#             'public_url_esign': f"http://localhost:8000/uploads/esignature/{os.path.basename(signature.image_path)}",
#             'public_url_pan': f"http://localhost:8000/uploads/pan/{os.path.basename(signature.pan_image_path)}",
#             'created_at': signature.created_at.isoformat(),
#             'modified_at': signature.modified_at.isoformat()
#         }
#     })


@esignature_bp.route('/upload', methods=['POST'])
def upload_esignature():
    application_number = request.form.get('application_number')
    esign_canvas = request.files.get('esign_canvas')
    pan_image = request.files.get('pan_image')  # required

    if not application_number or not pan_image or not esign_canvas:
        return jsonify({
            'status': 400,
            'error': 'Application number, PAN image, and canvas signature are required.'
        }), 400

    application = Application.query.filter_by(
        application_number=application_number).first()
    if not application:
        return jsonify({'status': 404, 'error': 'Application not found'}), 404

    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')

    # Save e-signature
    esign_dir = os.path.join('uploads', 'esignature')
    os.makedirs(esign_dir, exist_ok=True)
    esign_filename = f"{application_number}_canvas_{timestamp}.png"
    esign_path = os.path.join(esign_dir, secure_filename(esign_filename))
    esign_canvas.save(esign_path)

    # Save PAN card
    pan_dir = os.path.join('uploads', 'pan')
    os.makedirs(pan_dir, exist_ok=True)
    pan_filename = f"{application_number}_pan_{timestamp}.jpg"
    pan_path = os.path.join(pan_dir, secure_filename(pan_filename))
    pan_image.save(pan_path)

    # Save to DB
    signature = ESignatureUpload.query.filter_by(
        application_id=application.id).first()
    if signature:
        # Remove old files
        if signature.image_path and os.path.exists(signature.image_path):
            try:
                os.remove(signature.image_path)
            except Exception as e:
                current_app.logger.warning(
                    f"Failed to remove old e-signature: {e}")

        if signature.pan_image_path and os.path.exists(signature.pan_image_path):
            try:
                os.remove(signature.pan_image_path)
            except Exception as e:
                current_app.logger.warning(
                    f"Failed to remove old PAN image: {e}")

        # Update paths
        signature.image_path = esign_path
        signature.pan_image_path = pan_path
        signature.modified_at = datetime.utcnow()
    else:
        signature = ESignatureUpload(
            application_id=application.id,
            image_path=esign_path,
            pan_image_path=pan_path,
            esign_image_path=esign_path,
            created_at=datetime.utcnow(),
            modified_at=datetime.utcnow()
        )
        db.session.add(signature)

    db.session.commit()

    return jsonify({
        'status': 201,
        'message': 'E-signature and PAN card uploaded successfully',
        'data': {
            'application_number': application.application_number,
            'image_path': signature.image_path,
            'pan_image_path': signature.pan_image_path,
            'public_url_esign': f"http://localhost:8000/uploads/esignature/{os.path.basename(signature.image_path)}",
            'public_url_pan': f"http://localhost:8000/uploads/pan/{os.path.basename(signature.pan_image_path)}",
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
