# Config class (loads .env)

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
# Twilio configuration
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")           # for SMS
    TWILIO_WHATSAPP_NUMBER = os.getenv(
        "TWILIO_WHATSAPP_NUMBER")     # for WhatsApp
# SendGrid Email configuration
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    FROM_EMAIL = os.getenv("FROM_EMAIL")  # Verified sender email on SendGrid


# Sandbox Config
    SSANDBOX_API_KEY = os.getenv('SSANDBOX_API_KEY')
    SSANDBOX_API_SECRET = os.getenv('SSANDBOX_API_SECRET')
    SSANDBOX_JWT_TOKEN = os.getenv('SSANDBOX_JWT_TOKEN')
    SSANDBOX_BASE_URL = os.getenv('SSANDBOX_BASE_URL')
