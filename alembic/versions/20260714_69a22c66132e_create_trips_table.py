"""create trips table

Revision ID: 69a22c66132e
Revises: 
Create Date: 2026-07-14 18:35:04.095218
"""
from __future__ import annotations

from alembic import op

revision = '69a22c66132e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE trips (
            trip_id    TEXT PRIMARY KEY,
            station_id TEXT NOT NULL,
            started_at TIMESTAMPTZ NOT NULL,
            distance_m INT NOT NULL
        )
    """)
    # op.execute("CREATE INDEX ix_trips_started_at ON trips (started_at)")


def downgrade() -> None:
    # op.execute("DROP INDEX ix_trips_started_at")
    op.execute("DROP TABLE trips")