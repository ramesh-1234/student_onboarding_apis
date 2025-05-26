from flask import Blueprint, request, jsonify, render_template, current_app
from app.models import Application, Mobile, AadhaarDetails, AddressUpload, LiveWebcamPhoto, ESignatureUpload

combined_bp = Blueprint('combined', __name__, url_prefix='/combined')


@combined_bp.route('/details', methods=['GET'])
def combined_details():
    application_number = request.args.get('application_number')
    preview = request.args.get('preview', '').lower() == 'true'

    if not application_number:
        return jsonify({'status': 400, 'error': 'Application number is required'}), 400

    application = Application.query.filter_by(
        application_number=application_number).first()
    if not application:
        return jsonify({'status': 404, 'error': 'Application not found'}), 404

    mobile = Mobile.query.get(application.mobile_id)
    aadhaar = AadhaarDetails.query.filter_by(
        application_id=application.id).first()
    address = AddressUpload.query.filter_by(application_id=application.id).order_by(
        AddressUpload.created_at.desc()).first()
    live_photo = LiveWebcamPhoto.query.filter_by(
        application_id=application.id).order_by(LiveWebcamPhoto.created_at.desc()).first()
    esignature = ESignatureUpload.query.filter_by(
        application_id=application.id).order_by(ESignatureUpload.created_at.desc()).first()

    data = {
        'application_number': application.application_number,
        'created_at': application.created_at.isoformat() if application.created_at else None,
        'mobile': mobile.mobile if mobile else None,
        'aadhaar': {
            'name': aadhaar.name if aadhaar else None,
            'dob': aadhaar.dob if aadhaar else None,
            'gender': aadhaar.gender if aadhaar else None,
            'aadhaar_number': aadhaar.aadhaar_number if aadhaar else None,
            'address': aadhaar.address if aadhaar else None,
            'pincode': aadhaar.pincode if aadhaar else None,
            'city': aadhaar.city if aadhaar else None,
            'state': aadhaar.state if aadhaar else None,
            'country': aadhaar.country if aadhaar else None,
            'aadhaar_image_path': aadhaar.aadhaar_image_path if aadhaar else None,
            'created_at': aadhaar.created_at.isoformat() if aadhaar and aadhaar.created_at else None,
            'modified_at': aadhaar.modified_at.isoformat() if aadhaar and aadhaar.modified_at else None,
        } if aadhaar else None,
        'address': {
            'address_line': address.address_line,
            'city': address.city,
            'state': address.state,
            'pincode': address.pincode,
            'created_at': address.created_at.isoformat() if address else None,
            'modified_at': address.modified_at.isoformat() if address else None,
        } if address else None,
        'live_photo': {
            'image_path': live_photo.image_path,
            'created_at': live_photo.created_at.isoformat() if live_photo else None,
        } if live_photo else None,
        'esignature': {
            'image_path': esignature.image_path,
            'created_at': esignature.created_at.isoformat() if esignature else None,
            'modified_at': esignature.modified_at.isoformat() if esignature else None,
        } if esignature else None
    }

    if preview:
        # Render preview template with all data
        return render_template('application_preview.html', data=data)

    return jsonify({'status': 200, 'data': data})
