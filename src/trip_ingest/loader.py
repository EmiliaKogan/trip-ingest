"""Task 5 — put the trips in the database."""
from __future__ import annotations

from ast import If
from typing import Iterable

import psycopg

from trip_ingest.model import Trip



def _insert(conn: psycopg.Connection, batch_list: list[Trip]) -> int:
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO trips (trip_id, station_id, started_at, distance_m) VALUES (%s, %s, %s, %s) ON CONFLICT (trip_id) DO NOTHING",
            [(t.trip_id, t.station_id, t.started_at, t.distance_m)  for t in batch_list]
        )
        return cur.rowcount


def load_trips(conn: psycopg.Connection, trips: Iterable[Trip], batch_size: int = 1_000) -> int:
    """Insert `trips`, returning how many rows the database did not already have.

    `trips` is an iterable and may be a generator over a file larger than memory — consume it once,
    in batches, and do not build a list of the whole thing.

    Re-running last night's drop must insert nothing and return 0. The database already knows which
    trips it has; ask it, rather than reading it all back to check.
    """
    inserted, batch_list  = 0, []
    for trip in trips:
        batch_list.append(trip)
        if len(batch_list) == batch_size:
            inserted += _insert(conn, batch_list)
            batch_list.clear()
    # Handle any remaining trips in the last batch
    if batch_list:
        inserted += _insert(conn, batch_list)
    return inserted 

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # with conn.cursor() as cur:
    #     # 1. LAND: bulk-load the incoming data into a permissive RAW table with COPY (fast, append-only).
    #     cur.execute("DROP TABLE IF EXISTS trips_raw")
    #     cur.execute("CREATE TABLE trips_raw ( trip_id TEXT PRIMARY KEY, station_id TEXT NOT NULL, started_at TIMESTAMPTZ NOT NULL, distance_m INT NOT NULL)")    # loose: no keys, tolerates dupes
    #     batches = 0
    #     while True:
    #         batch = cur.fetchmany(batch_size)     # at most 1000 rows in memory at once
    #         if not batch:
    #             break
    #         batches += 1    
        
    #     # with cur.copy("COPY trips_raw (trip_id, station_id, started_at, distance_m) FROM STDIN") as copy:
    #     #     for trip in trips:
    #     #         copy.write_row((trip.trip_id, trip.station_id, trip.started_at, trip.distance_m))
    #     # 2. CHECK: run aggregate quality gates against trips here, before you trust it (see below).
    #     # 3. TRANSFORM + UPSERT: one set-based merge into the constrained target, all inside the DB.
    #     cur.execute(
    #         "INSERT INTO trips (trip_id, station_id, started_at, distance_m) SELECT trip_id, station_id, started_at, distance_m FROM trips " 
    #         # in select i give parameters via (%s) to the select statement, so that it can be used in the insert statement
    #         "ON CONFLICT (trip_id) DO NOTHING"
    #     )

#raise NotImplementedError
