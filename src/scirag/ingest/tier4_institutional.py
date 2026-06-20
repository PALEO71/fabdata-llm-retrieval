from .pipeline import ingest_folder
from pathlib import Path
from typing import Optional


def ingest(folder: str | Path, db_path: Optional[Path] = None, **kw) -> int:
    """Tier 4 — institutional: formal papers, reports (~800 tok chunks)."""
    return ingest_folder(folder, tier=4, db_path=db_path, **kw)
