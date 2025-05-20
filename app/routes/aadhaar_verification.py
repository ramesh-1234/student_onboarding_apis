from datetime import datetime
import os
import uuid
from flask import Blueprint, render_template, request, jsonify
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import AadhaarDetails, Mobile, Application, AccountPreferences

verify_aadhaar_bp = Blueprint('aadhaar_verification', __name__)
UPLOAD_FOLDER = 'uploads'


@verify_aadhaar_bp.route('/aadhaar-verification', methods=['POST'])
def aadhaar_verification():
    mobile = request.form.get('mobile')
    name = request.form.get('name')
    dob = request.form.get('dob')
    gender = request.form.get('gender')
    aadhaar_number = request.form.get('aadhaar_number')
    address = request.form.get('address')
    pincode = request.form.get('pincode')
    city = request.form.get('city')
    state = request.form.get('state')
    country = request.form.get('country')
    image = request.files.get('aadhaar_image')

    if not all([mobile, name, dob, gender, aadhaar_number, address, pincode, image]):
        return jsonify({'status': 400, 'error': 'All Aadhaar details and image are required'}), 400

    mobile_entry = Mobile.query.filter_by(mobile=mobile).first()
    if not mobile_entry:
        return jsonify({'status': 404, 'error': 'Mobile number not found'}), 404

    application = Application.query.filter_by(
        mobile_id=mobile_entry.id).first()
    if not application:
        return jsonify({'status': 403, 'error': 'Mobile not verified. Please complete OTP verification first.'}), 403

    preferences = AccountPreferences.query.filter_by(
        mobile_id=mobile_entry.id).first()
    if not preferences:
        return jsonify({'status': 403, 'error': 'Please complete account preference selection before Aadhaar verification.'}), 403

    try:
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        filename = secure_filename(image.filename)
        unique_filename = f'aadhaar_{uuid.uuid4().hex}_{filename}'
        relative_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        absolute_path = os.path.join(os.getcwd(), relative_path)
        image.save(absolute_path)

        existing = AadhaarDetails.query.filter_by(
            mobile_id=mobile_entry.id).first()
        if existing:
            return jsonify({
                'status': 409,
                'message': 'Aadhaar details already submitted for this mobile',
                'application_number': application.application_number
            }), 409

        details = AadhaarDetails(
            mobile_id=mobile_entry.id,
            application_id=application.id,
            name=name,
            dob=dob,
            gender=gender.capitalize(),
            aadhaar_number=aadhaar_number,
            address=address,
            pincode=pincode,
            city=city,
            state=state,
            country=country,
            aadhaar_image_path=relative_path
        )
        db.session.add(details)
        db.session.commit()

        aadhaar_image_url = f"http://localhost:8000/{relative_path.replace(os.sep, '/')}"

        return jsonify({
            'status': 200,
            'message': 'Aadhaar details saved successfully',
            'application_number': application.application_number,
            'data': {
                'name': name,
                'dob': dob,
                'gender': gender.capitalize(),
                'aadhaar_number': aadhaar_number,
                'address': address,
                'pincode': pincode,
                'city': city,
                'state': state,
                'country': country,
                'aadhaar_image_path': aadhaar_image_url,
                'created_at': details.created_at.isoformat() if details.created_at else None
            }
        }), 200

    except Exception as e:
        return jsonify({'status': 500, 'error': 'Failed to save Aadhaar details', 'details': str(e)}), 500


