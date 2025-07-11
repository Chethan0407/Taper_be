"""Add status to companies

Revision ID: d099d2f46013
Revises: 5ab445447de9
Create Date: 2025-07-12 02:36:30.937461

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd099d2f46013'
down_revision: Union[str, Sequence[str], None] = '5ab445447de9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('companies', sa.Column('status', sa.String(), nullable=True, server_default='Active'))

def downgrade() -> None:
    op.drop_column('companies', 'status')
