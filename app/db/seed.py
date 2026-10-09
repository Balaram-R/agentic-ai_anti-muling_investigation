from decimal import Decimal
from sqlalchemy import select
from app.models import Account
SEED=[("AI-ACC-1842","AI Bank","Balaram Ramji","AI-ACC-1842",Decimal("2500000.00"),"INR"),("BANKB-ACC-5276","Bank B","Priya Menon","BANKB-ACC-5276",Decimal("1000000.00"),"INR")]
def seed(db):
    have={x.account_id for x in db.execute(select(Account)).scalars()}
    for account_id,bank,customer,num,balance,currency in SEED:
        if account_id not in have: db.add(Account(account_id=account_id,bank_name=bank,customer_name=customer,account_number=num,balance=balance,currency=currency))
    db.commit()