@verify_aadhaar_bp.route('/aadhaar-verification', methods=['PUT'])
def update_aadhaar_details():
    mobile = request.form.get('mobile')
    if not mobile:
        return jsonify({'status': 400, 'error': 'Mobile number is required'}), 400

    mobile_entry = Mobile.query.filter_by(mobile=mobile).first()
    if not mobile_entry:
        return jsonify({'status': 404, 'error': 'Mobile number not found'}), 404

    aadhaar_details = AadhaarDetails.query.filter_by(
        mobile_id=mobile_entry.id).first()
    if not aadhaar_details:
        return jsonify({'status': 404, 'error': 'Aadhaar details not found for this mobile'}), 404

    # Optional fields
    aadhaar_details.name = request.form.get('name') or aadhaar_details.name
    aadhaar_details.dob = request.form.get('dob') or aadhaar_details.dob
    aadhaar_details.gender = request.form.get(
        'gender') or aadhaar_details.gender
    aadhaar_details.aadhaar_number = request.form.get(
        'aadhaar_number') or aadhaar_details.aadhaar_number
    aadhaar_details.address = request.form.get(
        'address') or aadhaar_details.address
    aadhaar_details.pincode = request.form.get(
        'pincode') or aadhaar_details.pincode
    aadhaar_details.city = request.form.get('city') or aadhaar_details.city
    aadhaar_details.state = request.form.get('state') or aadhaar_details.state
    aadhaar_details.country = request.form.get(
        'country') or aadhaar_details.country

    # Aadhaar image (optional)
    image = request.files.get('aadhaar_image')
    if image:
        filename = secure_filename(image.filename)
        unique_filename = f'aadhaar_{uuid.uuid4().hex}_{filename}'
        relative_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        absolute_path = os.path.join(os.getcwd(), relative_path)
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        image.save(absolute_path)
        aadhaar_details.aadhaar_image_path = relative_path

    aadhaar_details.modified_at = datetime.utcnow()
    db.session.commit()

    aadhaar_image_url = f"http://localhost:8000/{aadhaar_details.aadhaar_image_path.replace(os.sep, '/')}"

    return jsonify({
        'status': 200,
        'message': 'Aadhaar details updated successfully',
        'data': {
            'name': aadhaar_details.name,
            'dob': aadhaar_details.dob,
            'gender': aadhaar_details.gender,
            'aadhaar_number': aadhaar_details.aadhaar_number,
            'address': aadhaar_details.address,
            'pincode': aadhaar_details.pincode,
            'city': aadhaar_details.city,
            'state': aadhaar_details.state,
            'country': aadhaar_details.country,
            'aadhaar_image_path': aadhaar_image_url,
            'created_at': aadhaar_details.created_at,
            'modified_at': aadhaar_details.modified_at
        }
    }), 200


@verify_aadhaar_bp.route('/aadhaar-verification', methods=['DELETE'])
def delete_aadhaar_details():
    mobile = request.args.get('mobile')
    if not mobile:
        return jsonify({'status': 400, 'error': 'Mobile number is required'}), 400

    mobile_entry = Mobile.query.filter_by(mobile=mobile).first()
    if not mobile_entry:
        return jsonify({'status': 404, 'error': 'Mobile number not found'}), 404

    aadhaar_details = AadhaarDetails.query.filter_by(
        mobile_id=mobile_entry.id).first()
    if not aadhaar_details:
        return jsonify({'status': 404, 'error': 'Aadhaar details not found for this mobile'}), 404

    # Optionally delete image file from server
    image_path = aadhaar_details.aadhaar_image_path
    try:
        full_path = os.path.join(os.getcwd(), image_path)
        if os.path.exists(full_path):
            os.remove(full_path)
    except Exception as e:
        pass  # Log or ignore file deletion errors

    db.session.delete(aadhaar_details)
    db.session.commit()

    return jsonify({'status': 200, 'message': 'Aadhaar details deleted successfully'}), 200


@verify_aadhaar_bp.route('/aadhaar-verification', methods=['GET'])
def get_aadhaar_details():
    mobile = request.args.get('mobile')
    if not mobile:
        return jsonify({'status': 400, 'error': 'Mobile number is required'}), 400

    mobile_entry = Mobile.query.filter_by(mobile=mobile).first()
    if not mobile_entry:
        return jsonify({'status': 404, 'error': 'Mobile number not found'}), 404

    aadhaar_details = AadhaarDetails.query.filter_by(
        mobile_id=mobile_entry.id).first()
    if not aadhaar_details:
        return jsonify({'status': 404, 'error': 'Aadhaar details not found for this mobile'}), 404

    aadhaar_image_url = f"http://localhost:8000/{aadhaar_details.aadhaar_image_path.replace(os.sep, '/')}" if aadhaar_details.aadhaar_image_path else None

    return jsonify({
        'status': 200,
        'message': 'Aadhaar details fetched successfully',
        'application_number': aadhaar_details.application.application_number if aadhaar_details.application else None,
        'data': {
            'name': aadhaar_details.name,
            'dob': aadhaar_details.dob,
            'gender': aadhaar_details.gender,
            'aadhaar_number': aadhaar_details.aadhaar_number,
            'address': aadhaar_details.address,
            'pincode': aadhaar_details.pincode,
            'state': aadhaar_details.state,
            'city': aadhaar_details.city,
            'country': aadhaar_details.country,
            'aadhaar_image_path': aadhaar_image_url,
            'created_at': aadhaar_details.created_at.isoformat() if aadhaar_details.created_at else None,
            'modified_at': aadhaar_details.modified_at.isoformat() if aadhaar_details.modified_at else None
        }
    }), 200


@verify_aadhaar_bp.route('/aadhaar-verification-form', methods=['GET'])
def show_aadhaar_verification_form():
    mobile = request.args.get('mobile')
    application_number = request.args.get('application_number')

    if not mobile:
        return "Mobile number is required", 400

    return render_template(
        'aadhaar_details.html',
        mobile=mobile,
        application_number=application_number
    )
