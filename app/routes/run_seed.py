from app import create_app
from app.extensions import db
from app.seeds.seed_data import seed_banks_and_branches

app = create_app()

with app.app_context():
    seed_banks_and_branches()
