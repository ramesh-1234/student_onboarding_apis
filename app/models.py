from datetime import datetime
from app.extensions import db


class BankName(db.Model):
    __tablename__ = 'bank_names'

    bank_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bank_name = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    branches = db.relationship(
        'Branch', backref='bank', lazy=True, cascade='all, delete-orphan')


class Branch(db.Model):
    __tablename__ = 'branches'

    branch_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    branch_name = db.Column(db.String(100), nullable=False)
    bank_id = db.Column(db.Integer, db.ForeignKey(
        'bank_names.bank_id'), nullable=False)
    ifsc_code = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    status = db.Column(
        db.Enum('open', 'closed', name='branch_status'), nullable=False, default='open')
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


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


class Email(db.Model):
    __tablename__ = 'email'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)

    # Relationships
    otps = db.relationship('EmailOTP', backref='email', lazy=True)
    created_at = db.Column(db.DateTime, default=db.func.now())


class EmailOTP(db.Model):
    __tablename__ = 'email_otp'
    id = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.Integer, db.ForeignKey('email.id'), nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expired_at = db.Column(db.DateTime)


class Application(db.Model):
    __tablename__ = 'application'

    id = db.Column(db.Integer, primary_key=True)
    mobile_id = db.Column(
        db.Integer, db.ForeignKey('mobile.id'), nullable=True)
    email_id = db.Column(db.Integer, db.ForeignKey('email.id'), nullable=True)

    aadhaar_id = db.Column(
        db.Integer, db.ForeignKey('aadhaar_sandbox_details.id'), nullable=True
    )
    application_number = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    status = db.Column(db.String(50), default='pending')

    email = db.relationship('Email', backref='applications', lazy=True)

    aadhaar = db.relationship(
        'AadhaarSandboxDetails', back_populates='applications', lazy=True
    )


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


# class AadhaarDetails(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     mobile_id = db.Column(db.Integer, db.ForeignKey(
#         'mobile.id'), nullable=False)
#     application_id = db.Column(db.Integer, db.ForeignKey(
#         'application.id'), nullable=False)
#     name = db.Column(db.String(120))
#     dob = db.Column(db.String(20))
#     gender = db.Column(db.String(20))
#     address = db.Column(db.String(250))
#     pincode = db.Column(db.String(10))
#     city = db.Column(db.String(50))
#     state = db.Column(db.String(50))
#     country = db.Column(db.String(50))
#     aadhaar_number = db.Column(db.String(12), unique=True, nullable=False)
#     aadhaar_image_path = db.Column(db.String(255))  # Only this remains
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     modified_at = db.Column(
#         db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#     mobile = db.relationship('Mobile', backref='aadhaar_details')
#     application = db.relationship('Application', backref='aadhaar_details')


class AadhaarDetails(db.Model):
    __tablename__ = 'aadhaar_details'

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
    aadhaar_image_path = db.Column(db.String(255))

    verified = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    mobile = db.relationship('Mobile', backref='aadhaar_details', lazy=True)
    application = db.relationship(
        'Application', backref='aadhaar_details', lazy=True)

    otp_sessions = db.relationship(
        'AadhaarOTP',
        backref='aadhaar_detail',
        lazy=True,
        primaryjoin="AadhaarDetails.aadhaar_number == AadhaarOTP.aadhaar_number",
        foreign_keys='AadhaarOTP.aadhaar_number'
    )


class AadhaarOTP(db.Model):
    __tablename__ = 'aadhaar_otp'

    id = db.Column(db.Integer, primary_key=True)

    aadhaar_number = db.Column(
        db.String(12),
        db.ForeignKey('aadhaar_details.aadhaar_number'),
        nullable=False
    )

    client_id = db.Column(db.String(100))
    otp_txn_id = db.Column(db.String(100))

    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AadhaarSandboxDetails(db.Model):
    __tablename__ = 'aadhaar_sandbox_details'

    id = db.Column(db.Integer, primary_key=True)

    aadhaar_number = db.Column(db.String(12), unique=True, nullable=False)
    reference_id = db.Column(db.BigInteger, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    dob = db.Column(db.String(20), nullable=True)
    year_of_birth = db.Column(db.Integer, nullable=True)
    care_of = db.Column(db.String(255), nullable=True)
    full_address = db.Column(db.Text, nullable=True)
    house = db.Column(db.String(100), nullable=True)
    street = db.Column(db.String(255), nullable=True)
    landmark = db.Column(db.String(255), nullable=True)
    subdistrict = db.Column(db.String(100), nullable=True)
    vtc = db.Column(db.String(100), nullable=True)
    post_office = db.Column(db.String(100), nullable=True)
    district = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    pincode = db.Column(db.String(10), nullable=True)
    email_hash = db.Column(db.String(255), nullable=True)
    mobile_hash = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    message = db.Column(db.String(255), nullable=True)
    share_code = db.Column(db.String(10), nullable=True)
    photo_path = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    otp_details = db.relationship(
        'AadhaarOTPSandboxDetails', back_populates='sandbox_details'
    )

    applications = db.relationship(
        'Application', back_populates='aadhaar', cascade="all, delete-orphan"
    )


class AadhaarOTPSandboxDetails(db.Model):
    __tablename__ = 'aadhaar_otp_sandbox_details'

    id = db.Column(db.Integer, primary_key=True)
    aadhaar_id = db.Column(db.Integer, db.ForeignKey(
        'aadhaar_sandbox_details.id'))
    transaction_id = db.Column(db.String(255), nullable=True)
    client_id = db.Column(db.String(255), nullable=True)
    otp_sent = db.Column(db.Boolean, default=False)
    message = db.Column(db.String(255), nullable=True)
    reference_id = db.Column(db.String(255), nullable=True)
    entity = db.Column(db.String(255), nullable=True)
    code = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=True)
    test_otp = db.Column(db.String(10), nullable=True)  # For sandbox/testing
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sandbox_details = db.relationship(
        'AadhaarSandboxDetails', back_populates='otp_details')


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
    address_line = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    pincode = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    application = db.relationship('Application', backref='address_uploads')
    images = db.relationship(
        'AddressImage', backref='address_upload', cascade="all, delete-orphan")


class AddressImage(db.Model):
    __tablename__ = 'address_image'

    id = db.Column(db.Integer, primary_key=True)
    address_upload_id = db.Column(db.Integer, db.ForeignKey(
        'address_upload.id'), nullable=False)
    # Only one image path per row
    image_path = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


# class ESignatureUpload(db.Model):
#     __tablename__ = 'esignature_upload'

#     id = db.Column(db.Integer, primary_key=True)
#     application_id = db.Column(db.Integer, db.ForeignKey(
#         'application.id'), nullable=False)
#     image_path = db.Column(db.String(255), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     modified_at = db.Column(db.DateTime, default=datetime.utcnow)

#     application = db.relationship('Application', backref='esignature_uploads')

class ESignatureUpload(db.Model):
    __tablename__ = 'esignature_upload'

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey(
        'application.id'), nullable=False)
    # e-signature image path
    image_path = db.Column(db.String(255), nullable=True)
    # pan card image path (optional)
    pan_image_path = db.Column(db.String(255), nullable=True)
    esign_image_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    application = db.relationship('Application', backref='esignature_uploads')


class PanCard(db.Model):
    __tablename__ = 'pancards'

    id = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.Integer, db.ForeignKey('email.id'), nullable=False)
    pan_number = db.Column(db.String(10), nullable=False, unique=True)
    otp = db.Column(db.String(6), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expired_at = db.Column(db.DateTime, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)

    email = db.relationship("Email", backref=db.backref("pancards", lazy=True))


0
