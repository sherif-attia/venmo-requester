# Standard library imports
import re
from enum import Enum

from pydantic import BaseModel, condecimal, field_validator

# Constants for date validation
MIN_DAY = 1
MAX_DAY = 31
MIN_MONTH = 1
MAX_MONTH = 12


class PaymentFrequency(str, Enum):
    """Enumeration of possible payment frequencies"""

    MONTHLY = "monthly"
    YEARLY = "yearly"


class PaymentDate(BaseModel):
    """Model representing a payment date that can be either monthly or yearly"""

    value: str

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: str) -> str:
        """Validate the payment date format"""
        if not v:
            raise ValueError("Payment date cannot be empty")

        # Check if it's a monthly format (1-31)
        if v.isdigit():
            day = int(v)
            if not MIN_DAY <= day <= MAX_DAY:
                raise ValueError(f"Monthly payment date must be between {MIN_DAY} and {MAX_DAY}")
            return v

        # Check if it's a yearly format (MM-DD)
        if re.match(r"^\d{2}-\d{2}$", v):
            month, day = map(int, v.split("-"))
            if not MIN_MONTH <= month <= MAX_MONTH:
                raise ValueError(f"Month must be between {MIN_MONTH} and {MAX_MONTH}")
            if not MIN_DAY <= day <= MAX_DAY:
                raise ValueError(f"Day must be between {MIN_DAY} and {MAX_DAY}")
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
