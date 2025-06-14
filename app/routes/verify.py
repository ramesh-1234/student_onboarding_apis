from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Email, EmailOTP, MobileOTP, Mobile, Application
from datetime import datetime, timedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import random
import string
import re
import logging
import os
from twilio.rest import Client

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
twilio_whatsapp = os.getenv("TWILIO_WHATSAPP_NUMBER")

twilio_client = Client(account_sid, auth_token)

verify_bp = Blueprint('verify', __name__)

# Configuration
OTP_EXPIRY_SECONDS = 600  # 10 minutes

# Logging
logging.basicConfig(level=logging.DEBUG)


# Utility Functions
def generate_otp():
    return random.randint(100000, 999999)


def generate_application_number():
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    digits = ''.join(random.choices(string.digits, k=6))
    return letters + digits


def is_mobile_valid(mobile):
    return re.fullmatch(r'\d{10}', mobile) is not None


def is_email_valid(email):
    return re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email) is not None


def send_otp_via_sms(mobile, otp):
    try:
        message = twilio_client.messages.create(
            body=f"Your OTP is: {otp}",
            from_=twilio_number,
            to=f"+91{mobile}"  # Ensure proper country code
        )
        logging.info(f"[SMS] OTP sent to {mobile}: SID={message.sid}")
        return {"status": "sent", "sid": message.sid}
    except Exception as e:
        logging.error(f"[SMS] Failed to send OTP to {mobile}: {e}")
        return {"status": "error", "message": str(e)}


def send_otp_via_whatsapp(mobile, otp):
    try:
        message = twilio_client.messages.create(
            body=f"Your WhatsApp OTP is: {otp}",
            from_=twilio_whatsapp,
            to=f"whatsapp:+91{mobile}"  # Ensure proper WhatsApp format
        )
        logging.info(f"[WhatsApp] OTP sent to {mobile}: SID={message.sid}")
        return {"status": "sent", "sid": message.sid}
    except Exception as e:
        logging.error(f"[WhatsApp] Failed to send OTP to {mobile}: {e}")
        return {"status": "error", "message": str(e)}


def send_email_otp(email, otp):
    message = Mail(
        from_email=os.getenv("FROM_EMAIL"),
        to_emails=email,
        subject="Your Verification OTP",
        plain_text_content=f"Your OTP is: {otp}"
    )
    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        logging.info(
            f"Email sent to {email} with status {response.status_code}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email to {email}: {str(e)}")
        return False

# Sendgrid Email API


@verify_bp.route('/verify-email-twilio', methods=['POST'])
def verify_email_twilio():
    data = request.get_json()
    email = data.get('email')

    if not email or not is_email_valid(email):
        return jsonify({
            'status': 400,
            'message': 'Invalid or missing email'
        }), 400

    otp = generate_otp()
    now = datetime.utcnow()
    expiry = now + timedelta(seconds=OTP_EXPIRY_SECONDS)

    # Get or create Email record
    email_entry = Email.query.filter_by(email=email).first()
    if not email_entry:
        email_entry = Email(email=email)
        db.session.add(email_entry)
        db.session.commit()

    # Get or create/update OTP record
    otp_entry = EmailOTP.query.filter_by(email_id=email_entry.id).first()
    if otp_entry:
        otp_entry.otp = otp
        otp_entry.created_at = now
        otp_entry.expired_at = expiry
    else:
        otp_entry = EmailOTP(
            email_id=email_entry.id,
            otp=otp,
            created_at=now,
            expired_at=expiry
        )
        db.session.add(otp_entry)

    db.session.commit()

    if not send_email_otp(email, otp):
        return jsonify({'status': 500, 'message': 'Failed to send OTP email'}), 500

    return jsonify({
        'status': 200,
        'message': 'OTP sent via email successfully',
        'data': {
            'otp': otp,  # ⚠️ Remove in production!
            'created_at': now.isoformat()
        }
    }), 200

# TWilio API


