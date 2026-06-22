from __future__ import annotations
import os
import sqlite3
from pathlib import Path
from typing import Optional

_SCHEMA = Path(__file__).parent / "schema.sql"
_DEFAULT_DB = Path(__file__).resolve().parents[3] / "scirag.db"


def get_db_path() -> Path:
    env = os.getenv("SCIRAG_DB_PATH")
    return Path(env) if env else _DEFAULT_DB


def get_conn(path: Optional[Path] = None) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path or get_db_path()))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(path: Optional[Path] = None) -> None:
    schema = _SCHEMA.read_text(encoding="utf-8")
    with get_conn(path) as conn:
        conn.executescript(schema)
    print(f"Database initialised at {path or get_db_path()}")
