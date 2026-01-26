"""Campaign business logic service."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session
from loguru import logger

from app.modules.campaign.model import Campaign
from app.modules.campaign.send_log import CampaignSendLog
from app.modules.newsletters.newsletter_templates.model import NewsletterTemplate
from app.modules.subscribers.model import Subscriber
from app.modules.auth.model import Company
from app.utils.exceptions import (
    ResourceNotFoundError,
    ValidationError,
    PermissionError as AppPermissionError,
)


class CampaignService:
    """Service for campaign operations."""
    
    @staticmethod
    def create_campaign(
        db: Session,
        company_id: uuid.UUID,
        name: str,
        template_id: uuid.UUID,
        constants_values: dict,
        scheduled_for: datetime,
        send_timezone: str = "UTC",
    ) -> Campaign:
        """
        Create a new campaign in 'draft' status.
        
        Args:
            db: Database session
            company_id: Owner company ID
            name: Campaign name
            template_id: Newsletter template ID
            constants_values: Values for template constants
            scheduled_for: Scheduled send time (UTC)
            send_timezone: Timezone for display
        
        Returns:
            Campaign object
        
        Raises:
            ResourceNotFoundError: If template not found or doesn't belong to company
            ValidationError: If validation fails
        """
        
        # Verify template exists and belongs to company
        template = db.execute(
            select(NewsletterTemplate).where(
                and_(
                    NewsletterTemplate.id == template_id,
                    NewsletterTemplate.company_id == company_id,
                )
            )
        ).scalar_one_or_none()
        
        if not template:
            raise ResourceNotFoundError(f"Template {template_id} not found or doesn't belong to your company")
        
        # Validate constants_values matches template constants
        if set(constants_values.keys()) != set(template.constants):
            missing = set(template.constants) - set(constants_values.keys())
            extra = set(constants_values.keys()) - set(template.constants)
            msg = "Constants mismatch: "
            if missing:
                msg += f"missing {list(missing)}"
            if extra:
                msg += (", " if missing else "") + f"extra {list(extra)}"
            raise ValidationError(msg)
        
        # Validate no empty values
        empty_keys = [k for k, v in constants_values.items() if not v or str(v).strip() == ""]
        if empty_keys:
            raise ValidationError(f"Empty values for constants: {empty_keys}")
        
        # Validate scheduled_for is in the future
        now = datetime.now(timezone.utc)
        if scheduled_for <= now:
            raise ValidationError("scheduled_for must be in the future (UTC)")
        
        # Create campaign
        campaign = Campaign(
            id=uuid.uuid4(),
            company_id=company_id,
            template_id=template_id,
            name=name,
            subject=template.subject,  # Copy template subject
            constants_values=constants_values,
            scheduled_for=scheduled_for,
            send_timezone=send_timezone,
            status="draft",
        )
        
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        
        logger.info(f"✅ Created campaign {campaign.id} (Company: {company_id})")
        
        return campaign
    
    @staticmethod
    def schedule_campaign(
        db: Session,
        company_id: uuid.UUID,
        campaign_id: uuid.UUID,
        scheduled_for: datetime,
        send_timezone: str = "UTC",
    ) -> Campaign:
        """
        Schedule a campaign (draft → scheduled).
        
        Checks:
        - Campaign exists and belongs to company
        - Campaign status is 'draft'
        - scheduled_for is in the future
        - Subscriber count doesn't exceed plan limit
        
        Args:
            db: Database session
            company_id: Company ID
            campaign_id: Campaign ID
            scheduled_for: When to send (UTC)
            send_timezone: Timezone for display
        
        Returns:
            Updated Campaign object
        
        Raises:
            ResourceNotFoundError: If campaign not found
            ValidationError: If validation fails
            PermissionError: If campaign doesn't belong to company
        """
        
        # Fetch campaign
        campaign = db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        ).scalar_one_or_none()
        
        if not campaign:
            raise ResourceNotFoundError(f"Campaign {campaign_id} not found")
        
        # Check ownership
        if campaign.company_id != company_id:
            raise AppPermissionError("Campaign doesn't belong to your company")
        
        # Check status
        if campaign.status != "draft":
            raise ValidationError(f"Campaign must be in 'draft' status, but is '{campaign.status}'")
        
        # Validate scheduled_for
        now = datetime.now(timezone.utc)
        if scheduled_for <= now:
            raise ValidationError("scheduled_for must be in the future (UTC)")
        
        # Check subscriber count vs plan limit
        company = db.execute(
            select(Company).where(Company.id == company_id)
        ).scalar_one_or_none()
        
        if not company:
            raise ResourceNotFoundError("Company not found")
        
        subscriber_count = db.execute(
            select(func.count(Subscriber.id)).where(
                and_(
                    Subscriber.company_id == company_id,
                    Subscriber.status == "subscribed",
                )
            )
        ).scalar()
        
        # Plan enforcement
        if company.subscription_tier == "free" and subscriber_count > 250:
            raise ValidationError(
                f"Free plan limited to 250 subscribers. Your company has {subscriber_count}. "
                "Upgrade your plan to send to more subscribers."
            )
        
        # Update campaign
        now = datetime.now(timezone.utc)
        campaign.status = "scheduled"
        campaign.scheduled_for = scheduled_for
        campaign.send_timezone = send_timezone
        campaign.updated_at = now
        
        db.commit()
        db.refresh(campaign)
        
        logger.info(f"✅ Scheduled campaign {campaign_id} for {scheduled_for}")
        
        return campaign
    
    @staticmethod
    def cancel_campaign(
        db: Session,
        company_id: uuid.UUID,
        campaign_id: uuid.UUID,
    ) -> Campaign:
        """
        Cancel a campaign (draft/scheduled → cancelled).
        
        Can only cancel campaigns in draft or scheduled status.
        
        Args:
            db: Database session
            company_id: Company ID
            campaign_id: Campaign ID
        
        Returns:
            Updated Campaign object
        
        Raises:
            ResourceNotFoundError: If campaign not found
            ValidationError: If campaign is already sent/sending/cancelled
            PermissionError: If campaign doesn't belong to company
        """
        
        # Fetch campaign
        campaign = db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        ).scalar_one_or_none()
        
        if not campaign:
            raise ResourceNotFoundError(f"Campaign {campaign_id} not found")
        
        # Check ownership
        if campaign.company_id != company_id:
            raise AppPermissionError("Campaign doesn't belong to your company")
        
        # Check status
        if campaign.status not in ("draft", "scheduled"):
            raise ValidationError(
                f"Can only cancel campaigns in 'draft' or 'scheduled' status, "
                f"but this campaign is '{campaign.status}'"
            )
        
        # Update campaign
        now = datetime.now(timezone.utc)
        campaign.status = "cancelled"
        campaign.updated_at = now
        
        db.commit()
        db.refresh(campaign)
        
        logger.info(f"✅ Cancelled campaign {campaign_id}")
        
        return campaign
    
    @staticmethod
    def reschedule_campaign(
        db: Session,
        company_id: uuid.UUID,
        campaign_id: uuid.UUID,
        scheduled_for: datetime,
        send_timezone: str = "UTC",
    ) -> Campaign:
        """
        Reschedule an existing campaign (draft/scheduled only).
        
        Allows changing the scheduled_for time for campaigns that haven't been sent yet.
        Can reschedule draft or scheduled campaigns.
        
        Args:
            db: Database session
            company_id: Company ID
            campaign_id: Campaign ID
            scheduled_for: New schedule time (UTC)
            send_timezone: Timezone for display
        
        Returns:
            Updated Campaign object
        
        Raises:
            ResourceNotFoundError: If campaign not found
            ValidationError: If validation fails or campaign can't be rescheduled
            PermissionError: If campaign doesn't belong to company
        """
        
        # Fetch campaign
        campaign = db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        ).scalar_one_or_none()
        
        if not campaign:
            raise ResourceNotFoundError(f"Campaign {campaign_id} not found")
        
        # Check ownership
        if campaign.company_id != company_id:
            raise AppPermissionError("Campaign doesn't belong to your company")
        
        # Check status - can only reschedule draft or scheduled campaigns
        if campaign.status not in ("draft", "scheduled"):
            raise ValidationError(
                f"Can only reschedule campaigns in 'draft' or 'scheduled' status, "
                f"but this campaign is '{campaign.status}'"
            )
        
        # Validate scheduled_for is in the future
        now = datetime.now(timezone.utc)
        if scheduled_for <= now:
            raise ValidationError("scheduled_for must be in the future (UTC)")
        
        # Update campaign - CRITICAL: transition to scheduled status
        campaign.scheduled_for = scheduled_for
        campaign.send_timezone = send_timezone
        campaign.status = "scheduled"  # 🎯 KEY FIX: transition to scheduled
        campaign.updated_at = now
        
        db.commit()
        db.refresh(campaign)
        
        logger.info(f"✅ Rescheduled campaign {campaign_id} to {scheduled_for}")
        
        return campaign
    
    @staticmethod
    def get_campaign(
        db: Session,
        company_id: uuid.UUID,
        campaign_id: uuid.UUID,
    ) -> Campaign:
        """
        Get campaign details.
        
        Args:
            db: Database session
            company_id: Company ID
            campaign_id: Campaign ID
        
        Returns:
            Campaign object
        
        Raises:
            ResourceNotFoundError: If campaign not found
            PermissionError: If campaign doesn't belong to company
        """
        
        campaign = db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        ).scalar_one_or_none()
        
        if not campaign:
            raise ResourceNotFoundError(f"Campaign {campaign_id} not found")
        
        if campaign.company_id != company_id:
            raise AppPermissionError("Campaign doesn't belong to your company")
        
        return campaign
    
    @staticmethod
    def list_campaigns(
        db: Session,
        company_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
        status: str = None,
    ) -> tuple[list[Campaign], int]:
        """
        List campaigns for a company.
        
        Args:
            db: Database session
            company_id: Company ID
            skip: Pagination offset
            limit: Pagination limit
            status: Filter by status (optional)
        
        Returns:
            Tuple of (campaigns list, total count)
        """
        
        query = select(Campaign).where(Campaign.company_id == company_id)
        
        if status:
            query = query.where(Campaign.status == status)
        
        # Get total count
        total = db.execute(
            select(func.count(Campaign.id)).where(Campaign.company_id == company_id)
        ).scalar()
        
        # Get paginated results
        campaigns = db.execute(
            query.order_by(Campaign.created_at.desc()).offset(skip).limit(limit)
        ).scalars().all()
        
        return campaigns, total
    
    @staticmethod
    def get_campaign_status(
        db: Session,
        company_id: uuid.UUID,
        campaign_id: uuid.UUID,
    ) -> dict:
        """
        Get campaign send status.
        
        Returns counts of sent/failed emails from send logs.
        
        Args:
            db: Database session
            company_id: Company ID
            campaign_id: Campaign ID
        
        Returns:
            Dict with status info
        
        Raises:
            ResourceNotFoundError: If campaign not found
            PermissionError: If campaign doesn't belong to company
        """
        
        campaign = db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        ).scalar_one_or_none()
        
        if not campaign:
            raise ResourceNotFoundError(f"Campaign {campaign_id} not found")
        
        if campaign.company_id != company_id:
            raise AppPermissionError("Campaign doesn't belong to your company")
        
        # Get send log stats
        sent_count = db.execute(
            select(func.count(CampaignSendLog.id)).where(
                and_(
                    CampaignSendLog.campaign_id == campaign_id,
                    CampaignSendLog.status == "sent",
                )
            )
        ).scalar()
        
        failed_count = db.execute(
            select(func.count(CampaignSendLog.id)).where(
                and_(
                    CampaignSendLog.campaign_id == campaign_id,
                    CampaignSendLog.status == "failed",
                )
            )
        ).scalar()
        
        total_recipients = db.execute(
            select(func.count(CampaignSendLog.id)).where(
                CampaignSendLog.campaign_id == campaign_id
            )
        ).scalar()
        
        return {
            "id": campaign.id,
            "status": campaign.status,
            "sent_count": sent_count,
            "failed_count": failed_count,
            "total_recipients": total_recipients,
            "scheduled_for": campaign.scheduled_for,
            "sent_at": campaign.sent_at,
        }

    @staticmethod
    def delete_campaign(
        db: Session,
        company_id: uuid.UUID,
        campaign_id: uuid.UUID,
    ) -> None:
        """
        Delete a campaign.
        
        Restrictions:
        - Can only delete campaigns in draft or scheduled status
        - Cannot delete campaigns that are sending or already sent
        - All campaign send logs will be cascade deleted
        
        Args:
            db: Database session
            company_id: Owner company ID
            campaign_id: Campaign ID to delete
            
        Raises:
            ResourceNotFoundError: If campaign not found
            AppPermissionError: If campaign doesn't belong to company or cannot be deleted
        """
        campaign = db.execute(
            select(Campaign).where(
                and_(
                    Campaign.id == campaign_id,
                    Campaign.company_id == company_id,
                )
            )
        ).scalar_one_or_none()
        
        if not campaign:
            raise ResourceNotFoundError(f"Campaign {campaign_id} not found")
        
        # Prevent deletion of campaigns that are sending or already sent
        if campaign.status in ["sending", "sent"]:
            raise AppPermissionError(
                f"Cannot delete campaign in '{campaign.status}' status. "
                f"Only draft and scheduled campaigns can be deleted."
            )
        
        db.delete(campaign)
        db.commit()
        
        logger.info(f"Campaign deleted: {campaign_id} (status: {campaign.status})")
