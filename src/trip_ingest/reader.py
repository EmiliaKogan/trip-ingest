"""Tasks 2 and 3 — get rows out of a file, and turn them into trips."""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from trip_ingest.model import RawRow, Trip

import json
from trip_ingest.errors import MissingField ,NegativeDistance, BadTimestamp
from datetime import datetime


def read_drop(path: Path) -> Iterator[RawRow]:
    """Yield one raw JSON object per line of a `.jsonl` drop.

    Task 2. A drop is a night's trips: it does not fit in memory, and on a bad night it does not fit
    on the machine. Nothing that reads it may hold more than one line at a time.
    """
    
    with path.open("r", encoding="utf-8") as f:
        for line in f:  
            if line.strip() == "":
                continue
            else:                   
                yield json.loads(line)
    #  if line.strip():                  
    #       yield json.loads(line)   #more compact way to write the above code



bad_rows = []
def parse_row(raw: RawRow) -> Trip:
    """Turn one raw JSON object into a `Trip`, or raise. Task 3."""

    if raw.get("trip_id") is None or raw.get("station_id") is None or raw.get("distance_m") is None:
        bad_rows.append(raw)
        raise MissingField
    
    if raw["distance_m"] < 0:
        bad_rows.append(raw)
        raise NegativeDistance
    
    try:
        return Trip(
            trip_id=raw["trip_id"],
            station_id=raw["station_id"],
            started_at=datetime.fromisoformat(raw["started_at"]),
            distance_m=int(raw["distance_m"])
        )
        #return Trip.model_validate(raw) 
        ##more compact way to write the above code, pydantic will handle the validation and raise errors if any field is missing or has an invalid value.
    
    except (ValueError, KeyError):
        bad_rows.append(raw)
        raise BadTimestamp

    

    # if raw.get("trip_id") is None or raw.get("station_id") is None or raw.get("distance_m") is None or raw.get("started_at") is None:
    #     bad_rows.append(raw)
    #     raise MissingField
    
    # if datetime.fromisoformat(raw["started_at"]) is None or raw.get("started_at") is None:
    #     bad_rows.append(raw)
    #     raise BadTimestamp
    
    # if raw["distance_m"] < 0:
    #     bad_rows.append(raw)
    #     raise NegativeDistance

    # return Trip(
    #         trip_id=raw["trip_id"],
    #         station_id=raw["station_id"],
    #         started_at=datetime.fromisoformat(raw["started_at"]),
    #         distance_m=int(raw["distance_m"])
    #         )


# csv_out = Path("/tmp/borough_counts.csv")
# jsonl_path = Path("/data/trips_sample.jsonl")


# def convert(jsonl_path, csv_out):
#     n = 0
#     n_out = 0
#     # Open the input file for reading AND the output file for writing
#     with (
#         jsonl_path.open("r", encoding="utf-8") as f_in,
#         csv_out.open("w", encoding="utf-8", newline="") as f_out,
#     ):

#         writer = csv.writer(f_out)
#         writer.writerow(["pu_location_id", "total_amount"])  # Write CSV Header

#         for line in f_in:  # Read line by line
#             rec = json.loads(line)
#             n += 1

#             # Extract actual values from the JSON object (using .get() safely handles missing keys)
#             pu_location_id = rec.get("pu_location_id")
#             total_amount = rec.get("total_amount")

#             writer.writerow([pu_location_id, total_amount])
#             n_out+=1

#     print(f"{n:,} records readed")
#     print(f"{n_out:,} records written")
#     ##print(csv_out.read_text(encoding="utf-8"))

# convert(jsonl_path, csv_out)   