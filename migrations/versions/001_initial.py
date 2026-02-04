"""Initial migration with users and batches tables

Revision ID: 001
Revises: 
Create Date: 2026-02-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create batches table
    op.create_table(
        'batches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('ship_date', sa.DateTime(), nullable=True),
        sa.Column('label_layout', sa.String(length=50), nullable=True),
        sa.Column('label_format', sa.String(length=50), nullable=True),
        sa.Column('display_scheme', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_batches_id'), 'batches', ['id'], unique=False)
    op.create_index(op.f('ix_batches_batch_id'), 'batches', ['batch_id'], unique=True)

    # Create batch_shipments table
    op.create_table(
        'batch_shipments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=False),
        sa.Column('shipment_id', sa.String(length=255), nullable=False),
        sa.Column('tracking_number', sa.String(length=255), nullable=True),
        sa.Column('carrier', sa.String(length=100), nullable=True),
        sa.Column('service_code', sa.String(length=100), nullable=True),
        sa.Column('label_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['batch_id'], ['batches.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_batch_shipments_id'), 'batch_shipments', ['id'], unique=False)
    op.create_index(op.f('ix_batch_shipments_shipment_id'), 'batch_shipments', ['shipment_id'], unique=False)

    # Create batch_rates table
    op.create_table(
        'batch_rates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=False),
        sa.Column('rate_id', sa.String(length=255), nullable=False),
        sa.Column('carrier', sa.String(length=100), nullable=True),
        sa.Column('service_type', sa.String(length=100), nullable=True),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['batch_id'], ['batches.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_batch_rates_id'), 'batch_rates', ['id'], unique=False)
    op.create_index(op.f('ix_batch_rates_rate_id'), 'batch_rates', ['rate_id'], unique=False)

    # Create batch_errors table
    op.create_table(
        'batch_errors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=False),
        sa.Column('error_code', sa.String(length=100), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=False),
        sa.Column('error_type', sa.String(length=100), nullable=True),
        sa.Column('source', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['batch_id'], ['batches.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_batch_errors_id'), 'batch_errors', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_batch_errors_id'), table_name='batch_errors')
    op.drop_table('batch_errors')
    op.drop_index(op.f('ix_batch_rates_rate_id'), table_name='batch_rates')
    op.drop_index(op.f('ix_batch_rates_id'), table_name='batch_rates')
    op.drop_table('batch_rates')
    op.drop_index(op.f('ix_batch_shipments_shipment_id'), table_name='batch_shipments')
    op.drop_index(op.f('ix_batch_shipments_id'), table_name='batch_shipments')
    op.drop_table('batch_shipments')
    op.drop_index(op.f('ix_batches_batch_id'), table_name='batches')
    op.drop_index(op.f('ix_batches_id'), table_name='batches')
    op.drop_table('batches')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
