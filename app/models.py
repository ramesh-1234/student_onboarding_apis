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

    mobile = db.relationship('Mobile', backref='account_preferences')
    application = db.relationship('Application', backref='preferences')


class AadhaarDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mobile_id = db.Column(db.Integer, db.ForeignKey('mobile.id'), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    name = db.Column(db.String(120))
    dob = db.Column(db.String(20))
    gender = db.Column(db.String(20))
    aadhaar_number = db.Column(db.String(12), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    mobile = db.relationship('Mobile', backref='aadhaar_details')
    application = db.relationship('Application', backref='aadhaar_details')

