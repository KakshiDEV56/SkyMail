from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class CompanyProfileResponse(BaseModel):
    """Company profile response"""
    id: UUID
    username: str
    email: str
    company_name: str
    website_url: Optional[str]
    profile_image_key: Optional[str]
    is_verified: bool
    subscription_tier: str
    is_premium: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CompanyProfileUpdateRequest(BaseModel):
    """Request to update company profile"""
    company_name: Optional[str] = None
    website_url: Optional[str] = None


class CompanyProfileImageResponse(BaseModel):
    """Response for profile image upload"""
    message: str
    s3_url: str
    profile_image_key: str
