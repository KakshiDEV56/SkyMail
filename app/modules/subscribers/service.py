"""
Subscription service for managing newsletter subscriptions.

Handles:
- Email validation and normalization
- Origin/website validation
- Deduplication checks
- Tier-based limits (free vs premium)
- Atomic database operations
- Welcome email notifications
"""

import re
import uuid
from typing import Tuple, Optional
from urllib.parse import urlparse
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from loguru import logger
from fastapi import BackgroundTasks

from app.modules.auth.model import Company
from app.modules.subscribers.model import Subscriber
from app.utils.mail.email_service import EmailService


class SubscriptionService:
    """Service for managing public newsletter subscriptions."""

    # Email regex pattern for basic validation
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    @staticmethod
    def normalize_email(email: str) -> str:
        """
        Normalize email: lowercase and trim whitespace.
        
        Args:
            email: Raw email input
            
        Returns:
            Normalized email
        """
        return email.strip().lower()

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email format.
        
        Args:
            email: Email to validate
            
        Returns:
            (is_valid, error_message)
        """
        if not email or not isinstance(email, str):
            return False, "Email is required"
        
        if len(email) > 255:
            return False, "Email too long"
        
        if not SubscriptionService.EMAIL_PATTERN.match(email):
            return False, "Invalid email format"
        
        return True, ""

    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        """
        Extract domain from URL.
        
        Args:
            url: URL string (e.g., https://example.com or example.com)
            
        Returns:
            Normalized domain (lowercase) or None if invalid
        """
        try:
            if not url:
                return None
            
            # Add scheme if missing
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            parsed = urlparse(url)
            domain = parsed.netloc.lower() if parsed.netloc else None
            
            return domain
        except Exception as e:
            logger.error(f"Failed to extract domain from {url}: {str(e)}")
            return None

    @staticmethod
    def is_origin_allowed(origin: str, website_url: str) -> bool:
        """
        Validate if request origin matches company website.
        
        Supports:
        - Exact domain match: origin.com == website.com
        - Subdomain match: blog.origin.com matches origin.com
        
        Args:
            origin: Request Origin header (e.g., https://blog.example.com)
            website_url: Company website URL from database
            
        Returns:
            True if origin is allowed
        """
        if not origin or not website_url:
            return False
        
        origin_domain = SubscriptionService.extract_domain(origin)
        website_domain = SubscriptionService.extract_domain(website_url)
        
        if not origin_domain or not website_domain:
            return False
        
        # Exact match
        if origin_domain == website_domain:
            return True
        
        # Subdomain match: blog.example.com matches example.com
        if origin_domain.endswith(f".{website_domain}"):
            return True
        
        return False

    @staticmethod
    async def subscribe(
        company_id: str,
        email: str,
        origin: Optional[str],
        db: Session,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> Tuple[bool, dict]:
        """
        Subscribe an email to company newsletter.
        
        Workflow:
        1. Validate company exists and is active
        2. Validate email format
        3. Check origin header against company website
        4. Normalize email
        5. Check for existing subscription
        6. Enforce tier limits
        7. Insert subscriber (transactional)
        8. Increment company subscriber_count (atomic)
        
        Args:
            company_id: UUID of company
            email: Email to subscribe
            origin: Request Origin header
            db: Database session
            
        Returns:
            (success, response_dict)
        """
        try:
            # Step 1: Validate and fetch company
            company = db.query(Company).filter(
                Company.id == uuid.UUID(company_id)
            ).first()
            
            if not company:
                return False, {
                    "status": "error",
                    "code": "company_not_found",
                    "message": "Company not found"
                }
            
            if not company.is_verified:
                return False, {
                    "status": "error",
                    "code": "company_inactive",
                    "message": "Company is not active"
                }
            
            # Step 2: Validate email format
            is_valid, error_msg = SubscriptionService.validate_email(email)
            if not is_valid:
                return False, {
                    "status": "error",
                    "code": "invalid_email",
                    "message": error_msg
                }
            
            # Step 3: Origin validation
            if company.website_url and origin:
                if not SubscriptionService.is_origin_allowed(origin, company.website_url):
                    logger.warning(
                        f"Origin validation failed. Origin: {origin}, "
                        f"Company website: {company.website_url}"
                    )
                    return False, {
                        "status": "error",
                        "code": "invalid_origin",
                        "message": "Request origin not allowed"
                    }
            
            # Step 4: Normalize email
            normalized_email = SubscriptionService.normalize_email(email)
            
            # Step 5: Check for existing subscription
            existing = db.query(Subscriber).filter(
                and_(
                    Subscriber.company_id == uuid.UUID(company_id),
                    Subscriber.email == normalized_email
                )
            ).first()
            
            if existing:
                if existing.status == "subscribed":
                    # Already subscribed
                    return True, {
                        "status": "already_subscribed",
                        "message": "Email already subscribed",
                        "subscriber_id": str(existing.id),
                        "email": normalized_email
                    }
                else:
                    # Re-activate unsubscribed email
                    existing.status = "subscribed"
                    existing.source_origin = origin
                    db.commit()
                    
                    # Send welcome email for resubscription
                    if background_tasks:
                        background_tasks.add_task(
                            EmailService.send_subscription_welcome_email,
                            normalized_email,
                            company.company_name,
                            company.website_url
                        )
                    
                    return True, {
                        "status": "resubscribed",
                        "message": "Successfully resubscribed",
                        "subscriber_id": str(existing.id),
                        "email": normalized_email
                    }
            
            # Step 6: Enforce free tier limits
            if not company.is_premium:
                if company.subscriber_count >= company.max_subscribers:
                    logger.warning(
                        f"Free tier subscriber limit reached for company {company_id}. "
                        f"Current: {company.subscriber_count}, Max: {company.max_subscribers}"
                    )
                    return False, {
                        "status": "error",
                        "code": "upgrade_required",
                        "message": f"Subscriber limit reached ({company.max_subscribers}). Please upgrade to premium.",
                        "max_subscribers": company.max_subscribers,
                        "current_subscribers": company.subscriber_count
                    }
            
            # Step 7: Create new subscription (transactional)
            new_subscriber = Subscriber(
                id=uuid.uuid4(),
                company_id=uuid.UUID(company_id),
                email=normalized_email,
                status="subscribed",
                source_origin=origin
            )
            
            db.add(new_subscriber)
            
            # Step 8: Increment subscriber count atomically
            company.subscriber_count = (company.subscriber_count or 0) + 1
            
            # Commit transaction
            db.commit()
            db.refresh(new_subscriber)
            
            # Send welcome email in background
            if background_tasks:
                background_tasks.add_task(
                    EmailService.send_subscription_welcome_email,
                    normalized_email,
                    company.company_name,
                    company.website_url
                )
            
            logger.info(
                f"Subscription successful. Company: {company_id}, "
                f"Email: {normalized_email}, Total: {company.subscriber_count}"
            )
            
            return True, {
                "status": "subscribed",
                "message": "Successfully subscribed to newsletter",
                "subscriber_id": str(new_subscriber.id),
                "email": normalized_email
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Subscription error for company {company_id}: {str(e)}")
            return False, {
                "status": "error",
                "code": "subscription_failed",
                "message": "Failed to process subscription"
            }

    @staticmethod
    def unsubscribe(
        company_id: str,
        email: str,
        db: Session,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> Tuple[bool, dict]:
        """
        Unsubscribe an email from company newsletter.
        
        Args:
            company_id: UUID of company
            email: Email to unsubscribe
            db: Database session
            background_tasks: Optional BackgroundTasks for sending emails
            
        Returns:
            (success, response_dict)
        """
        try:
            normalized_email = SubscriptionService.normalize_email(email)
            
            subscriber = db.query(Subscriber).filter(
                and_(
                    Subscriber.company_id == uuid.UUID(company_id),
                    Subscriber.email == normalized_email
                )
            ).first()
            
            if not subscriber:
                return False, {
                    "status": "error",
                    "code": "subscriber_not_found",
                    "message": "Subscriber not found"
                }
            
            if subscriber.status == "unsubscribed":
                return True, {
                    "status": "already_unsubscribed",
                    "message": "Already unsubscribed"
                }
            
            # Mark as unsubscribed (keep record for re-subscribe)
            subscriber.status = "unsubscribed"
            
            # Decrement subscriber count
            company = db.query(Company).filter(
                Company.id == uuid.UUID(company_id)
            ).first()
            
            if company:
                company.subscriber_count = max(0, (company.subscriber_count or 1) - 1)
            
            db.commit()
            
            # Send unsubscribe confirmation email in background
            if background_tasks and company:
                background_tasks.add_task(
                    EmailService.send_unsubscribe_confirmation_email,
                    normalized_email,
                    company.company_name,
                    company.website_url
                )
            
            logger.info(
                f"Unsubscription successful. Company: {company_id}, "
                f"Email: {normalized_email}"
            )
            
            return True, {
                "status": "unsubscribed",
                "message": "Successfully unsubscribed"
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Unsubscription error for company {company_id}: {str(e)}")
            return False, {
                "status": "error",
                "code": "unsubscription_failed",
                "message": "Failed to process unsubscription"
            }
