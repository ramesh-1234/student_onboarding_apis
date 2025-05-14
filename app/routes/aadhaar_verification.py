import pytesseract
from PIL import Image
import re
from io import BytesIO
from app.models import AadhaarDetails, Mobile, Application, AccountPreferences
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.extensions import db

verify_aadhaar_bp = Blueprint('aadhaar_verification', __name__)


@verify_aadhaar_bp.route('/aadhaar-verification', methods=['POST'])
def aadhaar_verification():
    mobile = request.form.get('mobile')
    image = request.files.get('aadhaar_image')

    if not mobile or not image:
        return jsonify({'status': 400, 'error': 'Mobile number and Aadhaar image are required'}), 400

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
        img = Image.open(image.stream)
        text = pytesseract.image_to_string(img)

        name_match = re.search(r"(?i)(name|namae)\s*:\s*(.+)", text)
        dob_match = re.search(
            r"(?i)(dob|date of birth)\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})", text)
        gender_match = re.search(r"(?i)\b(male|female|others?)\b", text)
        aadhaar_match = re.search(r"\b\d{4}\s\d{4}\s\d{4}\b", text)

        if not aadhaar_match:
            return jsonify({'status': 400, 'error': 'Aadhaar number not found or invalid in image'}), 400

        aadhaar_number = aadhaar_match.group().replace(" ", "")
        if not re.fullmatch(r'\d{12}', aadhaar_number):
            return jsonify({'status': 400, 'error': 'Invalid Aadhaar number format'}), 400

        existing = AadhaarDetails.query.filter_by(
            mobile_id=mobile_entry.id).first()
        if existing:
            return jsonify({'status': 409, 'message': 'Aadhaar details already submitted for this mobile', 'application_number': application.application_number}), 409

        details = AadhaarDetails(
            mobile_id=mobile_entry.id,
            application_id=application.id,
            name=name_match.group(2).strip() if name_match else None,
            dob=dob_match.group(2) if dob_match else None,
            gender=gender_match.group(
                1).capitalize() if gender_match else None,
            aadhaar_number=aadhaar_number
        )
        db.session.add(details)
        db.session.commit()

        return jsonify({
            'status': 200,
            'message': 'Aadhaar details extracted and saved successfully',
            'application_number': application.application_number,
            'data': {
                'name': details.name,
                'dob': details.dob,
                'gender': details.gender,
                'aadhaar_number': details.aadhaar_number
            }
        }), 200

    except Exception as e:
        return jsonify({'status': 500, 'error': 'Failed to process image', 'details': str(e)}), 500
