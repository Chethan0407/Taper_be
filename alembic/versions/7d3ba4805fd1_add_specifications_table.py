"""add specifications table

Revision ID: 7d3ba4805fd1
Revises: 05d519a622c1
Create Date: 2025-07-09 22:44:52.200791

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7d3ba4805fd1'
down_revision: Union[str, Sequence[str], None] = '05d519a622c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Only create the specifications table
    op.create_table(
        'specifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('file_name', sa.String(), nullable=False),
        sa.Column('mime_type', sa.String(), nullable=False),
        sa.Column('uploaded_by', sa.String(), nullable=False),
        sa.Column('uploaded_on', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='Pending'),
        sa.Column('assigned_to', sa.String(), nullable=True),
        sa.Column('file_path', sa.String(), nullable=False),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # Only drop the specifications table
    op.drop_table('specifications')
    # ### end Alembic commands ###
