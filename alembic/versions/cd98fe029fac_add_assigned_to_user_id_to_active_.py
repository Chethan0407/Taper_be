"""add assigned_to_user_id to active_checklist_items

Revision ID: cd98fe029fac
Revises: 4e8942822bba
Create Date: 2025-07-10 00:45:23.456789

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'cd98fe029fac'
down_revision: Union[str, Sequence[str], None] = '4e8942822bba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('active_checklist_items', sa.Column('assigned_to_user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'active_checklist_items', 'users', ['assigned_to_user_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint(None, 'active_checklist_items', type_='foreignkey')
    op.drop_column('active_checklist_items', 'assigned_to_user_id')
