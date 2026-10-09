from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel,ConfigDict,Field,field_validator
from app.models.transaction import TransactionPurpose,TransactionStatus,TransactionType
class TransactionCreate(BaseModel):
    transaction_type:TransactionType; sender_account_id:str=Field(min_length=1,max_length=32); receiver_account_id:str=Field(min_length=1,max_length=32); amount:Decimal; currency:str=Field(min_length=3,max_length=3); purpose:TransactionPurpose
    @field_validator("amount")
    @classmethod
    def positive(cls,v):
        if v<=0: raise ValueError("Amount must be greater than zero")
        if v.as_tuple().exponent < -2: raise ValueError("Amount may have at most two decimal places")
        return v
    @field_validator("currency")
    @classmethod
    def currency(cls,v):
        v=v.upper()
        if v!="INR": raise ValueError("Unsupported currency")
        return v
class TransactionRead(BaseModel):
    model_config=ConfigDict(from_attributes=True,use_enum_values=True)
    transaction_id:str; transaction_type:TransactionType; sender_account_id:str; receiver_account_id:str; amount:Decimal; currency:str; purpose:TransactionPurpose; timestamp:datetime; status:TransactionStatus
