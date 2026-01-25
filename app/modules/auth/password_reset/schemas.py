from pydantic import BaseModel, Field, EmailStr


class PasswordResetRequest(BaseModel):
    """Request to initiate password reset"""
    email: EmailStr = Field(..., description="Company email")


class PasswordResetVerify(BaseModel):
    """Request to verify OTP and reset password"""
    email: EmailStr = Field(..., description="Company email")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP")
    new_password: str = Field(..., min_length=8, description="New password (min 8 chars)")
