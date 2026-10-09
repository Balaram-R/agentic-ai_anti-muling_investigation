from decimal import Decimal
from sqlalchemy import Numeric,String
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.db.base import Base
class Account(Base):
    __tablename__="accounts"
    account_id:Mapped[str]=mapped_column(String(32),primary_key=True)
    bank_name:Mapped[str]=mapped_column(String(100),nullable=False)
    customer_name:Mapped[str]=mapped_column(String(150),nullable=False)
    account_number:Mapped[str]=mapped_column(String(32),unique=True,nullable=False,index=True)
    balance:Mapped[Decimal]=mapped_column(Numeric(18,2),nullable=False)
    currency:Mapped[str]=mapped_column(String(3),nullable=False)
    sent_transactions=relationship("Transaction",foreign_keys="Transaction.sender_account_id",back_populates="sender_account")
    received_transactions=relationship("Transaction",foreign_keys="Transaction.receiver_account_id",back_populates="receiver_account")
    aml_profile = relationship(
    "AMLProfile",
    back_populates="account",
    uselist=False,
    cascade="all, delete-orphan",
    )