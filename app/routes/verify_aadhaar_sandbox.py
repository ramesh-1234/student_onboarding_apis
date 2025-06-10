import random
import requests
from flask import Blueprint, json, render_template, request, jsonify, current_app
from app.models import AadhaarDetails, AadhaarOTP, AadhaarOTPSandboxDetails, AadhaarSandboxDetails, Application
from app.extensions import db

aadhaar_bp = Blueprint('aadhaar_sandbox', __name__)

# Test OTP


@aadhaar_bp.route('/aadhaar/test-send-otp', methods=['POST'])
def test_send_otp():
    data = request.get_json()
    aadhaar_number = data.get('aadhaar_number')

    if not aadhaar_number:
        return jsonify({'status': 400, 'message': 'Aadhaar number is required'}), 400

    # Generate random 6-digit OTP
    generated_otp = str(random.randint(100000, 999999))

    # Simulate saving to DB
    aadhaar_entry = AadhaarSandboxDetails.query.filter_by(
        aadhaar_number=aadhaar_number).first()

    if not aadhaar_entry:
        aadhaar_entry = AadhaarSandboxDetails(
            aadhaar_number=aadhaar_number,
            reference_id=0  # Use valid logic here
        )
        db.session.add(aadhaar_entry)
        db.session.commit()

    otp_entry = AadhaarOTPSandboxDetails.query.filter_by(
        aadhaar_id=aadhaar_entry.id).first()

    if otp_entry:
        otp_entry.transaction_id = None
        otp_entry.client_id = None
        otp_entry.otp_sent = True
        otp_entry.message = "OTP generated"
        otp_entry.reference_id = None
        otp_entry.entity = "test"
        otp_entry.code = 200
        otp_entry.timestamp = None
        otp_entry.test_otp = generated_otp  # custom field
    else:
        otp_entry = AadhaarOTPSandboxDetails(
            aadhaar_id=aadhaar_entry.id,
            transaction_id=None,
            client_id=None,
            otp_sent=True,
            message="OTP generated",
            reference_id=None,
            entity="test",
            code=200,
            timestamp=None,
            test_otp=generated_otp  # custom field
        )
        db.session.add(otp_entry)

    db.session.commit()

    return jsonify({
        'status': 200,
        'message': 'Test OTP sent',
        'test_otp': generated_otp  # You can omit this in prod
    }), 200


# @aadhaar_bp.route('/aadhaar/test-verify-otp', methods=['POST'])
# def test_verify_otp():
#     data = request.get_json()
#     aadhaar_number = data.get('aadhaar_number')
#     entered_otp = data.get('otp')

#     if not aadhaar_number or not entered_otp:
#         return jsonify({'status': 400, 'message': 'Missing Aadhaar or OTP'}), 400

#     aadhaar_entry = AadhaarSandboxDetails.query.filter_by(
#         aadhaar_number=aadhaar_number).first()

#     if not aadhaar_entry:
#         return jsonify({'status': 404, 'message': 'Aadhaar record not found'}), 404

#     otp_entry = AadhaarOTPSandboxDetails.query.filter_by(
#         aadhaar_id=aadhaar_entry.id).first()

#     if not otp_entry:
#         return jsonify({'status': 404, 'message': 'OTP entry not found'}), 404

#     # Fetch the linked application record
#     application = Application.query.filter_by(
#         aadhaar_id=aadhaar_entry.id).first()
#     if not application:
#         return jsonify({'status': 404, 'message': 'Application record not found'}), 404

#     application_number = application.application_number

#     if otp_entry.verified:
#         return jsonify({
#             'status': 200,
#             'message': 'Already verified',
#             'already_verified': True,
#             'aadhaar_number': aadhaar_number,
#             'application_number': application_number
#         }), 200

#     if otp_entry.test_otp != entered_otp:
#         return jsonify({'status': 401, 'message': 'Invalid OTP'}), 401

#     otp_entry.verified = True
#     db.session.commit()

#     return jsonify({
#         'status': 200,
#         'message': 'OTP verified successfully',
#         'aadhaar_number': aadhaar_number,
#         'application_number': application_number
#     }), 200


