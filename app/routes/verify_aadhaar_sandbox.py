import requests
from flask import Blueprint, json, render_template, request, jsonify, current_app
from app.models import AadhaarDetails, AadhaarOTP, AadhaarOTPSandboxDetails, AadhaarSandboxDetails
from app.extensions import db

aadhaar_bp = Blueprint('aadhaar_sandbox', __name__)

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

        # Ensure Aadhaar record exists
        aadhaar_entry = AadhaarSandboxDetails.query.filter_by(
            aadhaar_number=aadhaar_number).first()

        if not aadhaar_entry:
            aadhaar_entry = AadhaarSandboxDetails(
                aadhaar_number=aadhaar_number
            )
            db.session.add(aadhaar_entry)
            db.session.commit()

        # Store OTP request status
        otp_entry = AadhaarOTPSandboxDetails(
            aadhaar_id=aadhaar_entry.id,
            txn_id=txn_id,
            client_id=client_id,
            otp_sent=True,
            raw_response=json.dumps(res)
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
    reference_id = data.get('reference_id')
    otp = data.get('otp')
    entity = data.get('entity', 'in.co.sandbox.kyc.aadhaar.okyc.request')

    if not reference_id or not otp:
        return jsonify({'status': 400, 'message': 'reference_id and otp are required'}), 400

    headers = {
        'Content-Type': 'application/json',
        'authorization': current_app.config['SANDBOX_JWT_TOKEN'],
        'x-api-key': current_app.config['SANDBOX_API_KEY'],
        'x-api-version': '2.0'
    }

    body = {
        "entity": entity,
        "reference_id": reference_id,
        "otp": otp
    }

    try:
        response = requests.post(
            f"{current_app.config['SANDBOX_BASE_URL']}/kyc/aadhaar/okyc/otp/verify",
            headers=headers,
            json=body
        )
        res = response.json()

        # if res.get("success"):
        if res.get("code") == 200:
            aadhaar_data = res.get("data", {})

            # Store in aadhaar_sandbox_details table
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

            # Optionally update AadhaarOTP if applicable
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
