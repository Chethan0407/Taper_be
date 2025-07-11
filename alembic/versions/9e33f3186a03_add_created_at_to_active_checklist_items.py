"""Add created_at to active_checklist_items

Revision ID: 9e33f3186a03
Revises: cd98fe029fac
Create Date: 2025-07-12 01:34:31.598247

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '9e33f3186a03'
down_revision: Union[str, Sequence[str], None] = 'cd98fe029fac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('active_checklist_items', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))

def downgrade() -> None:
    op.drop_column('active_checklist_items', 'created_at')
