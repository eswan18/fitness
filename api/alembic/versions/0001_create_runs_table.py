"""Create runs table

Revision ID: 0001
Revises:
Create Date: 2024-12-17 22:09:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE runs (
            id SERIAL PRIMARY KEY,
            datetime_utc TIMESTAMP NOT NULL,
            type VARCHAR(50) NOT NULL CHECK (type IN ('Outdoor Run', 'Treadmill Run')),
            distance FLOAT NOT NULL,
            duration FLOAT NOT NULL,
            source VARCHAR(50) NOT NULL CHECK (source IN ('MapMyFitness', 'Strava')),
            avg_heart_rate FLOAT,
            shoes VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create indexes for common queries
    op.execute("CREATE INDEX idx_runs_datetime_utc ON runs (datetime_utc)")
    op.execute("CREATE INDEX idx_runs_source ON runs (source)")
    op.execute("CREATE INDEX idx_runs_shoes ON runs (shoes)")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS runs")