# @verify_bp.route('/verify-mobile-twilio', methods=['POST'])
# def verify_mobile_twilio():
#     data = request.get_json()
#     mobile = data.get('mobile')
#     channel = data.get('channel', 'sms').lower()  # default to SMS

#     if not mobile or not is_mobile_valid(mobile):
#         return jsonify({
#             'status_code': 400,
#             'message': 'Invalid mobile number'
#         }), 400

#     otp = str(generate_otp())
#     logging.debug(f"Generated OTP: {otp}")

#     # Get or create Mobile record
#     mobile_entry = Mobile.query.filter_by(mobile=mobile).first()
#     if not mobile_entry:
#         mobile_entry = Mobile(mobile=mobile)
#         db.session.add(mobile_entry)
#         db.session.commit()

#     # Create or update OTP record
#     now = datetime.utcnow()
#     expiry = now + timedelta(seconds=OTP_EXPIRY_SECONDS)
#     otp_entry = MobileOTP.query.filter_by(mobile_id=mobile_entry.id).first()

#     if otp_entry:
#         otp_entry.otp = otp
#         otp_entry.created_at = now
#         otp_entry.expired_at = expiry
#     else:
#         otp_entry = MobileOTP(
#             mobile_id=mobile_entry.id,
#             otp=otp,
#             created_at=now,
#             expired_at=expiry
#         )
#         db.session.add(otp_entry)

#     db.session.commit()

#     # Send OTP via chosen channel
#     if channel == "whatsapp":
#         send_otp_via_whatsapp(mobile, otp)
#     else:
#         send_otp_via_sms(mobile, otp)

#     return jsonify({
#         'status': 200,
#         'message': f'OTP sent via {channel}',
#         'data': {
#             'otp': otp,  # remove this in production!
#             'created_at': otp_entry.created_at.isoformat()
#         }
#     }), 200


@verify_bp.route('/verify-mobile-twilio', methods=['POST'])
def verify_mobile_twilio():
    data = request.get_json()
    mobile = data.get('mobile')
    channel = data.get('channel', 'sms').lower()

    if not mobile or not is_mobile_valid(mobile):
        return jsonify({
            'status_code': 400,
            'message': 'Invalid mobile number'
        }), 400

    otp = str(generate_otp())
    logging.debug(f"Generated OTP: {otp}")

    # Get or create Mobile record
    mobile_entry = Mobile.query.filter_by(mobile=mobile).first()
    if not mobile_entry:
        mobile_entry = Mobile(mobile=mobile)
        db.session.add(mobile_entry)
        db.session.commit()

    # ==== [EXISTING_APPLICATION_CHECK] ====
    existing_app = Application.query.filter_by(
        mobile_id=mobile_entry.id).first()
    if existing_app:
        return jsonify({
            'status': 200,
            'message': 'Mobile already verified. Existing application found.',
            'data': {
                'application_number': existing_app.application_number,
                'existing': True
            }
        }), 200
    # ==== [/EXISTING_APPLICATION_CHECK] ====

    # Send OTP via Twilio (before storing it)
    if channel == "whatsapp":
        send_result = send_otp_via_whatsapp(mobile, otp)
    else:
        send_result = send_otp_via_sms(mobile, otp)

    if send_result.get("status") != "sent":
        return jsonify({
            'status_code': 400,
            'message': f'Failed to send OTP: {send_result.get("message", "Unknown error")}'
        }), 400

    # Create or update OTP record
    now = datetime.utcnow()
    expiry = now + timedelta(seconds=OTP_EXPIRY_SECONDS)
    otp_entry = MobileOTP.query.filter_by(mobile_id=mobile_entry.id).first()

    if otp_entry:
        otp_entry.otp = otp
        otp_entry.created_at = now
        otp_entry.expired_at = expiry
    else:
        otp_entry = MobileOTP(
            mobile_id=mobile_entry.id,
            otp=otp,
            created_at=now,
            expired_at=expiry
        )
        db.session.add(otp_entry)

    db.session.commit()

    return jsonify({
        'status': 200,
        'message': f'OTP sent via {channel}',
        'data': {
            'otp': otp,  # ⚠️ Remove in production
            'created_at': otp_entry.created_at.isoformat()
        }
    }), 200


