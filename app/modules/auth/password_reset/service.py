import uuid
from typing import Tuple, Optional
from sqlalchemy.orm import Session
from loguru import logger

from app.modules.auth.model import Company
from app.redis.redis_manager import redis_manager
from app.utils.password_handler import hash_password
from app.utils.mail.email_service import EmailService


class PasswordResetService:
    """Service for password reset operations"""

    @staticmethod
    async def request_password_reset(
        email: str,
        db: Session
    ) -> Tuple[bool, str]:
        """
        Generate OTP for password reset and send via email
        
        Args:
            email: Company email
            db: Database session
            
        Returns:
            (success, message)
        """
        try:
            # Check if company exists
            company = db.query(Company).filter(Company.email == email).first()
            if not company:
                # Don't reveal if email exists (security best practice)
                logger.info(f"Password reset requested for non-existent email: {email}")
                return True, "If email exists, OTP will be sent"
            
            # Generate OTP
            otp = str(uuid.uuid4().int)[:6]  # 6-digit OTP
            
            # Store OTP in Redis with 10-minute expiry
            redis_key = f"password_reset:{email}"
            await redis_manager.setex(redis_key, 600, otp)
            
            # Send OTP via email
            await EmailService.send_password_reset_otp(email, otp)
            
            logger.info(f"Password reset OTP sent to {email}")
            return True, "OTP sent to your email"
            
        except Exception as e:
            logger.error(f"Password reset request error for {email}: {str(e)}")
            return False, "Failed to process password reset request"

    @staticmethod
    async def verify_reset_otp_and_update_password(
        email: str,
        otp: str,
        new_password: str,
        db: Session
    ) -> Tuple[bool, str]:
        """
        Verify OTP and update password
        
        Args:
            email: Company email
            otp: OTP entered by user
            new_password: New password
            db: Database session
            
        Returns:
            (success, message)
        """
        try:
            # Get company
            company = db.query(Company).filter(Company.email == email).first()
            if not company:
                return False, "Company not found"
            
            # Verify OTP from Redis
            redis_key = f"password_reset:{email}"
            stored_otp = await redis_manager.get(redis_key)
            
            if not stored_otp:
                return False, "OTP expired or not found"
            
            if stored_otp.strip() != otp.strip():
                logger.warning(f"OTP mismatch for {email}. Expected: {stored_otp}, Got: {otp}")
                return False, "Invalid OTP"
            
            # Update password
            company.password_hash = hash_password(new_password)
            db.commit()
            db.refresh(company)
            
            # Delete OTP from Redis
            await redis_manager.delete(redis_key)
            
            logger.info(f"Password reset successful for {email}")
            return True, "Password updated successfully"
            
        except Exception as e:
            db.rollback()
            logger.error(f"Password reset verification error for {email}: {str(e)}")
            return False, "Failed to reset password"
