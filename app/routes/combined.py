from flask import Blueprint, request, jsonify, render_template, current_app
from sqlalchemy import or_
from app.models import AccountPreferences, Application, Mobile, AadhaarDetails, AddressUpload, LiveWebcamPhoto, ESignatureUpload

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
        'application_status': application.status,
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


@combined_bp.route('/all_details', methods=['GET'])
def all_application_details():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status_filter = request.args.get('status')
    search_term = request.args.get('search', '').strip().lower()

    query = Application.query

    # Apply status filter
    if status_filter in ['pending', 'approved', 'rejected']:
        query = query.filter(Application.status == status_filter)

    # Apply search filter
    if search_term:
        query = query.join(Mobile, Mobile.id ==
                           Application.mobile_id, isouter=True)
        query = query.join(
            AadhaarDetails, AadhaarDetails.application_id == Application.id, isouter=True)
        query = query.filter(
            or_(
                Application.application_number.ilike(f"%{search_term}%"),
                AadhaarDetails.name.ilike(f"%{search_term}%"),
                Mobile.mobile.ilike(f"%{search_term}%")
            )
        )

    applications = query.paginate(
        page=page, per_page=per_page, error_out=False)
    data = []

    for application in applications.items:
        mobile = Mobile.query.get(application.mobile_id)
        aadhaar = AadhaarDetails.query.filter_by(
            application_id=application.id).first()
        address = AddressUpload.query.filter_by(application_id=application.id).order_by(
            AddressUpload.created_at.desc()).first()
        live_photo = LiveWebcamPhoto.query.filter_by(
            application_id=application.id).order_by(LiveWebcamPhoto.created_at.desc()).first()
        esignature = ESignatureUpload.query.filter_by(
            application_id=application.id).order_by(ESignatureUpload.created_at.desc()).first()
        preferences = AccountPreferences.query.filter_by(
            application_id=application.id).first()

        application_data = {
            'application_number': application.application_number,
            'application_status': application.status,
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
                'address_line': address.address_line if address else None,
                'city': address.city if address else None,
                'state': address.state if address else None,
                'pincode': address.pincode if address else None,
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
            } if esignature else None,

            'account_preferences': {
                'account_type': preferences.account_type,
                'profession': preferences.profession,
                'enable_online_banking': preferences.enable_online_banking,
                'request_debit_card': preferences.request_debit_card,
                'card_type': preferences.card_type,
                'created_at': preferences.created_at.isoformat() if preferences else None,
                'modified_at': preferences.modified_at.isoformat() if preferences else None
            } if preferences else None
        }

        data.append(application_data)

    return jsonify({
        'status': 200,
        'page': page,
        'per_page': per_page,
        'total_pages': applications.pages,
        'total_records': applications.total,
        'data': data
    })
