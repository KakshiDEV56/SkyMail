"""Add campaign enhancements and send logs

Revision ID: 2_campaigns_enhancements
Revises: 46b6a5553332
Create Date: 2026-01-25 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2_campaigns_enhancements'
down_revision: Union[str, Sequence[str], None] = '46b6a5553332'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add campaign enhancements and send logs."""
    
    # Add new columns to campaigns table
    op.add_column('campaigns', sa.Column('sent_at', sa.TIMESTAMP(timezone=True), nullable=True))
    
    # Convert existing scheduled_for to timezone-aware if not already
    op.alter_column('campaigns', 'scheduled_for',
                    existing_type=sa.TIMESTAMP(),
                    type_=sa.TIMESTAMP(timezone=True),
                    nullable=True)
    
    # Convert created_at and updated_at to timezone-aware
    op.alter_column('campaigns', 'created_at',
                    existing_type=sa.TIMESTAMP(),
                    type_=sa.TIMESTAMP(timezone=True),
                    nullable=False,
                    server_default=sa.text('now()'))
    
    op.alter_column('campaigns', 'updated_at',
                    existing_type=sa.TIMESTAMP(),
                    type_=sa.TIMESTAMP(timezone=True),
                    nullable=False,
                    server_default=sa.text('now()'))
    
    # Make company_id explicitly NOT NULL
    op.alter_column('campaigns', 'company_id', nullable=False)
    
    # Make status NOT NULL with default
    op.alter_column('campaigns', 'status', nullable=False, server_default='draft')
    
    # Add indexes for performance
    op.create_index('idx_campaigns_company_id', 'campaigns', ['company_id'])
    op.create_index('idx_campaigns_status', 'campaigns', ['status'])
    op.create_index('idx_campaigns_scheduled_for', 'campaigns', ['scheduled_for'])
    
    # Create campaign_send_logs table
    op.create_table('campaign_send_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('campaign_id', sa.UUID(), nullable=False),
        sa.Column('subscriber_email', sa.String(length=255), nullable=False),
        sa.Column('ses_message_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('sent_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint("status IN ('pending','sending','sent','failed','bounced','complained')"),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ses_message_id', name='uq_ses_message_id')
    )
    op.create_index('idx_campaign_send_logs_campaign_id', 'campaign_send_logs', ['campaign_id'])
    op.create_index('idx_campaign_send_logs_email', 'campaign_send_logs', ['subscriber_email'])
    op.create_index('idx_campaign_send_logs_status', 'campaign_send_logs', ['status'])
    op.create_index('idx_campaign_send_logs_created_at', 'campaign_send_logs', ['created_at'])


def downgrade() -> None:
    """Downgrade schema."""
    
    # Drop campaign_send_logs table
    op.drop_index('idx_campaign_send_logs_created_at', table_name='campaign_send_logs')
    op.drop_index('idx_campaign_send_logs_status', table_name='campaign_send_logs')
    op.drop_index('idx_campaign_send_logs_email', table_name='campaign_send_logs')
    op.drop_index('idx_campaign_send_logs_campaign_id', table_name='campaign_send_logs')
    op.drop_table('campaign_send_logs')
    
    # Drop indexes from campaigns
    op.drop_index('idx_campaigns_scheduled_for', table_name='campaigns')
    op.drop_index('idx_campaigns_status', table_name='campaigns')
    op.drop_index('idx_campaigns_company_id', table_name='campaigns')
    
    # Revert column changes
    op.alter_column('campaigns', 'updated_at',
                    existing_type=sa.TIMESTAMP(timezone=True),
                    type_=sa.TIMESTAMP(),
                    nullable=False,
                    server_default=sa.text('now()'))
    
    op.alter_column('campaigns', 'created_at',
                    existing_type=sa.TIMESTAMP(timezone=True),
                    type_=sa.TIMESTAMP(),
                    nullable=False,
                    server_default=sa.text('now()'))
    
    op.alter_column('campaigns', 'scheduled_for',
                    existing_type=sa.TIMESTAMP(timezone=True),
                    type_=sa.TIMESTAMP(),
                    nullable=True)
    
    op.drop_column('campaigns', 'sent_at')
