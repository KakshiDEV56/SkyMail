"""Campaign API schemas."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid


class CampaignCreateRequest(BaseModel):
    """Schema for creating a campaign."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Campaign name")
    template_id: uuid.UUID = Field(..., description="Newsletter template ID to use")
    scheduled_for: datetime = Field(..., description="When to send (UTC)")
    send_timezone: Optional[str] = Field(
        default="UTC",
        description="Timezone for display (e.g., 'America/New_York')"
    )


class CampaignScheduleRequest(BaseModel):
    """Schema for scheduling a campaign."""
    
    scheduled_for: datetime = Field(..., description="When to send (UTC)")
    send_timezone: Optional[str] = Field(
        default="UTC",
        description="Timezone for display"
    )


class CampaignRescheduleRequest(BaseModel):
    """Schema for rescheduling an existing campaign."""
    
    scheduled_for: datetime = Field(..., description="New schedule time (UTC)")
    send_timezone: Optional[str] = Field(
        default="UTC",
        description="Timezone for display"
    )


class CampaignResponse(BaseModel):
    """Campaign response schema."""
    
    id: uuid.UUID
    company_id: uuid.UUID
    template_id: Optional[uuid.UUID]
    name: str
    subject: str
    scheduled_for: Optional[datetime]
    send_timezone: Optional[str]
    status: str
    sent_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CampaignListResponse(BaseModel):
    """List of campaigns with pagination."""
    
    total: int
    page: int
    page_size: int
    campaigns: list[CampaignResponse]


class CampaignStatusResponse(BaseModel):
    """Campaign status response."""
    
    id: uuid.UUID
    status: str
    sent_count: int = 0
    failed_count: int = 0
    total_recipients: int = 0
    scheduled_for: Optional[datetime]
    sent_at: Optional[datetime]
