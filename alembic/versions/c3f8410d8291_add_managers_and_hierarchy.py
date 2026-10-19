"""add managers and hierarchy

Revision ID: c3f8410d8291
Revises: e1b73f8a9102
Create Date: 2026-10-19 16:55:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c3f8410d8291'
down_revision: Union[str, None] = 'e1b73f8a9102'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add columns to responsible_areas
    with op.batch_alter_table('responsible_areas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sigla', sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column('level', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('parent_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_responsible_areas_parent', 'responsible_areas', ['parent_id'], ['id'])
        batch_op.create_index(batch_op.f('ix_responsible_areas_parent_id'), ['parent_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_responsible_areas_sigla'), ['sigla'], unique=False)

    # Create system_managers table
    op.create_table(
        'system_managers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='GESTOR'),
        sa.Column('responsible_area_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['responsible_area_id'], ['responsible_areas.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_system_managers_id'), 'system_managers', ['id'], unique=False)
    op.create_index(op.f('ix_system_managers_username'), 'system_managers', ['username'], unique=True)
    op.create_index(op.f('ix_system_managers_responsible_area_id'), 'system_managers', ['responsible_area_id'], unique=False)

    # Create manager_extra_units table
    op.create_table(
        'manager_extra_units',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('manager_id', sa.Integer(), nullable=False),
        sa.Column('responsible_area_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['manager_id'], ['system_managers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['responsible_area_id'], ['responsible_areas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('manager_id', 'responsible_area_id', name='uq_manager_extra_unit')
    )
    op.create_index(op.f('ix_manager_extra_units_id'), 'manager_extra_units', ['id'], unique=False)
    op.create_index(op.f('ix_manager_extra_units_manager_id'), 'manager_extra_units', ['manager_id'], unique=False)
    op.create_index(op.f('ix_manager_extra_units_responsible_area_id'), 'manager_extra_units', ['responsible_area_id'], unique=False)

def downgrade() -> None:
    op.drop_table('manager_extra_units')
    op.drop_table('system_managers')
    with op.batch_alter_table('responsible_areas', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_responsible_areas_sigla'))
        batch_op.drop_index(batch_op.f('ix_responsible_areas_parent_id'))
        batch_op.drop_constraint('fk_responsible_areas_parent', type_='foreignkey')
        batch_op.drop_column('parent_id')
        batch_op.drop_column('level')
        batch_op.drop_column('sigla')
