"""Create runs table

Revision ID: 001
Revises: 
Create Date: 2024-12-27 21:37:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create runs table
    op.create_table('runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('datetime_utc', sa.DateTime(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('distance', sa.Float(), nullable=False),
        sa.Column('duration', sa.Float(), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('avg_heart_rate', sa.Float(), nullable=True),
        sa.Column('shoes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better query performance
    op.create_index('ix_runs_datetime_utc', 'runs', ['datetime_utc'])
    op.create_index('ix_runs_source', 'runs', ['source'])
    op.create_index('ix_runs_shoes', 'runs', ['shoes'])
    op.create_index('ix_runs_updated_at', 'runs', ['updated_at'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('ix_runs_updated_at', table_name='runs')
    op.drop_index('ix_runs_shoes', table_name='runs')
    op.drop_index('ix_runs_source', table_name='runs')
    op.drop_index('ix_runs_datetime_utc', table_name='runs')
    
    # Drop table
    op.drop_table('runs')