"""add task responsible areas table

Revision ID: d4a9e51f8203
Revises: c3f8410d8291
Create Date: 2026-10-19 18:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'd4a9e51f8203'
down_revision: Union[str, None] = 'c3f8410d8291'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Criação da tabela associativa N:N task_responsible_areas
    op.create_table(
        'task_responsible_areas',
        sa.Column('task_id', sa.Integer(), sa.ForeignKey('audit_tasks.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('responsible_area_id', sa.Integer(), sa.ForeignKey('responsible_areas.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('task_responsible_areas')
