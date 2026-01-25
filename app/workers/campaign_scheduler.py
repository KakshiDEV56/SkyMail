"""Campaign scheduler task - runs every minute to enqueue due campaigns."""

from sqlalchemy import select, and_, func
from loguru import logger

from app.celery_app import app
from app.database.database import SessionLocal
# Import all models with proper initialization order
from app.database.models import Campaign
from app.workers.campaign_send import send_campaign


@app.task(
    name="app.workers.campaign_scheduler.enqueue_due_campaigns",
    bind=True,
    queue="scheduled",
    priority=10,
    max_retries=3,
)
def enqueue_due_campaigns(self):
    """
    Scheduler task that runs every minute.
    
    Fetches all campaigns with status='scheduled' and scheduled_for <= now()
    Enqueues send_campaign task for each due campaign.
    
    🧠 MENTAL MODEL:
    - Scheduler NEVER sends emails directly
    - Database state drives execution
    - Each campaign gets its own send task
    - PostgreSQL handles time comparisons, not Python
    """
    db = SessionLocal()
    try:
        logger.info("🔍 Checking for due campaigns...")
        
        # Query for campaigns that are scheduled and due
        # Use func.now() so PostgreSQL does the time comparison
        query = select(Campaign).where(
            and_(
                Campaign.status == "scheduled",
                Campaign.scheduled_for <= func.now(),
            )
        )
        
        due_campaigns = db.execute(query).scalars().all()
        
        if not due_campaigns:
            logger.debug("✅ No campaigns due to send")
            return {
                "status": "success",
                "campaigns_enqueued": 0,
            }
        
        logger.info(f"📨 Found {len(due_campaigns)} campaigns due to send")
        
        enqueued_count = 0
        for campaign in due_campaigns:
            try:
                # Enqueue the send_campaign task
                send_campaign.apply_async(
                    args=[str(campaign.id)],
                    queue="campaigns",
                    priority=10,
                )
                enqueued_count += 1
                logger.info(
                    f"✅ Enqueued campaign {campaign.id} "
                    f"(Company: {campaign.company_id}, Name: {campaign.name})"
                )
            except Exception as e:
                logger.error(
                    f"❌ Failed to enqueue campaign {campaign.id}: {str(e)}"
                )
        
        return {
            "status": "success",
            "campaigns_enqueued": enqueued_count,
            "total_due": len(due_campaigns),
        }
    
    except Exception as exc:
        logger.error(f"❌ Scheduler task failed: {str(exc)}", exc_info=True)
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60)  # Retry after 60 seconds
    
    finally:
        db.close()
