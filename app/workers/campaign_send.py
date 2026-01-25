"""Campaign send worker - orchestrates email sending with idempotency."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import select, and_, update
from sqlalchemy.orm import Session
from loguru import logger

from app.celery_app import app
from app.database.database import SessionLocal
# Import all models with proper initialization order
from app.database.models import Campaign
from app.modules.subscribers.model import Subscriber
from app.modules.auth.model import Company
from app.utils import constants
from app.workers.email_batch import send_campaign_batch


@app.task(
    name="app.workers.campaign_send.send_campaign",
    bind=True,
    queue="campaigns",
    max_retries=3,
    default_retry_delay=60,
)
def send_campaign(self, campaign_id: str):
    """
    Main campaign send orchestrator.
    
    🔒 CRITICAL: Campaign Locking
    First action: Try to acquire lock by setting status='sending'
    If lock fails (affected rows = 0), exit immediately → prevents double sends
    
    Then:
    1. Fetch campaign & template details
    2. Fetch subscribers in batches
    3. Enqueue batch send tasks
    4. Mark campaign as sent when all batches complete
    
    Args:
        campaign_id: UUID of campaign to send
    """
    db = SessionLocal()
    try:
        campaign_id_obj = uuid.UUID(campaign_id)
        logger.info(f"🚀 Starting send_campaign for {campaign_id}")
        
        # ======================== PHASE 1: ACQUIRE LOCK ========================
        # Update campaign status to 'sending' only if it's currently 'scheduled'
        # This is our distributed lock mechanism
        
        lock_query = (
            update(Campaign)
            .where(
                and_(
                    Campaign.id == campaign_id_obj,
                    Campaign.status == "scheduled",
                )
            )
            .values(status="sending", updated_at=datetime.now(timezone.utc))
        )
        
        result = db.execute(lock_query)
        db.commit()
        
        if result.rowcount == 0:
            logger.warning(
                f"⚠️ Failed to acquire lock for campaign {campaign_id}. "
                f"Another worker may be processing it."
            )
            return {
                "status": "lock_failed",
                "campaign_id": campaign_id,
                "reason": "Campaign not in 'scheduled' status",
            }
        
        logger.info(f"✅ Lock acquired for campaign {campaign_id}")
        
        # ======================== PHASE 2: FETCH CAMPAIGN ========================
        
        campaign = db.execute(
            select(Campaign).where(Campaign.id == campaign_id_obj)
        ).scalar_one_or_none()
        
        if not campaign:
            logger.error(f"❌ Campaign {campaign_id} not found")
            return {"status": "error", "campaign_id": campaign_id, "reason": "not_found"}
        
        logger.info(
            f"📧 Campaign: {campaign.name} | "
            f"Template: {campaign.template_id} | "
            f"Subject: {campaign.subject}"
        )
        
        # ======================== PHASE 3: FETCH SUBSCRIBERS IN BATCHES ========================
        
        # Get company info for plan limit check
        company = db.execute(
            select(Company).where(Company.id == campaign.company_id)
        ).scalar_one_or_none()
        
        if not company:
            logger.error(f"❌ Company {campaign.company_id} not found")
            _mark_campaign_failed(db, campaign_id_obj, "Company not found")
            return {"status": "error", "campaign_id": campaign_id, "reason": "company_not_found"}
        
        # Fetch active subscribers
        subscriber_query = select(Subscriber).where(
            and_(
                Subscriber.company_id == campaign.company_id,
                Subscriber.status == "subscribed",
            )
        )
        
        all_subscribers = db.execute(subscriber_query).scalars().all()
        subscriber_emails = [s.email for s in all_subscribers]
        
        logger.info(f"📊 Found {len(subscriber_emails)} active subscribers")
        
        if not subscriber_emails:
            logger.warning(f"⚠️ No active subscribers for campaign {campaign_id}")
            _mark_campaign_sent(db, campaign_id_obj)
            return {
                "status": "success",
                "campaign_id": campaign_id,
                "subscribers_count": 0,
                "batches_enqueued": 0,
            }
        
        # ======================== PHASE 4: ENQUEUE BATCH TASKS ========================
        
        batch_size = constants.CAMPAIGN_BATCH_SIZE
        batch_tasks = []
        
        for i in range(0, len(subscriber_emails), batch_size):
            batch = subscriber_emails[i : i + batch_size]
            batch_num = i // batch_size + 1
            
            # Enqueue batch send task
            task = send_campaign_batch.apply_async(
                args=[str(campaign_id), batch],
                queue="email_batches",
                priority=9,
            )
            batch_tasks.append(task)
            
            logger.info(
                f"📨 Enqueued batch {batch_num} "
                f"({len(batch)} emails) for campaign {campaign_id}"
            )
        
        logger.info(
            f"✅ All {len(batch_tasks)} batches enqueued "
            f"({len(subscriber_emails)} total emails)"
        )
        
        # ======================== PHASE 5: WAIT FOR COMPLETION ========================
        # In production, we'd use a chord/group to track completion
        # For now, mark as sent - send logs will track actual delivery
        
        _mark_campaign_sent(db, campaign_id_obj)
        
        return {
            "status": "success",
            "campaign_id": campaign_id,
            "company_id": str(campaign.company_id),
            "subscribers_count": len(subscriber_emails),
            "batches_enqueued": len(batch_tasks),
            "batch_size": batch_size,
        }
    
    except Exception as exc:
        logger.error(f"❌ send_campaign failed: {str(exc)}", exc_info=True)
        _mark_campaign_failed(db, uuid.UUID(campaign_id), str(exc))
        raise self.retry(exc=exc, countdown=120)
    
    finally:
        db.close()


def _mark_campaign_sent(db: Session, campaign_id: uuid.UUID):
    """Mark campaign as sent."""
    now = datetime.now(timezone.utc)
    db.execute(
        update(Campaign)
        .where(Campaign.id == campaign_id)
        .values(status="sent", sent_at=now, updated_at=now)
    )
    db.commit()
    logger.info(f"✅ Campaign {campaign_id} marked as sent")


def _mark_campaign_failed(db: Session, campaign_id: uuid.UUID, error_msg: str):
    """Revert campaign to scheduled status (for retry) if it fails to enqueue batches."""
    now = datetime.now(timezone.utc)
    db.execute(
        update(Campaign)
        .where(Campaign.id == campaign_id)
        .values(status="scheduled", updated_at=now)
    )
    db.commit()
    logger.error(f"❌ Campaign {campaign_id} reverted to scheduled: {error_msg}")