@verify_bp.route('/verify-email', methods=['POST'])
def verify_email():
    data = request.get_json()
    email = data.get('email')

    # Validate email format
    if not email or not is_email_valid(email):
        return jsonify({
            'status_code': 400,
            'message': 'Invalid email address'
        }), 400

    otp = str(generate_otp())
    logging.debug(f"Generated OTP for email: {otp}")

    # Get or create Email record
    email_entry = Email.query.filter_by(email=email).first()
    if not email_entry:
        email_entry = Email(email=email)
        db.session.add(email_entry)
        db.session.commit()

    # Get or create/update EmailOTP record
    now = datetime.utcnow()
    expiry = now + timedelta(seconds=OTP_EXPIRY_SECONDS)
    otp_entry = EmailOTP.query.filter_by(email_id=email_entry.id).first()

    if otp_entry:
        otp_entry.otp = otp
        otp_entry.created_at = now
        otp_entry.expired_at = expiry
    else:
        otp_entry = EmailOTP(
            email_id=email_entry.id,
            otp=otp,
            created_at=now,
            expired_at=expiry
        )
        db.session.add(otp_entry)

    db.session.commit()

    return jsonify({
        'status': 200,
        'message': 'OTP sent successfully',
        'data': {
            'otp': otp,  # ⚠️ Remove in production
            'created_at': otp_entry.created_at.isoformat()
        }
    }), 200


@verify_bp.route('/verify-mobile', methods=['POST'])
def verify_mobile():
    data = request.get_json()
    mobile = data.get('mobile')

    if not mobile or not is_mobile_valid(mobile):
        return jsonify({
            'status_code': 400,
            'message': 'Invalid mobile number'
        }), 400

    # Check for existing mobile
    mobile_entry = Mobile.query.filter_by(mobile=mobile).first()

    # If mobile exists, check for an existing application
    if mobile_entry:
        application = Application.query.filter_by(
            mobile_id=mobile_entry.id).first()
        if application:
            return jsonify({
                'status': 200,
                'message': 'Customer already exists with an application',
                'data': {
                    'application_number': application.application_number,
                    'status': application.status
                }
            }), 200

    # Proceed with OTP generation
    otp = str(generate_otp())
    logging.debug(f"Generated OTP: {otp}")

    # If mobile does not exist, create a new Mobile entry
    if not mobile_entry:
        mobile_entry = Mobile(mobile=mobile)
        db.session.add(mobile_entry)
        db.session.commit()

    now = datetime.utcnow()
    expiry = now + timedelta(seconds=OTP_EXPIRY_SECONDS)

    # Create or update OTP entry
    otp_entry = MobileOTP.query.filter_by(mobile_id=mobile_entry.id).first()
    if otp_entry:
        otp_entry.otp = otp
        otp_entry.created_at = now
        otp_entry.expired_at = expiry
    else:
        otp_entry = MobileOTP(
            mobile_id=mobile_entry.id,
            otp=otp,
            created_at=now,
            expired_at=expiry
        )
        db.session.add(otp_entry)

    db.session.commit()

    return jsonify({
        'status': 200,
        'message': 'OTP sent successfully',
        'data': {
            'otp': otp,
            'created_at': otp_entry.created_at.isoformat()
        }
    }), 200


