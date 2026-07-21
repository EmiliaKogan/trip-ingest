"""Task 7 — at most two ingests at a time."""
from __future__ import annotations

from contextlib import contextmanager
from time import time
from typing import Iterator

import psycopg

from trip_ingest.errors import SlotUnavailable
from trip_ingest.settings import database_url




@contextmanager
def job_slot(job_name: str, timeout: float = 30.0) -> Iterator[None]:
    """Hold one of `job_name`'s permits for the duration of the block.

    Take a permit if one is free. If none is, wait for one — up to `timeout` seconds, then raise.
    Give the permit back when the block ends, however it ends.

    Read the README before you write this. Two details decide whether it works.
    """
    start = time()
    acquired = False
    try:
        with psycopg.connect(database_url(), autocommit=True) as conn:
            permit = conn.execute("UPDATE job_slots SET in_use = in_use + 1 WHERE job_name = %s AND in_use < capacity RETURNING in_use;", (job_name,))
            if not permit or permit.rowcount == 0:
                raise SlotUnavailable(f"No available slots for job '{job_name}'")
            if time() - start > timeout:
                raise TimeoutError(f"Timeout waiting for slot for job '{job_name}'")
            else:
                acquired = True
        yield
    finally:
        if acquired:
            with psycopg.connect(database_url(), autocommit=True) as conn:
                conn.execute("UPDATE job_slots SET in_use = in_use - 1 WHERE job_name = %s;", (job_name,))

    #yield   # unreachable; keeps the type of this function a context manager




