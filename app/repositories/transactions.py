from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.transaction import Transaction
class TransactionRepository:
    def add(self,db,t): db.add(t); return t
    def get(self,db,id): return db.execute(select(Transaction).where(Transaction.transaction_id==id)).scalar_one_or_none()
    def list_all(self,db): return list(db.execute(select(Transaction).order_by(Transaction.timestamp.desc())).scalars())
    def list_for_account(self,db,id): return list(db.execute(select(Transaction).where((Transaction.sender_account_id==id)|(Transaction.receiver_account_id==id)).order_by(Transaction.timestamp.desc())).scalars())
