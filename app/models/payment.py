from decimal import Decimal
from pydantic import BaseModel, Field, validator, condecimal
import re
from datetime import datetime
from enum import Enum

class PaymentFrequency(str, Enum):
    """Enumeration of possible payment frequencies"""
    MONTHLY = "monthly"
    YEARLY = "yearly"

class PaymentDate(BaseModel):
    """Model representing a payment date that can be either monthly or yearly"""
    value: str
    
    @validator('value')
    def validate_value(cls, v: str, values: dict) -> str:
        """Validate the payment date format"""
        if not v:
            raise ValueError("Payment date cannot be empty")
            
        # Check if it's a monthly format (1-31)
        if v.isdigit():
            day = int(v)
            if not 1 <= day <= 31:
                raise ValueError("Monthly payment date must be between 1 and 31")
            return v
            
        # Check if it's a yearly format (MM-DD)
        if re.match(r'^\d{2}-\d{2}$', v):
            month, day = map(int, v.split('-'))
            if not 1 <= month <= 12:
                raise ValueError("Month must be between 1 and 12")
            if not 1 <= day <= 31:
                raise ValueError("Day must be between 1 and 31")
            return v
            
        raise ValueError("Payment date must be either a day (1-31) or in MM-DD format")

class PaymentRequest(BaseModel):
    """Model representing a payment request for Venmo"""
    venmo_id: str
    amount: condecimal(gt=0, decimal_places=2)
    note: str
    frequency: PaymentFrequency
    payment_date: PaymentDate

class PaymentResult(BaseModel):
    request: PaymentRequest
    success: bool
    error_message: str | None = None 