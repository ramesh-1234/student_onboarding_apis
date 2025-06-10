import io
import os
from flask import Blueprint, render_template, request, redirect, send_file, url_for, session
import pdfkit
import requests


frontend_bp = Blueprint('frontend', __name__)


@frontend_bp.route('/verify-mobile', methods=['GET', 'POST'])
def verify_mobile_page():
    return render_template('verify_mobile.html')


# @frontend_bp.route('/download-pdf', methods=['GET'])
# def template_form_page():
#     data = {
#         "full_name": request.args.get("full_name"),
#         "dob": request.args.get("dob"),
#         "gender": request.args.get("gender"),
#         "mobile": request.args.get("mobile"),
#         "address": request.args.get("address")
#     }

#     return render_template('sbi_single_form.html', data=data)


@frontend_bp.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    # Base uploads directory — adjust if needed
    uploads_dir = os.path.join(os.getcwd(), 'uploads')

    # Get image paths from form
    esignature_rel = request.form.get("esignature_path")
    live_photo_rel = request.form.get("live_photo_path")

    # Construct absolute file paths (must use file:/// and forward slashes for wkhtmltopdf)
    esignature_abs = os.path.join(
        uploads_dir, esignature_rel.strip('/')) if esignature_rel else None
    live_photo_abs = os.path.join(
        uploads_dir, live_photo_rel.strip('/')) if live_photo_rel else None

    def to_file_url(path):
        return f"file:///{path.replace(os.sep, '/')}" if path else None

    # Data dictionary passed to the template
    data = {
        "full_name": request.form.get("full_name"),
        "dob": request.form.get("dob"),
        "gender": request.form.get("gender"),
        "mobile": request.form.get("mobile"),
        "address": request.form.get("address"),
        "esignature_path": to_file_url(esignature_abs),
        "live_photo_path": to_file_url(live_photo_abs),
    }

    # Render HTML template with data
    rendered = render_template("sbi_single_form.html", data=data)

    # PDF configuration
    config = pdfkit.configuration(
        wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    )

    # Generate PDF from HTML string
    pdf = pdfkit.from_string(rendered, False, configuration=config)

    # Send the PDF as downloadable file
    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='sbi_account_form.pdf'
    )
