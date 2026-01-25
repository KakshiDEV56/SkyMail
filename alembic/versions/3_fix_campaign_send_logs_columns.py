"""Fix campaign_send_logs columns to match model

Revision ID: 3_fix_campaign_send_logs_columns
Revises: 2_campaigns_enhancements
Create Date: 2026-01-25 23:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3_fix_campaign_send_logs_columns'
down_revision: Union[str, Sequence[str], None] = '2_campaigns_enhancements'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - fix campaign_send_logs columns."""
    
    # Rename send_metadata to extra_data to match model definition
    op.alter_column('campaign_send_logs', 'send_metadata',
                    new_column_name='extra_data')


def downgrade() -> None:
    """Downgrade schema."""
    
    # Rename extra_data back to send_metadata
    op.alter_column('campaign_send_logs', 'extra_data',
                    new_column_name='send_metadata')
