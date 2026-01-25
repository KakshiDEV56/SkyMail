"""
Pydantic schemas for subscription endpoints.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class SubscribeRequest(BaseModel):
    """Request to subscribe to newsletter."""
    email: EmailStr = Field(..., description="Email to subscribe")


class SubscribeResponse(BaseModel):
    """Response from subscription endpoint."""
    status: str = Field(..., description="Subscription status (subscribed, already_subscribed, resubscribed, error)")
    message: str = Field(..., description="Human-readable message")
    subscriber_id: Optional[str] = Field(None, description="ID of subscriber (if successful)")
    email: Optional[str] = Field(None, description="Normalized email")
    code: Optional[str] = Field(None, description="Error code (if failed)")
    max_subscribers: Optional[int] = Field(None, description="Max subscribers for tier (if upgrade_required)")
    current_subscribers: Optional[int] = Field(None, description="Current subscriber count (if upgrade_required)")


class UnsubscribeRequest(BaseModel):
    """Request to unsubscribe from newsletter."""
    email: EmailStr = Field(..., description="Email to unsubscribe")


class UnsubscribeResponse(BaseModel):
    """Response from unsubscription endpoint."""
    status: str = Field(..., description="Unsubscription status")
    message: str = Field(..., description="Human-readable message")
    code: Optional[str] = Field(None, description="Error code (if failed)")