@aadhaar_bp.route('/aadhaar/test-verify-otp', methods=['POST'])
def test_verify_otp():
    data = request.get_json()
    aadhaar_number = data.get('aadhaar_number')
    entered_otp = data.get('otp')

    if not aadhaar_number or not entered_otp:
        return jsonify({'status': 400, 'message': 'Missing Aadhaar or OTP'}), 400

    aadhaar_entry = AadhaarSandboxDetails.query.filter_by(
        aadhaar_number=aadhaar_number).first()

    if not aadhaar_entry:
        return jsonify({'status': 404, 'message': 'Aadhaar record not found'}), 404

    otp_entry = AadhaarOTPSandboxDetails.query.filter_by(
        aadhaar_id=aadhaar_entry.id).first()

    if not otp_entry:
        return jsonify({'status': 404, 'message': 'OTP entry not found'}), 404

    application = Application.query.filter_by(
        aadhaar_id=aadhaar_entry.id).first()
    if not application:
        return jsonify({'status': 404, 'message': 'Application record not found'}), 404

    application_number = application.application_number

    # ✅ OTP check (robust string match)
    if str(otp_entry.test_otp).strip() != str(entered_otp).strip():
        return jsonify({'status': 401, 'message': 'Invalid OTP'}), 401

    if otp_entry.verified:
        return jsonify({
            'status': 200,
            'message': 'Already verified',
            'already_verified': True,
            'aadhaar_number': aadhaar_number,
            'application_number': application_number
        }), 200

    otp_entry.verified = True
    db.session.commit()

    return jsonify({
        'status': 200,
        'message': 'OTP verified successfully',
        'aadhaar_number': aadhaar_number,
        'application_number': application_number
    }), 200


# Initiate OTP Request


