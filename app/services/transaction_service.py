import logging
from uuid import uuid4
from app.models.transaction import Transaction,TransactionStatus
from app.repositories.accounts import AccountRepository
from app.repositories.transactions import TransactionRepository
logger=logging.getLogger(__name__)
class TransactionServiceError(Exception): status_code=400
class AccountNotFoundError(TransactionServiceError): status_code=404
class InsufficientBalanceError(TransactionServiceError): status_code=409
class TransactionService:
    def __init__(self,accounts=None,transactions=None): self.accounts=accounts or AccountRepository(); self.transactions=transactions or TransactionRepository()
    def create(self,db,req):
        if req.sender_account_id==req.receiver_account_id: raise TransactionServiceError("Sender and receiver must be different accounts")
        sender=self.accounts.get(db,req.sender_account_id,True)
        if sender is None: raise AccountNotFoundError(f"Sender account not found: {req.sender_account_id}")
        receiver=self.accounts.get(db,req.receiver_account_id,True)
        if receiver is None: raise AccountNotFoundError(f"Receiver account not found: {req.receiver_account_id}")
        if sender.currency!=req.currency or receiver.currency!=req.currency: raise TransactionServiceError("Transaction currency must match both account currencies")
        if sender.balance<req.amount: raise InsufficientBalanceError("Insufficient balance")
        t=Transaction(transaction_id=f"TXN-{uuid4().hex[:12].upper()}",transaction_type=req.transaction_type,sender_account_id=sender.account_id,receiver_account_id=receiver.account_id,amount=req.amount,currency=req.currency,purpose=req.purpose,status=TransactionStatus.PROCESSING)
        self.transactions.add(db,t); sender.balance-=req.amount; receiver.balance+=req.amount; t.status=TransactionStatus.SETTLED
        return t
