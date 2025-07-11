"""fix checklist created_at default

Revision ID: 0f0a01876a3b
Revises: 384d8ac05c6a
Create Date: 2025-07-10 00:08:34.768999

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0f0a01876a3b'
down_revision: Union[str, Sequence[str], None] = '384d8ac05c6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Set created_at to now() for all existing rows with NULL
    op.execute("UPDATE checklists SET created_at = now() WHERE created_at IS NULL;")
    # Alter column to set NOT NULL and default
    op.alter_column('checklists', 'created_at',
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text('now()')
    )


def downgrade() -> None:
    op.alter_column('checklists', 'created_at',
        existing_type=sa.DateTime(timezone=True),
        nullable=True,
        server_default=None
    )