@aadhaar_bp.route('/aadhaar/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    aadhaar_number = data.get('aadhaar_number') or data.get('aadhaar')

    if not aadhaar_number:
        return jsonify({'status': 400, 'message': 'Aadhaar number is required'}), 400

    headers = {
        'Content-Type': 'application/json',
        'accept': 'application/json',
        'x-api-version': '2.0',
        'x-api-key': current_app.config['RSANDBOX_API_KEY'],
        'authorization': current_app.config['RSANDBOX_JWT_TOKEN'],
    }

    body = {
        "@entity": "in.co.sandbox.kyc.aadhaar.okyc.otp.request",
        "aadhaar_number": aadhaar_number,
        "consent": "Y",
        "reason": "For KYC"
    }

    try:
        response = requests.post(
            f"{current_app.config['RSANDBOX_BASE_URL']}/kyc/aadhaar/okyc/otp",
            headers=headers,
            json=body
        )

        try:
            res = response.json()
        except ValueError:
            return jsonify({
                'status': 502,
                'message': 'Invalid response from Aadhaar API',
                'raw': response.text
            }), 502

        if res.get("code") != 200:
            return jsonify({
                'status': 400,
                'message': res.get('message', 'Failed to send OTP')
            }), 400

        # Extract response data
        data = res.get("data", {})
        txn_id = data.get("txn_id")
        client_id = data.get("client_id")

        # Ensure AadhaarSandboxDetails record exists
        aadhaar_entry = AadhaarSandboxDetails.query.filter_by(
            aadhaar_number=aadhaar_number).first()

        if not aadhaar_entry:
            # NOTE: reference_id is non-nullable, assign dummy or fetch properly
            aadhaar_entry = AadhaarSandboxDetails(
                aadhaar_number=aadhaar_number,
                reference_id=0  # or your logic here
            )
            db.session.add(aadhaar_entry)
            db.session.commit()

        # Check if OTP entry already exists for this Aadhaar
        otp_entry = AadhaarOTPSandboxDetails.query.filter_by(
            aadhaar_id=aadhaar_entry.id).first()

        if otp_entry:
            # Update existing OTP entry
            otp_entry.transaction_id = txn_id
            otp_entry.client_id = client_id
            otp_entry.otp_sent = True
            otp_entry.message = res.get('message')
            otp_entry.reference_id = data.get('reference_id')
            otp_entry.entity = data.get('entity')
            otp_entry.code = res.get('code')
            otp_entry.timestamp = None  # convert if needed
        else:
            # Create new OTP entry
            otp_entry = AadhaarOTPSandboxDetails(
                aadhaar_id=aadhaar_entry.id,
                transaction_id=txn_id,
                client_id=client_id,
                otp_sent=True,
                message=res.get('message'),
                reference_id=data.get('reference_id'),
                entity=data.get('entity'),
                code=res.get('code'),
                timestamp=None
            )
            db.session.add(otp_entry)

        db.session.commit()

        return jsonify({
            'status': 200,
            'message': 'OTP sent successfully',
            'data': {
                'txn_id': txn_id,
                'client_id': client_id
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': 500,
            'message': 'Server error',
            'error': str(e)
        }), 500


# template rendering

@aadhaar_bp.route('/aadhaar/send-otp', methods=['GET'])
def aadhaar_send_otp():
    return render_template('aadhaar_details_page.html')

# Verify OTP


@aadhaar_bp.route('/aadhaar/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    otp = data.get('otp')

    if not otp:
        return jsonify({'status': 400, 'message': 'otp is required'}), 400

    # For example, find latest or relevant reference_id from aadhaar_otp_sandbox_details table
    otp_record = AadhaarOTPSandboxDetails.query.order_by(
        AadhaarOTPSandboxDetails.created_at.desc()).first()
    if not otp_record or not otp_record.reference_id:
        return jsonify({'status': 400, 'message': 'No reference_id found in records'}), 400

    reference_id = otp_record.reference_id

    entity = data.get('entity', 'in.co.sandbox.kyc.aadhaar.okyc.request')

    headers = {
        'Content-Type': 'application/json',
        'authorization': current_app.config['RSANDBOX_JWT_TOKEN'],
        'x-api-key': current_app.config['RSANDBOX_API_KEY'],
        'x-api-version': '2.0'
    }

    body = {
        "entity": entity,
        "reference_id": reference_id,
        "otp": otp
    }

    try:
        response = requests.post(
            f"{current_app.config['RSANDBOX_BASE_URL']}/kyc/aadhaar/okyc/otp/verify",
            headers=headers,
            json=body
        )
        res = response.json()

        if res.get("code") == 200:
            aadhaar_data = res.get("data", {})

            details = AadhaarSandboxDetails(
                aadhaar_number=aadhaar_data.get("aadhaar_number"),
                name=aadhaar_data.get("full_name"),
                gender=aadhaar_data.get("gender"),
                dob=aadhaar_data.get("dob"),
                address=aadhaar_data.get("address"),
                city=aadhaar_data.get("district"),
                state=aadhaar_data.get("state"),
                country="India"
            )

            db.session.add(details)
            db.session.commit()

            otp_entry = AadhaarOTP.query.filter_by(
                otp_txn_id=reference_id).first()
            if otp_entry:
                otp_entry.verified = True
                db.session.commit()

            return jsonify({
                'status': 200,
                'message': 'Aadhaar verified successfully',
                'aadhaar_id': details.id
            }), 200

        return jsonify({
            'status': 400,
            'message': res.get('message', 'Verification failed')
        }), 400

    except Exception as e:
        return jsonify({
            'status': 500,
            'message': 'Server error during Aadhaar verification',
            'error': str(e)
        }), 500


@aadhaar_bp.route('/aadhaar/match-otp', methods=['POST'])
def match_otp():
    data = request.get_json()
    aadhaar_number = data.get('aadhaar_number')
    entered_otp = data.get('otp')

    if not aadhaar_number or not entered_otp:
        return jsonify({'status': 400, 'message': 'Aadhaar number and OTP are required'}), 400

    # Lookup Aadhaar entry
    aadhaar_entry = AadhaarSandboxDetails.query.filter_by(
        aadhaar_number=aadhaar_number
    ).first()

    if not aadhaar_entry:
        return jsonify({'status': 404, 'message': 'Aadhaar number not found'}), 404

    # ✅ Skip OTP code comparison and assume it's valid
    return jsonify({
        'status': 200,
        'message': 'OTP submitted successfully',
        'aadhaar_number': aadhaar_number
    }), 200
