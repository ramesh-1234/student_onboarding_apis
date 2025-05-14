from datetime import datetime
from flask import Blueprint, request, jsonify
from app.models import AccountPreferences, Application, Mobile
from app.extensions import db

account_bp = Blueprint('account_preferences', __name__)

ALLOWED_ACCOUNT_TYPES = {'savingsAccount', 'currentAccount',
                         'jointAccount', 'salaryAccount', 'fixedDeposit'}
ALLOWED_PROFESSIONS = {'Student', 'Employee', 'Manager',
                       'BusinessOwner', 'Professional', 'Retired', 'Other'}
ALLOWED_CARD_TYPES = {'Classic', 'Gold', 'Platinum'}


@account_bp.route('/account-preferences', methods=['POST'])
def save_account_preferences():
    data = request.get_json()
    mobile = data.get('mobile')
    account_type = data.get('account_type')
    profession = data.get('profession')
    enable_online_banking = data.get('enable_online_banking', False)
    request_debit_card = data.get('request_debit_card', False)
    card_type = data.get('card_type')

    if not mobile:
        return jsonify({'status': 400, 'message': 'Mobile number is required'}), 400

    if account_type not in ALLOWED_ACCOUNT_TYPES:
        return jsonify({'status': 400, 'message': 'Invalid account type'}), 400

    if profession not in ALLOWED_PROFESSIONS:
        return jsonify({'status': 400, 'message': 'Invalid profession'}), 400

    if card_type and card_type not in ALLOWED_CARD_TYPES:
        return jsonify({'status': 400, 'message': 'Invalid card type'}), 400

    # Get mobile and application
    mobile_entry = Mobile.query.filter_by(mobile=mobile).first()
    if not mobile_entry:
        return jsonify({'status': 404, 'message': 'Mobile number not found'}), 404

    application = Application.query.filter_by(
        mobile_id=mobile_entry.id).first()
    if not application:
        return jsonify({'status': 404, 'message': 'No application found for this mobile'}), 404

    # Check if preferences already exist, then update
    preferences = AccountPreferences.query.filter_by(
        mobile_id=mobile_entry.id).first()
    if preferences:
        preferences.account_type = account_type
        preferences.profession = profession
        preferences.enable_online_banking = enable_online_banking
        preferences.request_debit_card = request_debit_card
        preferences.card_type = card_type
        preferences.application_id = application.id
        preferences.created_at = datetime.utcnow()
    else:
        preferences = AccountPreferences(
            mobile_id=mobile_entry.id,
            application_id=application.id,
            account_type=account_type,
            profession=profession,
            enable_online_banking=enable_online_banking,
            request_debit_card=request_debit_card,
            card_type=card_type
        )
        db.session.add(preferences)

    db.session.commit()

    return jsonify({
        'status': 200,
        'message': 'Account preferences saved successfully',
        'data': {
            'application_number': application.application_number,
            'created_at': preferences.created_at.isoformat()
        }
    }), 200
