"""
Pydantic schemas for billing endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CreateOrderRequest(BaseModel):
    """Request to create a Razorpay order for premium subscription."""
    plan: str = Field(default="premium", description="Subscription plan (currently only 'premium')")


class CreateOrderResponse(BaseModel):
    """Response with Razorpay order details."""
    order_id: str = Field(..., description="Razorpay order ID")
    amount: int = Field(..., description="Amount in paise (smallest currency unit for INR)")
    currency: str = Field(..., description="Currency code (INR)")
    key_id: str = Field(..., description="Razorpay key ID for frontend")


class VerifyPaymentRequest(BaseModel):
    """Request to verify Razorpay payment."""
    razorpay_order_id: str = Field(..., description="Razorpay order ID")
    razorpay_payment_id: str = Field(..., description="Razorpay payment ID")
    razorpay_signature: str = Field(..., description="Razorpay signature for verification")


class VerifyPaymentResponse(BaseModel):
    """Response after payment verification."""
    success: bool = Field(..., description="Whether payment was verified successfully")
    message: str = Field(..., description="Success or error message")
    subscription_tier: Optional[str] = Field(None, description="Updated subscription tier")
    is_premium: Optional[bool] = Field(None, description="Premium status")
    subscription_end_date: Optional[datetime] = Field(None, description="Subscription end date")


class PaymentHistoryItem(BaseModel):
    """Individual payment record."""
    id: str
    amount: float
    currency: str
    subscription_plan: str
    razorpay_payment_id: Optional[str]
    created_at: datetime
    valid_until: Optional[datetime]


class PaymentHistoryResponse(BaseModel):
    """Response with payment history."""
    payments: list[PaymentHistoryItem]
    total: int
