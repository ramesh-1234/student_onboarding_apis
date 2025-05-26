from flask import Blueprint, render_template, request, redirect, url_for, session
import requests

frontend_bp = Blueprint('frontend', __name__)


# @frontend_bp.route('/verify-mobile', methods=['GET', 'POST'])
# def verify_mobile_page():
#     if request.method == 'POST':
#         mobile = request.form['mobile']
#         try:
#             response = requests.post(
#                 'http://localhost:8000/verify-mobile', json={'mobile': mobile})
#             result = response.json()
#             if response.status_code == 200:
#                 otp = result['data']['otp']
#                 # Store in session instead of query param (more secure)
#                 session['otp'] = otp
#                 session['mobile'] = mobile
#                 return redirect(url_for('frontend.verify_otp_page'))
#             else:
#                 return render_template('verify_mobile.html', error=result.get('message'))
#         except Exception as e:
#             return render_template('verify_mobile.html', error=str(e))
#     return render_template('verify_mobile.html')

@frontend_bp.route('/verify-mobile', methods=['GET', 'POST'])
def verify_mobile_page():
    return render_template('verify_mobile.html')


# @frontend_bp.route('/verify-otp', methods=['GET', 'POST'])
# def verify_otp_page():
#     mobile = session.get('mobile')
#     otp = session.get('otp', '')
#     if request.method == 'POST':
#         submitted_otp = request.form['otp']
#         try:
#             response = requests.post(
#                 'http://localhost:8000/verify-otp', json={'mobile': mobile, 'otp': submitted_otp})
#             result = response.json()
#             if response.status_code == 200:
#                 # OTP verified successfully
#                 application_number = result.get(
#                     'data', {}).get('application_number', '')
#                 # Redirect to account preferences with mobile and application_number in query params
#                 return redirect(url_for('frontend.account_preferences_page', mobile=mobile, application_number=application_number))
#             else:
#                 error = result.get('message')
#                 return render_template('verify_otp.html', otp=submitted_otp, mobile=mobile, error=error)
#         except Exception as e:
#             return render_template('verify_otp.html', otp=submitted_otp, mobile=mobile, error=str(e))
#     return render_template('verify_otp.html', otp=otp, mobile=mobile)
