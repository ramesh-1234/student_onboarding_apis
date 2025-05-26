import io
from flask import Blueprint, render_template, request, redirect, send_file, url_for, session
import pdfkit
import requests


frontend_bp = Blueprint('frontend', __name__)


@frontend_bp.route('/verify-mobile', methods=['GET', 'POST'])
def verify_mobile_page():
    return render_template('verify_mobile.html')


# @frontend_bp.route('/download-pdf', methods=['GET'])
# def template_form_page():
#     return render_template('filled_template_form.html')


@frontend_bp.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    data = {
        "full_name": request.form.get("full_name"),
        "dob": request.form.get("dob"),
        "gender": request.form.get("gender"),
        "mobile": request.form.get("mobile"),
        "address": request.form.get("address")
    }

    rendered = render_template("filled_template_form.html", data=data)

    # Add configuration with the absolute path to wkhtmltopdf
    config = pdfkit.configuration(
        wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    )
    pdf = pdfkit.from_string(rendered, False, configuration=config)

    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='sbi_account_form.pdf'
    )
