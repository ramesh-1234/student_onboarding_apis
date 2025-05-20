import os
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import Application, AddressUpload

address_upload_bp = Blueprint(
    'address_upload', __name__, url_prefix='/address')


@address_upload_bp.route('/upload', methods=['POST'])
def upload_address():
    application_number = request.form.get('application_number')
    address_line = request.form.get('address_line')
    city = request.form.get('city')
    state = request.form.get('state')
    pincode = request.form.get('pincode')
    image = request.files.get('image')

    if not application_number:
        return jsonify({'status': 400, 'error': 'Application number is required'}), 400

    application = Application.query.filter_by(
        application_number=application_number).first()
    if not application:
        return jsonify({'status': 404, 'error': 'Application not found'}), 404

    if not address_line or not city or not state or not pincode or not image:
        return jsonify({'status': 400, 'error': 'All address fields and image are required'}), 400

    # Save image
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    filename = f"{application_number}_{timestamp}.jpg"
    save_dir = os.path.join('uploads', 'address_proof')
    os.makedirs(save_dir, exist_ok=True)
    image_path = os.path.join(save_dir, secure_filename(filename))
    image.save(image_path)

    # Check if address already exists for application and override
    address = AddressUpload.query.filter_by(
        application_id=application.id).first()
    if address:
        # Delete old image file if exists
        old_image_path = address.image_path
        if old_image_path and os.path.exists(old_image_path):
            try:
                os.remove(old_image_path)
            except Exception as e:
                current_app.logger.warning(
                    f"Failed to remove old address image: {old_image_path}, error: {e}")

        address.address_line = address_line
        address.city = city
        address.state = state
        address.pincode = pincode
        address.image_path = image_path
        address.modified_at = datetime.utcnow()
    else:
        address = AddressUpload(
            application_id=application.id,
            address_line=address_line,
            city=city,
            state=state,
            pincode=pincode,
            image_path=image_path,
            created_at=datetime.utcnow(),
            modified_at=datetime.utcnow()
        )
        db.session.add(address)

    db.session.commit()

    return jsonify({
        'status': 201,
        'message': 'Address uploaded successfully',
        'data': {
            'application_number': application.application_number,
            'address_line': address.address_line,
            'city': address.city,
            'state': address.state,
            'pincode': address.pincode,
            'image_path': address.image_path,
            'public_url': f"/uploads/address_proof/{os.path.basename(address.image_path)}",
            'created_at': address.created_at.isoformat(),
            'modified_at': address.modified_at.isoformat()
        }
    })


@address_upload_bp.route('/upload', methods=['GET'])
def get_uploaded_address():
    application_number = request.args.get('application_number')

    if not application_number:
        return jsonify({'status': 400, 'error': 'Application number is required'}), 400

    application = Application.query.filter_by(
        application_number=application_number).first()
    if not application:
        return jsonify({'status': 404, 'error': 'Application not found'}), 404

    address = AddressUpload.query.filter_by(application_id=application.id).order_by(
        AddressUpload.created_at.desc()
    ).first()

    if not address:
        return jsonify({'status': 404, 'error': 'No address uploaded for this application'}), 404

    return jsonify({
        'status': 200,
        'message': 'Address data retrieved successfully',
        'data': {
            'application_number': application.application_number,
            'address_line': address.address_line,
            'city': address.city,
            'state': address.state,
            'pincode': address.pincode,
            'image_path': address.image_path,
            'public_url': f"/uploads/address_proof/{os.path.basename(address.image_path)}",
            'created_at': address.created_at.isoformat(),
            'modified_at': address.modified_at.isoformat()
        }
    }), 200


@address_upload_bp.route('/upload', methods=['PUT'])
def update_address():
    data = request.form
    application_number = data.get('application_number')

    if not application_number:
        return jsonify({'status': 400, 'error': 'Application number is required'}), 400

    application = Application.query.filter_by(
        application_number=application_number).first()
    if not application:
        return jsonify({'status': 404, 'error': 'Application not found'}), 404

    address = AddressUpload.query.filter_by(
        application_id=application.id).first()
    if not address:
        return jsonify({'status': 404, 'error': 'Address not found for update'}), 404

    # Update fields if present
    address.address_line = data.get('address_line', address.address_line)
    address.city = data.get('city', address.city)
    address.state = data.get('state', address.state)
    address.pincode = data.get('pincode', address.pincode)

    image = request.files.get('image')
    if image:
        # Replace image
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
        filename = f"{application_number}_{timestamp}.jpg"
        save_dir = os.path.join('uploads', 'address_proof')
        os.makedirs(save_dir, exist_ok=True)
        image_path = os.path.join(save_dir, secure_filename(filename))
        image.save(image_path)

        # Delete old image
        if os.path.exists(address.image_path):
            os.remove(address.image_path)

        address.image_path = image_path

    address.modified_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'status': 200, 'message': 'Address updated successfully'})


@address_upload_bp.route('/upload', methods=['DELETE'])
def delete_uploaded_address():
    application_number = request.args.get('application_number')

    if not application_number:
        return jsonify({'status': 400, 'error': 'Application number is required'}), 400

    application = Application.query.filter_by(
        application_number=application_number).first()
    if not application:
        return jsonify({'status': 404, 'error': 'Application not found'}), 404

    address = AddressUpload.query.filter_by(
        application_id=application.id).first()
    if not address:
        return jsonify({'status': 404, 'error': 'Address not found'}), 404

    # Delete image file
    if os.path.exists(address.image_path):
        os.remove(address.image_path)

    db.session.delete(address)
    db.session.commit()

    return jsonify({'status': 200, 'message': 'Address deleted successfully'})


@address_upload_bp.route('/address-upload-form', methods=['GET'])
def show_address_upload_form():
    mobile = request.args.get('mobile')
    application_number = request.args.get('application_number')

    if not mobile:
        return "Mobile number is required", 400

    return render_template(
        'address_details.html',
        mobile=mobile,
        application_number=application_number
    )
