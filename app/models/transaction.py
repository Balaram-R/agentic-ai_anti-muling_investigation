import enum
from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime,Enum,ForeignKey,Index,Numeric,String,func
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.db.base import Base
class TransactionType(str,enum.Enum): UPI="UPI"; TRANSFER="TRANSFER"
class TransactionPurpose(str,enum.Enum):
    GENERAL_TRANSFER="GENERAL_TRANSFER"; SHOP_PAYMENT="SHOP_PAYMENT"; BILL_PAYMENT="BILL_PAYMENT"; SALARY="SALARY"; INVESTMENT="INVESTMENT"; OTHER="OTHER"
class TransactionStatus(str,enum.Enum): PROCESSING="PROCESSING"; SETTLED="SETTLED"
class Transaction(Base):
    __tablename__="transactions"
    __table_args__=(Index("ix_tx_sender_ts","sender_account_id","timestamp"),Index("ix_tx_receiver_ts","receiver_account_id","timestamp"))
    transaction_id:Mapped[str]=mapped_column(String(36),primary_key=True)
    transaction_type:Mapped[TransactionType]=mapped_column(Enum(TransactionType,name="transaction_type"),nullable=False)
    sender_account_id:Mapped[str]=mapped_column(ForeignKey("accounts.account_id"),nullable=False)
    receiver_account_id:Mapped[str]=mapped_column(ForeignKey("accounts.account_id"),nullable=False)
    amount:Mapped[Decimal]=mapped_column(Numeric(18,2),nullable=False)
    currency:Mapped[str]=mapped_column(String(3),nullable=False)
    purpose:Mapped[TransactionPurpose]=mapped_column(Enum(TransactionPurpose,name="transaction_purpose"),nullable=False)
    timestamp:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    status:Mapped[TransactionStatus]=mapped_column(Enum(TransactionStatus,name="transaction_status"),nullable=False)
    sender_account=relationship("Account",foreign_keys=[sender_account_id],back_populates="sent_transactions")
    receiver_account=relationship("Account",foreign_keys=[receiver_account_id],back_populates="received_transactions")