# Route: Verify OTP
@verify_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    mobile = data.get('mobile')
    otp_input = data.get('otp')

    if not mobile or not otp_input:
        return jsonify({
            'status': 400,
            'message': 'Mobile number and OTP are required'
        }), 400

    mobile_entry = Mobile.query.filter_by(mobile=mobile).first()
    if not mobile_entry:
        return jsonify({
            'status': 404,
            'message': 'Mobile number not found'
        }), 404

    otp_record = MobileOTP.query.filter_by(mobile_id=mobile_entry.id).first()
    if not otp_record:
        return jsonify({
            'status': 404,
            'message': 'No OTP request found for this mobile number. Please request again.'
        }), 404

    now = datetime.utcnow()
    if otp_record.expired_at < now:
        db.session.delete(otp_record)
        db.session.commit()
        return jsonify({
            'status': 400,
            'message': 'OTP expired. Please request again.',
            'data': {
                'created_at': otp_record.created_at.isoformat(),
                'expired_at': otp_record.expired_at.isoformat()
            }
        }), 400

    if otp_record.otp != str(otp_input):
        return jsonify({
            'status': 401,
            'message': 'Invalid OTP',
            'data': {
                'created_at': otp_record.created_at.isoformat(),
                'expired_at': otp_record.expired_at.isoformat()
            }
        }), 401

    db.session.delete(otp_record)

    # Check if application already exists
    existing_app = Application.query.filter_by(
        mobile_id=mobile_entry.id).first()
    if existing_app:
        db.session.commit()
        return jsonify({
            'status': 200,
            'message': 'Mobile number verified successfully.',
            'data': {
                'application_number': existing_app.application_number,
                'created_at': otp_record.created_at.isoformat(),
                'expired_at': otp_record.expired_at.isoformat()
            }
        }), 200

    # Create new application
    app_number = generate_application_number()
    new_application = Application(
        mobile_id=mobile_entry.id,
        application_number=app_number
    )
    db.session.add(new_application)
    db.session.commit()

    return jsonify({
        'status': 200,
        'message': 'Mobile number verified successfully.',
        'data': {
            'application_number': app_number,
            'created_at': otp_record.created_at.isoformat(),
            'expired_at': otp_record.expired_at.isoformat()
        }
    }), 200

# Route: Verify OTP


@verify_bp.route('/verify-otp-twilio', methods=['POST'])
def verify_otp_twilio():
    data = request.get_json()
    mobile = data.get('mobile')
    otp_input = data.get('otp')

    if not mobile or not otp_input:
        return jsonify({
            'status': 400,
            'message': 'Mobile number and OTP are required'
        }), 400

    mobile_entry = Mobile.query.filter_by(mobile=mobile).first()
    if not mobile_entry:
        return jsonify({
            'status': 404,
            'message': 'Mobile number not found'
        }), 404

    otp_record = MobileOTP.query.filter_by(mobile_id=mobile_entry.id).first()
    if not otp_record:
        return jsonify({
            'status': 404,
            'message': 'No OTP request found for this mobile number. Please request again.'
        }), 404

    now = datetime.utcnow()
    if otp_record.expired_at < now:
        db.session.delete(otp_record)
        db.session.commit()
        return jsonify({
            'status': 400,
            'message': 'OTP expired. Please request again.',
            'data': {
                'created_at': otp_record.created_at.isoformat(),
                'expired_at': otp_record.expired_at.isoformat()
            }
        }), 400

    if otp_record.otp != str(otp_input):
        return jsonify({
            'status': 401,
            'message': 'Invalid OTP',
            'data': {
                'created_at': otp_record.created_at.isoformat(),
                'expired_at': otp_record.expired_at.isoformat()
            }
        }), 401

    db.session.delete(otp_record)

    # Check if application already exists
    existing_app = Application.query.filter_by(
        mobile_id=mobile_entry.id).first()
    if existing_app:
        db.session.commit()
        return jsonify({
            'status': 200,
            'message': 'Mobile number verified successfully.',
            'data': {
                'application_number': existing_app.application_number,
                'created_at': otp_record.created_at.isoformat(),
                'expired_at': otp_record.expired_at.isoformat()
            }
        }), 200

    # Create new application
    app_number = generate_application_number()
    new_application = Application(
        mobile_id=mobile_entry.id,
        application_number=app_number
    )
    db.session.add(new_application)
    db.session.commit()

    return jsonify({
        'status': 200,
        'message': 'Mobile number verified successfully.',
        'data': {
            'application_number': app_number,
            'created_at': otp_record.created_at.isoformat(),
            'expired_at': otp_record.expired_at.isoformat()
        }
    }), 200


