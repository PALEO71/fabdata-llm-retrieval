from .pipeline import ingest_folder
from pathlib import Path
from typing import Optional


def ingest(folder: str | Path, db_path: Optional[Path] = None, **kw) -> int:
    """Tier 3 — pedagogy: workshop notes, slides, teaching scripts (~300 tok chunks)."""
    return ingest_folder(folder, tier=3, db_path=db_path, **kw)
