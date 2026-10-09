from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.account import Account
class AccountRepository:
    def get(self,db:Session,account_id:str,for_update=False):
        q=select(Account).where(Account.account_id==account_id)
        if for_update: q=q.with_for_update()
        return db.execute(q).scalar_one_or_none()
