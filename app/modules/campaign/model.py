import uuid
import datetime
from sqlalchemy import String, TIMESTAMP, ForeignKey,CheckConstraint, func, Index
from sqlalchemy.dialects.postgresql import UUID,JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

class Campaign(Base):
    """
    Campaign model for scheduling and tracking email campaigns.
    
    🧠 MENTAL MODEL:
    A campaign is a scheduled instruction, not an email.
    Database state drives execution — never time-based logic in API handlers.
    """
    __tablename__ = "campaigns"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft','scheduled','sending','sent','cancelled')"
        ),
        Index("idx_campaigns_company_id", "company_id"),
        Index("idx_campaigns_status", "status"),
        Index("idx_campaigns_scheduled_for", "scheduled_for"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    template_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("newsletter_templates.id", ondelete="CASCADE"),
        nullable=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)

    # Scheduled time in UTC
    scheduled_for: Mapped[datetime.datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True
    )
    
    # Timezone for display purposes (e.g., 'America/New_York')
    send_timezone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Status lifecycle: draft → scheduled → sending → sent OR cancelled
    status: Mapped[str] = mapped_column(
        String(20),
        default="draft",
        nullable=False,
        index=True
    )

    # Timestamp when campaign was fully sent
    sent_at: Mapped[datetime.datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    constants_values: Mapped[dict] = mapped_column(
        JSONB,
        server_default="{}",
        nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
