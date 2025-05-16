from datetime import datetime
from app.extensions import db


class Mobile(db.Model):
    __tablename__ = 'mobile'
    id = db.Column(db.Integer, primary_key=True)
    mobile = db.Column(db.String(15), unique=True, nullable=False)

    # Relationship (optional but helpful)
    otps = db.relationship('MobileOTP', backref='mobile', lazy=True)
    applications = db.relationship('Application', backref='mobile', lazy=True)
    created_at = db.Column(db.DateTime, default=db.func.now())


class MobileOTP(db.Model):
    __tablename__ = 'mobile_otp'
    id = db.Column(db.Integer, primary_key=True)
    mobile_id = db.Column(db.Integer, db.ForeignKey(
        'mobile.id'), nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expired_at = db.Column(db.DateTime)


class Application(db.Model):
    __tablename__ = 'application'
    id = db.Column(db.Integer, primary_key=True)
    mobile_id = db.Column(db.Integer, db.ForeignKey(
        'mobile.id'), nullable=False)
    application_number = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AccountPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mobile_id = db.Column(db.Integer, db.ForeignKey(
        'mobile.id'), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey(
        'application.id'), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)
    profession = db.Column(db.String(100), nullable=False)
    enable_online_banking = db.Column(db.Boolean, default=False)
    request_debit_card = db.Column(db.Boolean, default=False)
    card_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    mobile = db.relationship('Mobile', backref='account_preferences')
    application = db.relationship('Application', backref='preferences')


class AadhaarDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mobile_id = db.Column(db.Integer, db.ForeignKey(
        'mobile.id'), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey(
        'application.id'), nullable=False)
    name = db.Column(db.String(120))
    dob = db.Column(db.String(20))
    gender = db.Column(db.String(20))
    address = db.Column(db.String(250))
    pincode = db.Column(db.String(10))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50))
    aadhaar_number = db.Column(db.String(12), unique=True, nullable=False)
    aadhaar_image_path = db.Column(db.String(255))  # Only this remains
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    mobile = db.relationship('Mobile', backref='aadhaar_details')
    application = db.relationship('Application', backref='aadhaar_details')


class LiveWebcamPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mobile_id = db.Column(db.Integer, db.ForeignKey(
        'mobile.id'), nullable=False)
    aadhaar_id = db.Column(db.Integer, db.ForeignKey(
        'aadhaar_details.id'), nullable=False)
    application_id = db.Column(
        db.Integer, db.ForeignKey('application.id'), nullable=True)
    image_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    mobile = db.relationship('Mobile', backref='live_photos')
    aadhaar = db.relationship('AadhaarDetails', backref='live_photos')
    application = db.relationship('Application', backref='live_photos')

# app/models/address_upload.py (or in models/__init__.py if you're centralizing)


class AddressUpload(db.Model):
    __tablename__ = 'address_upload'
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey(
        'application.id'), nullable=False)
    address_line = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    application = db.relationship('Application', backref='address_uploads')


class ESignatureUpload(db.Model):
    __tablename__ = 'esignature_upload'

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey(
        'application.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow)

    application = db.relationship('Application', backref='esignature_uploads')
