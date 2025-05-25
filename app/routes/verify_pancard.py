from datetime import datetime, timedelta
import re

from flask import Blueprint, jsonify, request
from app.extensions import db

from app.models import Email, PanCard
from app.routes.verify import OTP_EXPIRY_SECONDS, generate_otp, is_email_valid, send_email_otp

verify_pancard_bp = Blueprint('verify-pancard', __name__)


def is_valid_pan(pan):
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
    return re.match(pattern, pan.upper()) is not None


@verify_pancard_bp.route('/verify-pancard', methods=['POST'])
def verify_pancard():
    data = request.get_json()
    email = data.get('email')
    pan_number = data.get('pan_number')

    if not email or not is_email_valid(email):
        return jsonify({'status': 400, 'message': 'Invalid or missing email'}), 400

    if not pan_number or not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', pan_number):
        return jsonify({'status': 400, 'message': 'Invalid PAN number format'}), 400

    otp = str(generate_otp())
    now = datetime.utcnow()
    expiry = now + timedelta(seconds=OTP_EXPIRY_SECONDS)

    email_entry = Email.query.filter_by(email=email).first()
    if not email_entry:
        email_entry = Email(email=email)
        db.session.add(email_entry)
        db.session.commit()

    pan_entry = PanCard.query.filter_by(pan_number=pan_number).first()
    if pan_entry:
        pan_entry.otp = otp
        pan_entry.created_at = now
        pan_entry.expired_at = expiry
        pan_entry.email_id = email_entry.id
        pan_entry.is_verified = False
    else:
        pan_entry = PanCard(
            email_id=email_entry.id,
            pan_number=pan_number,
            otp=otp,
            created_at=now,
            expired_at=expiry,
            is_verified=False
        )
        db.session.add(pan_entry)

    db.session.commit()

    # Send OTP via email
    if not send_email_otp(email, otp):
        return jsonify({'status': 500, 'message': 'Failed to send OTP'}), 500

    return jsonify({
        'status': 200,
        'message': 'PAN verification OTP sent in email',
        'data': {
            # 'otp': otp,  # ❌ Remove in production

            # 'otp': 'otp sent in email, please check and verify',

            'expires_at': expiry.isoformat()
        }
    }), 200


@verify_pancard_bp.route('/verify-pancard-otp', methods=['POST'])
def verify_pancard_otp():
    data = request.get_json()
    pan_number = data.get('pan_number')
    otp = data.get('otp')

    pan_entry = PanCard.query.filter_by(pan_number=pan_number).first()

    if not pan_entry:
        return jsonify({'status': 404, 'message': 'PAN not found'}), 404

    if pan_entry.otp != otp:
        return jsonify({'status': 401, 'message': 'Invalid OTP'}), 401

    if datetime.utcnow() > pan_entry.expired_at:
        return jsonify({'status': 410, 'message': 'OTP expired'}), 410

    pan_entry.is_verified = True
    db.session.commit()

    return jsonify({'status': 200, 'message': 'PAN verified successfully'}), 200
