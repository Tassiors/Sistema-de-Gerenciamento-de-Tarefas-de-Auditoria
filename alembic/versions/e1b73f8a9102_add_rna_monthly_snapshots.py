"""add rna_monthly_snapshots table

Revision ID: e1b73f8a9102
Revises: 7a9e4b0e6178
Create Date: 2026-10-19 16:04:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'e1b73f8a9102'
down_revision: Union[str, None] = '7a9e4b0e6178'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'rna_monthly_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('year_month', sa.String(length=7), nullable=False),
        sa.Column('label', sa.String(length=20), nullable=False),
        sa.Column('count_rna', sa.Integer(), nullable=False),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('is_closed', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('year_month')
    )
    op.create_index(op.f('ix_rna_monthly_snapshots_id'), 'rna_monthly_snapshots', ['id'], unique=False)
    op.create_index(op.f('ix_rna_monthly_snapshots_year_month'), 'rna_monthly_snapshots', ['year_month'], unique=True)

def downgrade() -> None:
    op.drop_index(op.f('ix_rna_monthly_snapshots_year_month'), table_name='rna_monthly_snapshots')
    op.drop_index(op.f('ix_rna_monthly_snapshots_id'), table_name='rna_monthly_snapshots')
    op.drop_table('rna_monthly_snapshots')
