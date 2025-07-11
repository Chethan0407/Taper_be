"""add checklist template and active checklist models

Revision ID: 4e8942822bba
Revises: 0f0a01876a3b
Create Date: 2025-07-10 00:23:14.110455

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '4e8942822bba'
down_revision: Union[str, Sequence[str], None] = '0f0a01876a3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'checklist_templates',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
    )
    op.create_table(
        'checklist_items',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('template_id', sa.Integer(), sa.ForeignKey('checklist_templates.id'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
    )
    op.create_table(
        'active_checklists',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('template_id', sa.Integer(), sa.ForeignKey('checklist_templates.id'), nullable=False),
        sa.Column('linked_spec_id', sa.String(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('status', sa.String(), default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
    )
    op.create_table(
        'active_checklist_items',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('checklist_id', sa.Integer(), sa.ForeignKey('active_checklists.id'), nullable=False),
        sa.Column('template_item_id', sa.Integer(), sa.ForeignKey('checklist_items.id'), nullable=False),
        sa.Column('status', sa.String(), default='pending'),
        sa.Column('comment', sa.String(), nullable=True),
        sa.Column('evidence_file_path', sa.String(), nullable=True),
        sa.Column('assigned_to', sa.String(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
    )

def downgrade() -> None:
    op.drop_table('active_checklist_items')
    op.drop_table('active_checklists')
    op.drop_table('checklist_items')
    op.drop_table('checklist_templates')
