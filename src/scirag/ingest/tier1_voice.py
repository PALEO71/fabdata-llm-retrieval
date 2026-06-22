from .pipeline import ingest_folder
from pathlib import Path
from typing import Optional


def ingest(folder: str | Path, db_path: Optional[Path] = None, **kw) -> int:
    """Tier 1 — voice: Sul Informação columns, published divulgação pieces (~200 tok chunks)."""
    return ingest_folder(folder, tier=1, db_path=db_path, **kw)
