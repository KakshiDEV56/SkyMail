"""
Billing routes for premium subscription management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.modules.auth.routes import get_current_company
from app.modules.billing.schemas import (
    CreateOrderRequest,
    CreateOrderResponse,
    VerifyPaymentRequest,
    VerifyPaymentResponse,
    PaymentHistoryResponse
)
from app.modules.billing.service import BillingService


router = APIRouter(
    prefix="/api/billing",
    tags=["Billing & Subscriptions"]
)


@router.post(
    "/create-order",
    response_model=CreateOrderResponse,
    status_code=200,
    summary="Create Razorpay order for premium subscription",
    description="Create a Razorpay order to purchase premium subscription (₹1699 INR for 1 year)."
)
async def create_premium_order(
    request: CreateOrderRequest,
    company_id: str = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """
    Create a Razorpay order for premium subscription.
    
    **Premium Benefits:**
    - Unlimited subscribers (vs 250 for free tier)
    - Priority support
    - Advanced analytics
    - Custom templates
    
    **Pricing:** ₹1699 INR for 1 year
    
    **Flow:**
    1. Call this endpoint to create an order
    2. Use the returned `order_id` and `key_id` with Razorpay frontend SDK
    3. After payment, call `/verify-payment` with payment details
    """
    success, response = BillingService.create_order(company_id, db)
    
    if not success:
        error_msg = response.get("error", "Failed to create order")
        details = response.get("details", "")
        if details:
            error_msg = f"{error_msg}: {details}"
            
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    return CreateOrderResponse(**response)


@router.post(
    "/verify-payment",
    response_model=VerifyPaymentResponse,
    status_code=200,
    summary="Verify payment and activate premium",
    description="Verify Razorpay payment signature and activate premium subscription."
)
async def verify_payment(
    request: VerifyPaymentRequest,
    company_id: str = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """
    Verify Razorpay payment and activate premium subscription.
    
    **After successful verification:**
    - Company is upgraded to premium tier
    - Subscriber limit increased to unlimited
    - Subscription valid for 1 year
    
    **Required fields:**
    - `razorpay_order_id`: From create-order response
    - `razorpay_payment_id`: From Razorpay payment success callback
    - `razorpay_signature`: From Razorpay payment success callback
    """
    success, response = BillingService.verify_and_activate_premium(
        company_id=company_id,
        order_id=request.razorpay_order_id,
        payment_id=request.razorpay_payment_id,
        signature=request.razorpay_signature,
        db=db
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response.get("message", "Payment verification failed")
        )
    
    return VerifyPaymentResponse(**response)


@router.get(
    "/payment-history",
    response_model=PaymentHistoryResponse,
    status_code=200,
    summary="Get payment history",
    description="Retrieve all payment records for the authenticated company."
)
async def get_payment_history(
    company_id: str = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """
    Get payment history for the company.
    
    Returns all payment records including:
    - Payment amount and currency
    - Subscription plan
    - Payment date
    - Validity period
    """
    success, response = BillingService.get_payment_history(company_id, db)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response.get("error", "Failed to fetch payment history")
        )
    
    return PaymentHistoryResponse(**response)


@router.get(
    "/subscription-status",
    status_code=200,
    summary="Get current subscription status",
    description="Get current subscription tier and status for the company."
)
async def get_subscription_status(
    company_id: str = Depends(get_current_company),
    db: Session = Depends(get_db)
):
    """
    Get current subscription status.
    
    Returns:
    - Current tier (free/premium)
    - Premium status
    - Subscription end date (if premium)
    - Max subscribers allowed
    """
    from app.modules.auth.model import Company
    import uuid
    
    company = db.query(Company).filter(
        Company.id == uuid.UUID(company_id)
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return {
        "company_id": str(company.id),
        "subscription_tier": company.subscription_tier,
        "is_premium": company.is_premium,
        "subscription_end_date": company.subscription_end_date,
        "max_subscribers": company.max_subscribers,
        "current_subscribers": company.subscriber_count
    }
