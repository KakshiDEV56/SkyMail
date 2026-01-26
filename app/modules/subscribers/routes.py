"""
Public subscription routes.

These routes are PUBLIC - no authentication required.
They handle newsletter subscriptions from company websites.
"""

from fastapi import APIRouter, Depends, Header, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from loguru import logger

from app.database.database import get_db
from app.modules.subscribers.service import SubscriptionService
from app.modules.subscribers.schemas import (
    SubscribeRequest,
    SubscribeResponse,
    UnsubscribeRequest,
    UnsubscribeResponse,
)


# Public router (no authentication)
public_router = APIRouter(
    prefix="/public",
    tags=["Public Subscriptions"]
)


@public_router.post(
    "/companies/{company_id}/subscribe",
    response_model=SubscribeResponse,
    response_model_exclude_none=True,
    status_code=200,
    summary="Subscribe to company newsletter",
    description="Public endpoint for newsletter subscriptions. No authentication required. "
                "Origin header is validated against company website URL.",
)
async def subscribe_to_newsletter(
    company_id: str,
    request: SubscribeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    origin: str = Header(None, description="Request Origin header")
) -> SubscribeResponse:
    """
    Subscribe an email to a company's newsletter.
    
    **Validations:**
    - Email format validation
    - Company existence check
    - Origin header validation (must match company website)
    - Duplicate prevention (UNIQUE constraint)
    - Free tier subscriber limit (max 250)
    
    **Response Codes:**
    - 200: Successfully subscribed
    - 400: Invalid input
    - 404: Company not found
    - 403: Origin not allowed or limit reached
    
    **Example:**
    ```
    POST /public/companies/123e4567-e89b-12d3-a456-426614174000/subscribe
    Content-Type: application/json
    Origin: https://company-website.com
    
    {
        "email": "user@gmail.com"
    }
    ```
    """
    # Validate company_id format
    try:
        import uuid
        uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid company ID format"
        )
    
    # Call subscription service
    success, response = await SubscriptionService.subscribe(
        company_id=company_id,
        email=request.email,
        origin=origin,
        db=db,
        background_tasks=background_tasks
    )
    
    # Handle responses
    if success:
        if response.get("status") == "error":
            # Handle errors
            code = response.get("code", "unknown_error")
            if code == "company_not_found":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=response.get("message")
                )
            elif code == "invalid_origin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=response.get("message")
                )
            elif code == "upgrade_required":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "upgrade_required",
                        "message": response.get("message"),
                        "max_subscribers": response.get("max_subscribers"),
                        "current_subscribers": response.get("current_subscribers")
                    }
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=response.get("message")
                )
        
        # Success case
        return SubscribeResponse(**response)
    else:
        # Service error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process subscription"
        )


@public_router.post(
    "/companies/{company_id}/unsubscribe",
    response_model=UnsubscribeResponse,
    response_model_exclude_none=True,
    status_code=200,
    summary="Unsubscribe from company newsletter",
    description="Public endpoint for newsletter unsubscriptions. No authentication required.",
)
async def unsubscribe_from_newsletter(
    company_id: str,
    request: UnsubscribeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> UnsubscribeResponse:
    """
    Unsubscribe an email from a company's newsletter.
    
    **Note:** Unsubscribed users can re-subscribe later.
    
    **Response Codes:**
    - 200: Successfully unsubscribed
    - 400: Invalid input
    - 404: Subscriber not found
    
    **Example:**
    ```
    POST /public/companies/123e4567-e89b-12d3-a456-426614174000/unsubscribe
    Content-Type: application/json
    
    {
        "email": "user@gmail.com"
    }
    ```
    """
    # Validate company_id format
    try:
        import uuid
        uuid.UUID(company_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid company ID format"
        )
    
    # Call subscription service
    success, response = SubscriptionService.unsubscribe(
        company_id=company_id,
        email=request.email,
        db=db,
        background_tasks=background_tasks
    )
    
    # Handle responses
    if success:
        if response.get("status") == "error":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=response.get("message")
            )
        
        # Success case
        return UnsubscribeResponse(**response)
    else:
        # Service error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process unsubscription"
        )


# ==================== PROTECTED ROUTES (Company Access) ====================

from app.modules.auth.routes import get_current_company

