# Customer Onboarding APIs

Flask-based API for customer onboarding with mobile verification, account preferences, and Aadhaar OCR.

## 🚀 Setup Instructions

### 1. Clone the Repository

````bash
git clone https://github.com/yourusername/customer_onboarding_apis.git
cd customer_onboarding_apis


### 2. Create a Virtual Environment

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

### 3. Install Requirements
pip install -r requirements.txt

### 4.  Run Database Migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade


### 4. For dependencies

pip install -r requirements.txt


### 5. Run the App
flask run (default: 5000)
or
python app.py(this runs on configured localhost:8000)

Requirements
Flask

Flask-Migrate

Flask-SQLAlchemy

PyMySQL

Pillow

pytesseract

python-dotenv


Then commit and push:

```bash
git add README.md
git commit -m "Add README"
git push
````
