import uuid
import datetime
from sqlalchemy import String, TIMESTAMP, ForeignKey, CheckConstraint, func, Index, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CampaignSendLog(Base):
    """
    Tracks individual email send attempts for idempotency and debugging.
    
    Enables:
    - Per-email delivery tracking
    - Idempotent retries
    - SES bounce/complaint handling
    - Audit trail
    """
    __tablename__ = "campaign_send_logs"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','sending','sent','failed','bounced','complained')"
        ),
        Index("idx_campaign_send_logs_campaign_id", "campaign_id"),
        Index("idx_campaign_send_logs_email", "subscriber_email"),
        Index("idx_campaign_send_logs_status", "status"),
        Index("idx_campaign_send_logs_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    subscriber_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    # SES Message ID for tracking bounces/complaints
    ses_message_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True  # Ensure SES Message ID is unique
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
        index=True
    )

    # Error details if failed
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Additional metadata (SES response, retry count, etc.)
    extra_data: Mapped[dict] = mapped_column(
        JSONB,
        server_default="{}",
        nullable=False
    )

    # Timestamp when email was actually sent to SES
    sent_at: Mapped[datetime.datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
