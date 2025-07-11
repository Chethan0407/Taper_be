"""Add approved_by and rejected_by to specifications

Revision ID: 5ab445447de9
Revises: 9e33f3186a03
Create Date: 2025-07-12 01:44:50.878884

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '5ab445447de9'
down_revision: Union[str, Sequence[str], None] = '9e33f3186a03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('specifications', sa.Column('approved_by', sa.String(), nullable=True))
    op.add_column('specifications', sa.Column('rejected_by', sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column('specifications', 'approved_by')
    op.drop_column('specifications', 'rejected_by')