# Protected router for company-specific subscriber management
protected_router = APIRouter(
    prefix="/api/subscribers",
    tags=["Subscriber Management"]
)


@protected_router.get(
    "/stats",
    status_code=200,
    summary="Get subscriber statistics",
    description="Get subscriber count and statistics for the authenticated company."
)
async def get_subscriber_stats(
    company_id: str = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """
    Get subscriber statistics for the company.
    
    Returns:
    - Total subscriber count
    - Active subscribers
    - Subscription tier
    - Max subscribers allowed
    """
    from app.modules.auth.model import Company
    import uuid
    
    try:
        company = db.query(Company).filter(
            Company.id == uuid.UUID(company_id)
        ).first()
        
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Count active subscribers
        from app.modules.subscribers.model import Subscriber
        active_count = db.query(Subscriber).filter(
            Subscriber.company_id == uuid.UUID(company_id),
            Subscriber.status == "subscribed"
        ).count()
        
        return {
            "company_id": str(company.id),
            "company_name": company.company_name,
            "total_subscribers": company.subscriber_count,
            "active_subscribers": active_count,
            "subscription_tier": company.subscription_tier,
            "is_premium": company.is_premium,
            "max_subscribers": company.max_subscribers,
            "percentage_used": round((company.subscriber_count / company.max_subscribers * 100), 2) if company.max_subscribers > 0 else 0
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid company ID"
        )
    except Exception as e:
        logger.error(f"Error fetching subscriber stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subscriber statistics"
        )


@protected_router.get(
    "",
    status_code=200,
    summary="List company subscribers",
    description="Get paginated list of subscribers for the authenticated company with optional search"
)
async def list_subscribers(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    email: str = Query(None),
    company_id: str = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """
    List all subscribers for a company with pagination and optional search.
    
    Query Parameters:
    - page: Page number (default: 1)
    - limit: Items per page (default: 20, max: 100)
    - email: Optional email search filter
    
    Returns:
    - subscribers: List of subscriber objects
    - total: Total subscriber count
    - page: Current page number
    - page_size: Items per page
    """
    from app.modules.subscribers.model import Subscriber
    import uuid
    
    try:
        # Validate pagination
        page = max(1, page)
        limit = min(100, max(1, limit))
        skip = (page - 1) * limit
        
        # Build query
        query = db.query(Subscriber).filter(
            Subscriber.company_id == uuid.UUID(company_id)
        )
        
        # Apply email filter if provided
        if email:
            query = query.filter(
                Subscriber.subscriber_email.ilike(f"%{email}%")
            )
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        subscribers = query.order_by(
            Subscriber.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return {
            "subscribers": [
                {
                    "id": str(sub.id),
                    "email": sub.subscriber_email,
                    "is_subscribed": sub.status == "subscribed",
                    "subscribed_at": sub.created_at.isoformat(),
                    "unsubscribed_at": None  # Could add unsubscribe timestamp if needed
                }
                for sub in subscribers
            ],
            "total": total,
            "page": page,
            "page_size": limit
        }
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid company ID"
        )
    except Exception as e:
        logger.error(f"Error listing subscribers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list subscribers"
        )


@protected_router.delete(
    "/{subscriber_id}",
    status_code=200,
    summary="Delete a subscriber",
    description="Delete a specific subscriber from the company's list"
)
async def delete_subscriber(
    subscriber_id: str,
    company_id: str = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """
    Delete a subscriber by ID.
    
    Parameters:
    - subscriber_id: UUID of the subscriber to delete
    
    Returns:
    - message: Success message
    """
    from app.modules.subscribers.model import Subscriber
    import uuid
    
    try:
        # Verify subscriber exists and belongs to the company
        subscriber = db.query(Subscriber).filter(
            Subscriber.id == uuid.UUID(subscriber_id),
            Subscriber.company_id == uuid.UUID(company_id)
        ).first()
        
        if not subscriber:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscriber not found"
            )
        
        # Delete the subscriber
        db.delete(subscriber)
        db.commit()
        
        return {
            "message": "Subscriber deleted successfully",
            "subscriber_id": subscriber_id
        }
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subscriber ID or company ID"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting subscriber: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete subscriber"
        )
