import uuid
import datetime
from sqlalchemy import String, TIMESTAMP, ForeignKey, UniqueConstraint, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

class Subscriber(Base):
    """
    Newsletter subscriber model.
    
    Represents an anonymous user subscribed to a company's newsletter.
    Email is the primary identifier for subscribers.
    """
    __tablename__ = "subscribers"
    __table_args__ = (
        UniqueConstraint("company_id", "email", name="uq_subscriber_company_email"),
        Index("idx_subscribers_company_id", "company_id"),
        Index("idx_subscribers_email", "email"),
        Index("idx_subscribers_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        index=True
    )

    # Email normalized to lowercase
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Subscription status: 'subscribed' or 'unsubscribed'
    status: Mapped[str] = mapped_column(String(20), default="subscribed", nullable=False)

    # Origin from which subscription was made
    source_origin: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
