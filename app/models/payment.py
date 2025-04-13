from decimal import Decimal
from pydantic import BaseModel, Field

class PaymentRequest(BaseModel):
    venmo_id: str
    note: str
    amount: Decimal = Field(ge=0)

class PaymentResult(BaseModel):
    request: PaymentRequest
    success: bool
    error_message: str | None = None 