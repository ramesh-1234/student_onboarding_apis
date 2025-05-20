from flask import Blueprint, render_template, request, redirect, url_for, session
import requests

frontend_bp = Blueprint('frontend', __name__)


@frontend_bp.route('/verify-mobile', methods=['GET', 'POST'])
def verify_mobile_page():
    if request.method == 'POST':
        mobile = request.form['mobile']
        try:
            response = requests.post(
                'http://localhost:8000/verify-mobile', json={'mobile': mobile})
            result = response.json()
            if response.status_code == 200:
                otp = result['data']['otp']
                # Store in session instead of query param (more secure)
                session['otp'] = otp
                session['mobile'] = mobile
                return redirect(url_for('frontend.verify_otp_page'))
            else:
                return render_template('verify_mobile.html', error=result.get('message'))
        except Exception as e:
            return render_template('verify_mobile.html', error=str(e))
    return render_template('verify_mobile.html')


@frontend_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp_page():
    mobile = session.get('mobile')
    otp = session.get('otp', '')
    if request.method == 'POST':
        submitted_otp = request.form['otp']
        try:
            response = requests.post(
                'http://localhost:8000/verify-otp', json={'mobile': mobile, 'otp': submitted_otp})
            result = response.json()
            if response.status_code == 200:
                # OTP verified successfully
                application_number = result.get(
                    'data', {}).get('application_number', '')
                # Redirect to account preferences with mobile and application_number in query params
                return redirect(url_for('frontend.account_preferences_page', mobile=mobile, application_number=application_number))
            else:
                error = result.get('message')
                return render_template('verify_otp.html', otp=submitted_otp, mobile=mobile, error=error)
        except Exception as e:
            return render_template('verify_otp.html', otp=submitted_otp, mobile=mobile, error=str(e))
    return render_template('verify_otp.html', otp=otp, mobile=mobile)


# @frontend_bp.route('/account-preferences', methods=['GET', 'POST'])
# def account_preferences_page():
#     mobile = session.get('mobile')
#     if not mobile:
#         # If no mobile in session, redirect back to verify mobile page
#         return redirect(url_for('frontend.verify_mobile_page'))

#     if request.method == 'POST':
#         data = {
#             'mobile': mobile,
#             'account_type': request.form.get('account_type'),
#             'profession': request.form.get('profession'),
#             'enable_online_banking': request.form.get('enable_online_banking') == 'on',
#             'request_debit_card': request.form.get('request_debit_card') == 'on',
#             'card_type': request.form.get('card_type')
#         }

#         try:
#             response = requests.post(
#                 'http://localhost:8000/account-preferences', json=data)
#             result = response.json()
#             if response.status_code == 200:
#                 return f"✅ Account preferences saved successfully for mobile {mobile}!"
#             else:
#                 error = result.get('error') or result.get(
#                     'message') or 'Error saving preferences'
#                 return render_template('account_preferences.html', mobile=mobile, error=error, data=data)
#         except Exception as e:
#             return render_template('account_preferences.html', mobile=mobile, error=str(e), data=data)

#     # GET request
#     return render_template('account_preferences.html', mobile=mobile)
