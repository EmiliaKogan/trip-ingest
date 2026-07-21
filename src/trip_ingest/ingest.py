"""Task 6 — wire it together. Task 7 — and then make sure only two of these run at once."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Generator


from alembic.migration import Iterable, Iterator
import psycopg
from trip_ingest.errors import RowError
from trip_ingest.model import Report, Trip

from tests.conftest import conn

from trip_ingest.loader import load_trips
from trip_ingest.reader import parse_row, read_drop

from trip_ingest.settings import database_url

import logging

from trip_ingest.slots import job_slot

logger = logging.getLogger(__name__)


def _parse_all(path: Path, rejects_dir: Path, rejected: dict[str, int]) -> Generator[Trip, None, None]:
    """Parse rows lazily. Bad rows are written immediately to rejects file."""
    rejects_dir.mkdir(parents=True, exist_ok=True)#בודקים אם התיקיה קיימת, אם לא - יוצרים אותה
    reject_path = rejects_dir / f"{path.name}.rejects.jsonl"

    for row in read_drop(path):
        try:
            yield parse_row(row)
        except RowError as e:
            rejected["count"] += 1
            with reject_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"row": row,"error": type(e).__name__}) + "\n")


def ingest_drop(conn: psycopg.Connection, path: Path, rejects_dir: Path) -> Report:
    """Read one drop, load the good rows, write the bad ones aside, and report what happened.

    A rejected row must not stop the job, and it must not vanish either: write it to
    `rejects_dir/<drop-name>.rejects.jsonl`, one JSON object per line, each carrying the original row
    and why it was rejected. Somebody will have to fix these in the morning.
    """
    rejected = {"count": 0}
    loaded = load_trips(conn, _parse_all(path, rejects_dir, rejected))
    rejected = rejected["count"]

    return Report(
        read=loaded + rejected,
        loaded=loaded,
        rejected=rejected)


def _ingest_drop_all(conn: psycopg.Connection, drops: Iterable[Path], rejects_dir: Path) -> Report:

    total_loaded, total_rejected = 0, 0

    for path in drops:
        report = ingest_drop(conn, path, rejects_dir)
        total_loaded += report.loaded
        total_rejected += report.rejected

    return Report(
        read=total_loaded + total_rejected,
        loaded=total_loaded,
        rejected=total_rejected,
    )


def run_job(drop_dir: Path, rejects_dir: Path = Path("rejects")) -> Report:
    """Ingest every `*.jsonl` in `drop_dir` and return the totals across all of them.

    Task 6. Log a structured summary — one line, at INFO, naming the counts — so that a person on
    call at 3am can tell what happened without opening the database.

    Task 7. Two of these may run at once. A third must wait.
    """
    with job_slot("ingest"):
        drops = drop_dir.glob("*.jsonl") #לעבור על כל הקבצים בתיקיה DROPS
        with psycopg.connect(database_url()) as conn:
            totals = _ingest_drop_all(conn, drops, rejects_dir)

        logger.info(
            "Finished ingestion:  read=%s loaded=%s rejected=%s",
            totals.read,
            totals.loaded,
            totals.rejected
        )
        
        # logger.info(f"Finished ingesting drop {path.name} with {total_drops} total drops, {loaded+rejected} read rows, {loaded} loaded rows and {rejected} rejected rows.")

        # parametrized logging is better than f-strings because it avoids the cost of string formatting when the log level is higher than INFO. It also allows for structured logging,
        # where the log message can be parsed and analyzed more easily.

        return Report(
            read=totals.read,
            loaded=totals.loaded,
            rejected=totals.rejected
        )             