@verify_bp.route('/verify-email-otp', methods=['POST'])
def verify_email_otp():
    data = request.get_json()
    email = data.get('email')
    otp_input = data.get('otp')

    if not email or not otp_input:
        return jsonify({'status': 400, 'message': 'Email and OTP are required'}), 400

    email_entry = Email.query.filter_by(email=email).first()
    if not email_entry:
        return jsonify({'status': 404, 'message': 'Email not found'}), 404

    otp_record = EmailOTP.query.filter_by(email_id=email_entry.id).first()
    if not otp_record:
        return jsonify({'status': 404, 'message': 'No OTP found. Please request again.'}), 404

    if datetime.utcnow() > otp_record.expired_at:
        db.session.delete(otp_record)
        db.session.commit()
        return jsonify({'status': 400, 'message': 'OTP expired. Please request again.'}), 400

    if otp_record.otp != str(otp_input):
        return jsonify({'status': 401, 'message': 'Invalid OTP'}), 401

    # Delete OTP
    db.session.delete(otp_record)

    # Check if application already exists
    existing_app = Application.query.filter_by(email_id=email_entry.id).first()
    if existing_app:
        db.session.commit()
        return jsonify({
            'status': 200,
            'message': 'Email verified. Application already exists.',
            'data': {
                'application_number': existing_app.application_number
            }
        }), 200

    # Create new application
    app_number = generate_application_number()
    new_application = Application(
        email_id=email_entry.id, application_number=app_number)
    db.session.add(new_application)
    db.session.commit()

    return jsonify({
        'status': 200,
        'message': 'Email verified and application created.',
        'data': {
            'application_number': app_number
        }
    }), 200


# application-status


@verify_bp.route('/application-status', methods=['GET'])
def application_status():
    mobile = request.args.get('mobile')
    email = request.args.get('email')

    if not mobile and not email:
        return jsonify({'status': 400, 'error': 'Mobile number or email is required'}), 400

    if mobile:
        mobile_entry = Mobile.query.filter_by(mobile=mobile).first()
        if not mobile_entry:
            return jsonify({'status': 404, 'error': 'Mobile number not found'}), 404
        app_record = Application.query.filter_by(
            mobile_id=mobile_entry.id).first()
        contact_info = {'mobile': mobile}
    else:
        email_entry = Email.query.filter_by(email=email).first()
        if not email_entry:
            return jsonify({'status': 404, 'error': 'Email not found'}), 404
        app_record = Application.query.filter_by(
            email_id=email_entry.id).first()
        contact_info = {'email': email}

    if not app_record:
        return jsonify({'status': 404, 'error': 'No application found'}), 404

    return jsonify({
        'status': 200,
        'data': {
            **contact_info,
            'application_number': app_record.application_number,
            'created_at': app_record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'application_status': app_record.status  # update if you add a status column
        }
    }), 200


@verify_bp.route('/change-application-status', methods=['POST'])
def update_application_status():
    data = request.get_json()
    app_number = data.get('application_number')
    new_status = data.get('status')

    if not app_number or not new_status:
        return jsonify({'status': 400, 'message': 'Missing application_number or status'}), 400

    if new_status.lower() not in ['approved', 'rejected', 'pending']:
        return jsonify({'status': 400, 'message': 'Invalid status value'}), 400

    application = Application.query.filter_by(
        application_number=app_number).first()

    if not application:
        return jsonify({'status': 404, 'message': 'Application not found'}), 404

    application.status = new_status.lower()
    db.session.commit()

    return jsonify({
        'status': 200,
        'message': f'Application status updated to {new_status}',
        'data': {
            'application_number': application.application_number,
            'new_status': application.status
        }
    }), 200
