"""create job_slots table

Revision ID: c658259975b2
Revises: 69a22c66132e
Create Date: 2026-07-20 16:35:24.694106
"""
from __future__ import annotations

from alembic import op

revision = 'c658259975b2'
down_revision = '69a22c66132e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE job_slots (
            job_name   TEXT  PRIMARY KEY,
            capacity   INT   NOT NULL,
            in_use     INT   NOT NULL,
            CHECK (in_use <= capacity)
        )
    """)

    op.execute("INSERT INTO job_slots (job_name, capacity, in_use) VALUES ('ingest', 2, 0)")




def downgrade() -> None:
    op.execute("DROP TABLE job_slots")
