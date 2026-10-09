from decimal import Decimal
from pydantic import BaseModel,ConfigDict
class AccountRead(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    account_id:str; bank_name:str; customer_name:str; account_number:str; balance:Decimal; currency:str
