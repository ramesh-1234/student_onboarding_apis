from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
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


@account_bp.route('/account-preferences', methods=['GET'])
def get_preferences():
    mobile = request.args.get('mobile')
    if not mobile:
        return jsonify({'status': 400, 'error': 'Mobile is required'}), 400

    mobile_entry = Mobile.query.filter_by(mobile=mobile).first()
    if not mobile_entry:
        return jsonify({'status': 404, 'error': 'Mobile not found'}), 404

    preferences = AccountPreferences.query.filter_by(
        mobile_id=mobile_entry.id).first()
    if not preferences:
        return jsonify({'status': 404, 'error': 'Preferences not found'}), 404

    return jsonify({
        'status': 200,
        'message': 'Account preferences fetched successfully',
        'data': {
            'application_number': preferences.application.application_number,
            'application_id': preferences.application_id,
            'account_type': preferences.account_type,
            'profession': preferences.profession,
            'enable_online_banking': preferences.enable_online_banking,
            'request_debit_card': preferences.request_debit_card,
            'card_type': preferences.card_type,
            'created_at': preferences.created_at.isoformat() if preferences.created_at else None,
            'modified_at': preferences.modified_at.isoformat() if preferences.modified_at else None
        }
    })


@account_bp.route('/account-preferences', methods=['PUT'])
def update_preferences():
    data = request.get_json()
    mobile = data.get('mobile')
    if not mobile:
        return jsonify({'status': 400, 'error': 'Mobile is required'}), 400

    mobile_entry = Mobile.query.filter_by(mobile=mobile).first()
    if not mobile_entry:
        return jsonify({'status': 404, 'error': 'Mobile not found'}), 404

    preferences = AccountPreferences.query.filter_by(
        mobile_id=mobile_entry.id).first()
    if not preferences:
        return jsonify({'status': 404, 'error': 'Preferences not found'}), 404

    preferences.account_type = data.get(
        'account_type', preferences.account_type)
    preferences.profession = data.get('profession', preferences.profession)
    preferences.enable_online_banking = data.get(
        'enable_online_banking', preferences.enable_online_banking)
    preferences.request_debit_card = data.get(
        'request_debit_card', preferences.request_debit_card)
    preferences.card_type = data.get('card_type', preferences.card_type)
    preferences.modified_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        'status': 200,
        'message': 'Preferences updated successfully',
        'data': {
            'application_number': preferences.application.application_number,
            'created_at': preferences.created_at.isoformat() if preferences.created_at else None,
            'modified_at': preferences.modified_at.isoformat() if preferences.modified_at else None
        }
    })


@account_bp.route('/account-preferences', methods=['DELETE'])
def delete_preferences():
    mobile = request.args.get('mobile')
    if not mobile:
        return jsonify({'status': 400, 'error': 'Mobile is required'}), 400

    mobile_entry = Mobile.query.filter_by(mobile=mobile).first()
    if not mobile_entry:
        return jsonify({'status': 404, 'error': 'Mobile not found'}), 404

    preferences = AccountPreferences.query.filter_by(
        mobile_id=mobile_entry.id).first()
    if not preferences:
        return jsonify({'status': 404, 'error': 'Preferences not found'}), 404

    db.session.delete(preferences)
    db.session.commit()

    return jsonify({
        'status': 200,
        'message': 'Account preferences deleted successfully',
        'data': {
            'id': preferences.id
        }
    })


@account_bp.route('/account-preferences-form', methods=['GET'])
def show_account_preferences_form():
    mobile = request.args.get('mobile')
    application_number = request.args.get('application_number')

    if not mobile:
        return "Mobile number is required", 400

    return render_template(
        'account_preferences.html',
        mobile=mobile,
        application_number=application_number
    )
