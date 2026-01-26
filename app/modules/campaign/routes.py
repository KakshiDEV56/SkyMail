"""Campaign API routes."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import uuid

from app.database.database import get_db
from app.modules.campaign.schemas import (
    CampaignCreateRequest,
    CampaignScheduleRequest,
    CampaignRescheduleRequest,
    CampaignResponse,
    CampaignListResponse,
    CampaignStatusResponse,
)
from app.modules.campaign.service import CampaignService
from app.modules.auth.routes import get_current_company
from app.utils.exceptions import (
    ResourceNotFoundError,
    ValidationError,
    PermissionError as AppPermissionError,
)


# Note: Pydantic (v2.12.5) automatically parses ISO-8601 datetime strings
# The service layer validates that scheduled_for is in the future


router = APIRouter(
    prefix="/api/campaigns",
    tags=["campaigns"],
)


@router.post("", response_model=CampaignResponse, status_code=201)
async def create_campaign(
    req: CampaignCreateRequest,
    db: Session = Depends(get_db),
    company_id: uuid.UUID = Depends(get_current_company),
):
    """
    Create a new campaign.
    
    - Campaign starts in 'draft' status
    - Template must belong to your company
    - constants_values must match template.constants exactly
    - scheduled_for must be UTC (format: 2026-01-25T17:30:00Z)
    """
    try:
        company_uuid = uuid.UUID(company_id) if isinstance(company_id, str) else company_id
        campaign = CampaignService.create_campaign(
            db=db,
            company_id=company_uuid,
            name=req.name,
            template_id=req.template_id,
            constants_values=req.constants_values,
            scheduled_for=req.scheduled_for,
            send_timezone=req.send_timezone,
        )
        return campaign
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{campaign_id}/schedule", response_model=CampaignResponse)
async def schedule_campaign(
    campaign_id: uuid.UUID,
    req: CampaignScheduleRequest,
    db: Session = Depends(get_db),
    company_id: uuid.UUID = Depends(get_current_company),
):
    """
    Schedule a campaign (draft to scheduled).
    
    Checks:
    - Campaign must be in draft status
    - scheduled_for must be in the future (UTC format: YYYY-MM-DDTHH:MM:SSZ)
    - Subscriber count must not exceed plan limit
    
    Once scheduled, the campaign will be picked up by Celery Beat scheduler.
    """
    try:
        company_uuid = uuid.UUID(company_id) if isinstance(company_id, str) else company_id
        campaign = CampaignService.schedule_campaign(
            db=db,
            company_id=company_uuid,
            campaign_id=campaign_id,
            scheduled_for=req.scheduled_for,
            send_timezone=req.send_timezone or "UTC",
        )
        return campaign
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AppPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/{campaign_id}/cancel", response_model=CampaignResponse)
async def cancel_campaign(
    campaign_id: uuid.UUID,
    db: Session = Depends(get_db),
    company_id: uuid.UUID = Depends(get_current_company),
):
    """
    Cancel a campaign.
    
    Can only cancel campaigns in draft or scheduled status.
    Once sending/sent, campaigns cannot be cancelled.
    """
    try:
        company_uuid = uuid.UUID(company_id) if isinstance(company_id, str) else company_id
        campaign = CampaignService.cancel_campaign(
            db=db,
            company_id=company_uuid,
            campaign_id=campaign_id,
        )
        return campaign
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AppPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.patch("/{campaign_id}/reschedule", response_model=CampaignResponse)
async def reschedule_campaign(
    campaign_id: uuid.UUID,
    request: CampaignRescheduleRequest,
    db: Session = Depends(get_db),
    company_id: uuid.UUID = Depends(get_current_company),
):
    """
    Reschedule a campaign to a new time.
    
    Can only reschedule campaigns in draft or scheduled status.
    Once sending/sent, campaigns cannot be rescheduled.
    
    The scheduled_for time must be in the future (UTC).
    Required format: ISO 8601 with Z suffix (e.g., 2026-01-25T17:30:00Z).
    """
    try:
        company_uuid = uuid.UUID(company_id) if isinstance(company_id, str) else company_id
        campaign = CampaignService.reschedule_campaign(
            db=db,
            company_id=company_uuid,
            campaign_id=campaign_id,
            scheduled_for=request.scheduled_for,
            send_timezone=request.send_timezone or "UTC",
        )
        return campaign
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AppPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: uuid.UUID,
    db: Session = Depends(get_db),
    company_id: uuid.UUID = Depends(get_current_company),
):
    """
    Get campaign details.
    """
    try:
        company_uuid = uuid.UUID(company_id) if isinstance(company_id, str) else company_id
        campaign = CampaignService.get_campaign(
            db=db,
            company_id=company_uuid,
            campaign_id=campaign_id,
        )
        return campaign
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AppPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("", response_model=CampaignListResponse)
async def list_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    db: Session = Depends(get_db),
    company_id: uuid.UUID = Depends(get_current_company),
):
    """
    List campaigns for your company.
    
    Optional filters:
    - status: Filter by campaign status (draft, scheduled, sending, sent, cancelled)
    """
    company_uuid = uuid.UUID(company_id) if isinstance(company_id, str) else company_id
    campaigns, total = CampaignService.list_campaigns(
        db=db,
        company_id=company_uuid,
        skip=skip,
        limit=limit,
        status=status,
    )
    
    return CampaignListResponse(
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        campaigns=campaigns,
    )


@router.get("/{campaign_id}/status", response_model=CampaignStatusResponse)
async def get_campaign_status(
    campaign_id: uuid.UUID,
    db: Session = Depends(get_db),
    company_id: uuid.UUID = Depends(get_current_company),
):
    """
    Get campaign delivery status.
    
    Returns:
    - sent_count: Number of emails successfully sent
    - failed_count: Number of emails that failed
    - total_recipients: Total emails in this campaign
    """
    try:
        company_uuid = uuid.UUID(company_id) if isinstance(company_id, str) else company_id
        status_info = CampaignService.get_campaign_status(
            db=db,
            company_id=company_uuid,
            campaign_id=campaign_id,
        )
        return status_info
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AppPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{campaign_id}", status_code=204)
async def delete_campaign(
    campaign_id: uuid.UUID,
    db: Session = Depends(get_db),
    company_id: uuid.UUID = Depends(get_current_company),
):
    """
    Delete a campaign.
    
    Restrictions:
    - Can only delete campaigns in draft or scheduled status
    - Cannot delete campaigns that are sending or already sent
    - All associated send logs will be deleted (cascade delete)
    """
    try:
        company_uuid = uuid.UUID(company_id) if isinstance(company_id, str) else company_id
        CampaignService.delete_campaign(
            db=db,
            company_id=company_uuid,
            campaign_id=campaign_id,
        )
        return None
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AppPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
