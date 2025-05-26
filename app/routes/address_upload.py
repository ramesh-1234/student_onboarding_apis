import os
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import AddressImage, Application, AddressUpload

address_upload_bp = Blueprint(
    'address_upload', __name__, url_prefix='/address')


@address_upload_bp.route('/upload', methods=['POST'])
def upload_address():
    application_number = request.form.get('application_number')
    address_line = request.form.get('address_line')
    city = request.form.get('city')
    state = request.form.get('state')
    pincode = request.form.get('pincode')
    images = request.files.getlist('images')

    if not application_number:
        return jsonify({'status': 400, 'error': 'Application number is required'}), 400

    application = Application.query.filter_by(
        application_number=application_number).first()
    if not application:
        return jsonify({'status': 404, 'error': 'Application not found'}), 404

    # if not address_line or not city or not state or not pincode:
    #     return jsonify({'status': 400, 'error': 'All address fields are required'}), 400

    if not images or len(images) == 0:
        return jsonify({'status': 400, 'error': 'At least one image is required'}), 400

    if len(images) > 2:
        return jsonify({'status': 400, 'error': 'Maximum 2 images allowed'}), 400

    save_dir = os.path.join('uploads', 'address_proof')
    os.makedirs(save_dir, exist_ok=True)

    # Check if address exists and update, else create new
    address = AddressUpload.query.filter_by(
        application_id=application.id).first()
    if address:
        # Delete old images
        for img in address.images:
            try:
                if os.path.exists(img.image_path):
                    os.remove(img.image_path)
            except Exception as e:
                current_app.logger.warning(
                    f"Failed to remove old address image: {img.image_path}, error: {e}")
        # Clear old image entries
        address.images.clear()

        address.address_line = address_line
        address.city = city
        address.state = state
        address.pincode = pincode
        address.modified_at = datetime.utcnow()
    else:
        address = AddressUpload(
            application_id=application.id,
            address_line=address_line,
            city=city,
            state=state,
            pincode=pincode,
            created_at=datetime.utcnow(),
            modified_at=datetime.utcnow()
        )
        db.session.add(address)
        db.session.flush()  # Get address.id before adding images

    # Save new images
    for file in images:
        if file and file.filename:
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
            filename = f"{application_number}_{timestamp}_{secure_filename(file.filename)}"
            image_path = os.path.join(save_dir, filename)
            file.save(image_path)

            address_image = AddressImage(
                address_upload_id=address.id,
                image_path=image_path,
                uploaded_at=datetime.utcnow()
            )
            db.session.add(address_image)

    db.session.commit()

    return jsonify({
        'status': 201,
        'message': 'Address and images uploaded successfully',
        'data': {
            'application_number': application.application_number,
            'address_line': address.address_line,
            'city': address.city,
            'state': address.state,
            'pincode': address.pincode,
            'images': [
                {
                    'image_path': img.image_path,
                    'public_url': f"/uploads/address_proof/{os.path.basename(img.image_path)}"
                } for img in address.images
            ],
            'created_at': address.created_at.isoformat(),
            'modified_at': address.modified_at.isoformat()
        }
    }), 201


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


# @address_upload_bp.route('/address-upload-form', methods=['GET'])
# def show_address_upload_form():
#     mobile = request.args.get('mobile')
#     application_number = request.args.get('application_number')

#     if not mobile:
#         return "Mobile number is required", 400

#     return render_template(
#         'address_details.html',
#         mobile=mobile,
#         application_number=application_number
#     )


@address_upload_bp.route('address-upload-form', methods=['GET'])
def show_address_upload_form():
    return render_template('address_details.html')
