"""Step 1: load the original dataset (berka.sql) into the staging database."""

import gzip
import time
from collections.abc import Iterator
from pathlib import Path

import pandas as pd

from berka_bank.db import Database

STAGING_TABLES = ["district", "client", "account", "disp", "card", "loan", "order", "trans"]
EXPECTED_TRANS_ROWS = 1_056_320


def read_statements(path: Path) -> Iterator[str]:
    """Yield the SQL statements of the file (each one ends with ';' at the end of a line).

    Reading line by line keeps every INSERT (~1,000 rows) under max_allowed_packet.
    Accepts plain .sql and gzip-compressed .sql.gz files.
    """
    opener = gzip.open if path.suffix == ".gz" else open
    buffer: list[str] = []
    with opener(path, "rt", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not buffer and (not stripped or stripped.startswith("--")):
                continue
            buffer.append(line)
            if stripped.endswith(";"):
                yield "".join(buffer)
                buffer = []


def is_loaded(db: Database) -> bool:
    try:
        n = db.query(f"SELECT COUNT(*) AS n FROM {db.settings.staging_db}.trans", engine=db.server)["n"][0]
        return n == EXPECTED_TRANS_ROWS
    except Exception:
        return False


def load(db: Database) -> None:
    """Run berka.sql statement by statement (1-3 minutes)."""
    start, n = time.time(), 0
    con = db.raw_connection()
    try:
        with con.cursor() as cur:
            for statement in read_statements(db.settings.berka_sql):
                cur.execute(statement)
                n += 1
                if n % 50 == 0:
                    print(f"\r  {n} statements executed...", end="", flush=True)
        con.commit()
    finally:
        con.close()
    print(f"\r  Done: {n} statements in {time.time() - start:.0f} s.        ")


def row_counts(db: Database):
    staging = db.settings.staging_db
    return pd.DataFrame(
        [
            {"table": t, "rows": db.query(f"SELECT COUNT(*) AS n FROM {staging}.`{t}`", engine=db.server)["n"][0]}
            for t in STAGING_TABLES
        ]
    )


def ensure(db: Database, force: bool = False) -> None:
    if is_loaded(db) and not force:
        print(f"[staging] '{db.settings.staging_db}' already loaded, skipping.")
        return
    if not db.settings.berka_sql.exists():
        raise FileNotFoundError(f"Dataset not found: {db.settings.berka_sql}")
    print(f"[staging] Loading {db.settings.berka_sql.name} into '{db.settings.staging_db}'...")
    load(db)
