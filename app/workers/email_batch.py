"""Email batch sending worker with AWS SES integration."""

import boto3
from datetime import datetime, timezone
import uuid
from sqlalchemy import select, insert
from loguru import logger
from botocore.exceptions import ClientError

from app.celery_app import app
from app.database.database import SessionLocal
# Import all models with proper initialization order
from app.database.models import Campaign, CampaignSendLog
from app.modules.newsletters.newsletter_templates.model import NewsletterTemplate
from app.utils import constants


# Initialize SES client
ses_client = boto3.client(
    "ses",
    region_name=constants.AWS_SES_REGION,
    aws_access_key_id=constants.AWS_SES_ACCESS_KEY_ID,
    aws_secret_access_key=constants.AWS_SES_SECRET_ACCESS_KEY,
)


@app.task(
    name="app.workers.email_batch.send_campaign_batch",
    bind=True,
    queue="email_batches",
    max_retries=5,
    default_retry_delay=30,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def send_campaign_batch(self, campaign_id: str, subscriber_emails: list):
    """
    Send emails to a batch of subscribers using AWS SES.
    
    🚫 CRITICAL CONSTRAINT:
    Must NOT update campaign status. Campaign status is managed by send_campaign task.
    
    Responsibilities:
    1. Render template with variables
    2. Send via AWS SES
    3. Log delivery status per email
    4. Handle SES errors (throttling, bounces, etc.)
    5. Track via CampaignSendLog for idempotency
    
    Args:
        campaign_id: UUID of campaign
        subscriber_emails: List of email addresses to send to
    """
    db = SessionLocal()
    try:
        campaign_id_obj = uuid.UUID(campaign_id)
        
        logger.info(
            f"📧 Starting batch send for campaign {campaign_id} "
            f"({len(subscriber_emails)} emails)"
        )
        
        # ======================== FETCH CAMPAIGN & TEMPLATE ========================
        
        campaign = db.execute(
            select(Campaign).where(Campaign.id == campaign_id_obj)
        ).scalar_one_or_none()
        
        if not campaign:
            logger.error(f"❌ Campaign {campaign_id} not found")
            return {"status": "error", "reason": "campaign_not_found"}
        
        # Fetch template
        template = None
        if campaign.template_id:
            template = db.execute(
                select(NewsletterTemplate).where(
                    NewsletterTemplate.id == campaign.template_id
                )
            ).scalar_one_or_none()
        
        if not template:
            logger.error(f"❌ Template {campaign.template_id} not found")
            return {"status": "error", "reason": "template_not_found"}
        
        logger.info(f"📄 Using template: {template.name}")
        
        # ======================== FETCH COMPANY DATA ========================
        
        from app.modules.auth.model import Company
        
        company = db.execute(
            select(Company).where(Company.id == campaign.company_id)
        ).scalar_one_or_none()
        
        if not company:
            logger.error(f"❌ Company {campaign.company_id} not found")
            return {"status": "error", "reason": "company_not_found"}
        
        # ======================== FETCH TEMPLATE ASSETS ========================
        
        from app.modules.newsletters.template_assets.model import TemplateAsset
        
        template_assets = db.execute(
            select(TemplateAsset).where(
                (TemplateAsset.template_id == campaign.template_id)
                & (TemplateAsset.company_id == campaign.company_id)
            )
        ).scalars().all()
        
        # Build template_asset string (comma-separated URLs)
        template_asset_urls = ",".join([asset.file_url for asset in template_assets]) if template_assets else ""
        
        logger.debug(f"📦 Found {len(template_assets)} template assets")
        
        # ======================== PREPARE EMAIL DETAILS ========================
        
        from_email = constants.AWS_SES_SENDER_EMAIL or constants.MAIL_FROM
        campaign_subject = campaign.subject or template.subject
        template_html = template.html_content
        template_text = template.text_content
        
        if not from_email:
            logger.error("❌ AWS_SES_SENDER_EMAIL not configured")
            return {"status": "error", "reason": "sender_email_not_configured"}
        
        # ======================== SEND EMAILS IN BATCH ========================
        
        sent_count = 0
        failed_count = 0
        
        for email in subscriber_emails:
            try:
                logger.debug(f"📤 Sending to {email}")
                
                # Check if already sent (idempotency)
                existing_log = db.execute(
                    select(CampaignSendLog).where(
                        (CampaignSendLog.campaign_id == campaign_id_obj)
                        & (CampaignSendLog.subscriber_email == email)
                    )
                ).scalar_one_or_none()
                
                if existing_log and existing_log.status == "sent":
                    logger.debug(f"⏭️  Email already sent to {email}, skipping")
                    sent_count += 1
                    continue
                
                # ======================== FETCH SUBSCRIBER DATA ========================
                
                from app.modules.subscribers.model import Subscriber
                
                subscriber = db.execute(
                    select(Subscriber).where(
                        (Subscriber.company_id == campaign.company_id)
                        & (Subscriber.subscriber_email == email)
                    )
                ).scalar_one_or_none()
                
                # ======================== BUILD RENDER CONTEXT ========================
                # Merge system variables (from DB) + campaign constants (manual values) + template assets
                
                render_context = {
                    # System variables (auto-resolved)
                    "company_name": company.company_name,
                    "website_url": company.website_url or "",
                    "subscriber_email": email,
                    "subscriber_username": subscriber.subscriber_name if subscriber else email.split("@")[0],
                    "template_asset": template_asset_urls,
                    # Campaign constants (manual values provided at creation)
                    **(campaign.constants_values or {})
                }
                
                logger.debug(f"🔍 Render context: {render_context}")
                
                # ======================== RENDER TEMPLATE ========================
                
                rendered_subject = campaign_subject
                rendered_html = template_html
                rendered_text = template_text if template_text else ""
                
                # Replace all {{variable_name}} placeholders
                for key, value in render_context.items():
                    placeholder = f"{{{{{key}}}}}"
                    rendered_subject = rendered_subject.replace(placeholder, str(value))
                    rendered_html = rendered_html.replace(placeholder, str(value))
                    rendered_text = rendered_text.replace(placeholder, str(value))
                
                # Check for unresolved variables
                import re
                unresolved = re.findall(r"\{\{(\w+)\}\}", rendered_html)
                if unresolved:
                    logger.warning(f"⚠️ Unresolved variables in template: {unresolved}")
                
                logger.info(f"✅ Template rendered for {email}")
                
                # Create or update send log
                send_log_id = existing_log.id if existing_log else uuid.uuid4()
                
                # Send via SES
                response = ses_client.send_email(
                    Source=from_email,
                    Destination={"ToAddresses": [email]},
                    Message={
                        "Subject": {"Data": rendered_subject, "Charset": "UTF-8"},
                        "Body": {
                            "Html": {"Data": rendered_html, "Charset": "UTF-8"},
                        },
                    },
                )
                
                ses_message_id = response["MessageId"]
                
                logger.debug(f"✅ Email sent to {email} (SES ID: {ses_message_id})")
                
                # Create or update send log
                if existing_log:
                    # Update existing log
                    existing_log.status = "sent"
                    existing_log.ses_message_id = ses_message_id
                    existing_log.sent_at = datetime.now(timezone.utc)
                    existing_log.error_message = None
                    db.merge(existing_log)
                else:
                    # Create new log
                    send_log = CampaignSendLog(
                        id=send_log_id,
                        campaign_id=campaign_id_obj,
                        subscriber_email=email,
                        ses_message_id=ses_message_id,
                        status="sent",
                        sent_at=datetime.now(timezone.utc),
                        metadata={"batch_size": len(subscriber_emails)},
                    )
                    db.add(send_log)
                
                sent_count += 1
            
            except ClientError as ses_error:
                error_code = ses_error.response["Error"]["Code"]
                error_msg = ses_error.response["Error"]["Message"]
                
                logger.error(f"❌ SES error for {email}: {error_code} - {error_msg}")
                
                # Update or create send log with error
                if existing_log:
                    existing_log.status = "failed"
                    existing_log.error_message = f"{error_code}: {error_msg}"
                    db.merge(existing_log)
                else:
                    send_log = CampaignSendLog(
                        id=uuid.uuid4(),
                        campaign_id=campaign_id_obj,
                        subscriber_email=email,
                        status="failed",
                        error_message=f"{error_code}: {error_msg}",
                        metadata={
                            "error_code": error_code,
                            "batch_size": len(subscriber_emails),
                        },
                    )
                    db.add(send_log)
                
                failed_count += 1
                
                # Handle specific SES errors
                if error_code == "MessageRejected":
                    logger.warning(f"⚠️ Message rejected for {email}, skipping")
                elif error_code == "Throttling":
                    logger.warning(f"⏱️ SES throttled, retrying batch in 30 seconds")
                    db.commit()
                    raise self.retry(countdown=30)
            
            except Exception as exc:
                logger.error(f"❌ Unexpected error sending to {email}: {str(exc)}")
                
                # Create send log for failed email
                send_log = CampaignSendLog(
                    id=uuid.uuid4(),
                    campaign_id=campaign_id_obj,
                    subscriber_email=email,
                    status="failed",
                    error_message=str(exc),
                    metadata={"batch_size": len(subscriber_emails)},
                )
                db.add(send_log)
                failed_count += 1
        
        # ======================== COMMIT SEND LOGS ========================
        
        db.commit()
        
        logger.info(
            f"✅ Batch complete: {sent_count} sent, {failed_count} failed "
            f"(Campaign: {campaign_id})"
        )
        
        return {
            "status": "success" if failed_count == 0 else "partial",
            "campaign_id": campaign_id,
            "sent_count": sent_count,
            "failed_count": failed_count,
            "total": len(subscriber_emails),
        }
    
    except Exception as exc:
        logger.error(f"❌ Batch send failed: {str(exc)}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)
    
    finally:
        db.close()
