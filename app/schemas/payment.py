from typing import Optional

from pydantic import BaseModel, Field, field_validator


class PaymentRequest(BaseModel):
    order_id: int
    card_number: str = Field(..., min_length=16, max_length=16)
    card_holder: str = Field(..., min_length=3, max_length=100)
    expiry_month: int = Field(..., ge=1, le=12)
    expiry_year: int = Field(..., ge=2024, le=2050)
    cvv: str = Field(..., min_length=3, max_length=4)

    @field_validator("card_number")
    @classmethod
    def validate_card_number(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("Card number must contain only digits")
        if len(v) != 16:
            raise ValueError("Card number must be 16 digits")
        return v

    @field_validator("cvv")
    @classmethod
    def validate_cvv(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("CVV must contain only digits")
        if len(v) not in [3, 4]:
            raise ValueError("CVV must be 3 or 4 digits")
        return v


class PaymentResponse(BaseModel):
    success: bool
    message: str
    order_id: int
    transaction_id: Optional[str] = None