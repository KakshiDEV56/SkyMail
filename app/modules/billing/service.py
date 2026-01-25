"""
Billing service for handling Razorpay payments and premium subscriptions.
"""

import razorpay
import hmac
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Tuple, Optional
from sqlalchemy.orm import Session
from loguru import logger

from app.utils import constants
from app.modules.auth.model import Company
from app.modules.billing.model import Payment


class BillingService:
    """Service for managing premium subscriptions and payments."""
    
    # Premium subscription pricing
    PREMIUM_PRICE_AMOUNT = 1699.00  # ₹1699 INR (approx $20)
    PREMIUM_PRICE_PAISE = 169900  # In paise for Razorpay
    PREMIUM_DURATION_DAYS = 365  # 1 year
    
    # Initialize Razorpay client with validation
    if not constants.RAZORPAY_KEY_ID or not constants.RAZORPAY_SECRET_KEY:
        logger.error("Razorpay credentials not configured in environment variables")
        raise ValueError("Missing Razorpay API credentials (RAZORPAY_KEY_ID or RAZORPAY_SECRET_KEY)")
    
    razorpay_client = razorpay.Client(
        auth=(constants.RAZORPAY_KEY_ID, constants.RAZORPAY_SECRET_KEY)
    )
    
    @staticmethod
    def create_order(company_id: str, db: Session) -> Tuple[bool, dict]:
        """
        Create a Razorpay order for premium subscription.
        
        Args:
            company_id: UUID of the company
            db: Database session
            
        Returns:
            (success, response_dict)
        """
        try:
            # Verify company exists
            company = db.query(Company).filter(
                Company.id == uuid.UUID(company_id)
            ).first()
            
            if not company:
                return False, {
                    "error": "Company not found"
                }
            
            # Check if already premium
            if company.is_premium and company.subscription_end_date:
                if company.subscription_end_date > datetime.utcnow():
                    return False, {
                        "error": "Already have an active premium subscription",
                        "subscription_end_date": company.subscription_end_date.isoformat()
                    }
            
            # Create Razorpay order
            # Receipt must be under 40 characters - use first 8 chars of UUID + timestamp
            timestamp = int(datetime.utcnow().timestamp())
            receipt = f"prem_{str(company_id)[:8]}_{timestamp}"[:40]  # Ensure max 40 chars
            
            order_data = {
                "amount": BillingService.PREMIUM_PRICE_PAISE,  # Amount in paise
                "currency": "INR",
                "receipt": receipt,
                "notes": {
                    "company_id": str(company_id),
                    "plan": "premium",
                    "duration_days": str(BillingService.PREMIUM_DURATION_DAYS)
                }
            }
            
            razorpay_order = BillingService.razorpay_client.order.create(data=order_data)
            
            # Store pending payment record
            payment = Payment(
                id=uuid.uuid4(),
                company_id=uuid.UUID(company_id),
                razorpay_order_id=razorpay_order["id"],
                amount=BillingService.PREMIUM_PRICE_AMOUNT,
                currency="INR",
                subscription_plan="premium"
            )
            db.add(payment)
            db.commit()
            
            logger.info(
                f"Created Razorpay order {razorpay_order['id']} for company {company_id}. "
                f"Amount: {razorpay_order['amount']} paise"
            )
            
            return True, {
                "order_id": razorpay_order["id"],
                "amount": razorpay_order["amount"],  # Amount in paise
                "currency": razorpay_order["currency"],  # INR
                "key_id": constants.RAZORPAY_KEY_ID
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating Razorpay order: {str(e)}")
            return False, {
                "error": "Failed to create payment order",
                "details": str(e)
            }
    
    @staticmethod
    def verify_payment_signature(
        order_id: str,
        payment_id: str,
        signature: str
    ) -> bool:
        """
        Verify Razorpay payment signature using HMAC SHA256.
        
        Razorpay signature verification process:
        1. Concatenate: order_id|payment_id
        2. Generate HMAC SHA256 with secret key
        3. Compare with provided signature using constant-time comparison
        
        Args:
            order_id: Razorpay order ID
            payment_id: Razorpay payment ID
            signature: Razorpay signature from webhook/callback
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            if not constants.RAZORPAY_SECRET_KEY:
                logger.error("Razorpay secret key not configured")
                return False
            
            # Generate expected signature
            message = f"{order_id}|{payment_id}"
            expected_signature = hmac.new(
                constants.RAZORPAY_SECRET_KEY.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Use constant-time comparison to prevent timing attacks
            is_valid = hmac.compare_digest(expected_signature, signature)
            
            if not is_valid:
                logger.warning(
                    f"Invalid payment signature for order {order_id}. "
                    f"Expected: {expected_signature[:10]}..., Got: {signature[:10]}..."
                )
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying payment signature: {str(e)}", exc_info=True)
            return False
    
    @staticmethod
    def verify_and_activate_premium(
        company_id: str,
        order_id: str,
        payment_id: str,
        signature: str,
        db: Session
    ) -> Tuple[bool, dict]:
        """
        Verify payment and activate premium subscription.
        
        Args:
            company_id: UUID of the company
            order_id: Razorpay order ID
            payment_id: Razorpay payment ID
            signature: Razorpay signature
            db: Database session
            
        Returns:
            (success, response_dict)
        """
        try:
            # Verify signature
            if not BillingService.verify_payment_signature(order_id, payment_id, signature):
                logger.warning(f"Invalid payment signature for order {order_id}")
                return False, {
                    "success": False,
                    "message": "Payment verification failed: Invalid signature"
                }
            
            # Find payment record
            payment = db.query(Payment).filter(
                Payment.razorpay_order_id == order_id,
                Payment.company_id == uuid.UUID(company_id)
            ).first()
            
            if not payment:
                return False, {
                    "success": False,
                    "message": "Payment record not found"
                }
            
            # Check if already processed
            if payment.razorpay_payment_id:
                return False, {
                    "success": False,
                    "message": "Payment already processed"
                }
            
            # Update payment record
            payment.razorpay_payment_id = payment_id
            payment.razorpay_signature = signature
            
            # Calculate subscription end date
            subscription_end = datetime.utcnow() + timedelta(days=BillingService.PREMIUM_DURATION_DAYS)
            payment.valid_until = subscription_end
            
            # Update company to premium
            company = db.query(Company).filter(
                Company.id == uuid.UUID(company_id)
            ).first()
            
            if not company:
                db.rollback()
                return False, {
                    "success": False,
                    "message": "Company not found"
                }
            
            company.is_premium = True
            company.subscription_tier = "premium"
            company.subscription_end_date = subscription_end
            company.max_subscribers = 999999  # Unlimited for premium
            
            db.commit()
            
            logger.info(
                f"Premium activated for company {company_id}. "
                f"Valid until {subscription_end.isoformat()}"
            )
            
            return True, {
                "success": True,
                "message": "Premium subscription activated successfully!",
                "subscription_tier": "premium",
                "is_premium": True,
                "subscription_end_date": subscription_end
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error verifying payment: {str(e)}")
            return False, {
                "success": False,
                "message": "Failed to process payment verification",
                "details": str(e)
            }
    
    @staticmethod
    def get_payment_history(company_id: str, db: Session) -> Tuple[bool, dict]:
        """
        Get payment history for a company.
        
        Args:
            company_id: UUID of the company
            db: Database session
            
        Returns:
            (success, response_dict)
        """
        try:
            payments = db.query(Payment).filter(
                Payment.company_id == uuid.UUID(company_id)
            ).order_by(Payment.created_at.desc()).all()
            
            payment_list = [
                {
                    "id": str(payment.id),
                    "amount": float(payment.amount),
                    "currency": payment.currency,
                    "subscription_plan": payment.subscription_plan,
                    "razorpay_payment_id": payment.razorpay_payment_id,
                    "created_at": payment.created_at,
                    "valid_until": payment.valid_until
                }
                for payment in payments
            ]
            
            return True, {
                "payments": payment_list,
                "total": len(payment_list)
            }
            
        except Exception as e:
            logger.error(f"Error fetching payment history: {str(e)}")
            return False, {
                "error": "Failed to fetch payment history",
                "details": str(e)
            }
