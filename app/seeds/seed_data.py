from app.extensions import db
from app.models import BankName, Branch

banks_data = [
    {
        "bank_name": "First National Bank",
        "address": "123 Main St",
        "city": "New York",
        "state": "NY",
        "country": "USA",
        "branches": [
            {
                "branch_name": "Downtown Branch",
                "ifsc_code": "FNB001NY",
                "address": "123 Main St, Downtown",
                "status": "open",
                "city": "New York",
                "state": "NY",
                "country": "USA",
            },
            {
                "branch_name": "Uptown Branch",
                "ifsc_code": "FNB002NY",
                "address": "456 Uptown Ave",
                "status": "closed",
                "city": "New York",
                "state": "NY",
                "country": "USA",
            },
        ]
    },
    {
        "bank_name": "Global Trust Bank",
        "address": "789 Market St",
        "city": "San Francisco",
        "state": "CA",
        "country": "USA",
        "branches": [
            {
                "branch_name": "Market Street Branch",
                "ifsc_code": "GTB001CA",
                "address": "789 Market St",
                "status": "open",
                "city": "San Francisco",
                "state": "CA",
                "country": "USA",
            }
        ]
    },
    # ... add other banks here ...
]


def seed_banks_and_branches():
    for bank in banks_data:
        bank_obj = BankName(
            bank_name=bank['bank_name'],
            address=bank['address'],
            city=bank['city'],
            state=bank['state'],
            country=bank['country']
        )
        db.session.add(bank_obj)
        db.session.flush()  # get bank_id before commit

        for branch in bank['branches']:
            branch_obj = Branch(
                branch_name=branch['branch_name'],
                bank_id=bank_obj.bank_id,
                ifsc_code=branch['ifsc_code'],
                address=branch['address'],
                status=branch['status'],
                city=branch['city'],
                state=branch['state'],
                country=branch['country']
            )
            db.session.add(branch_obj)

    db.session.commit()
    print("Banks and branches seeded successfully.")
