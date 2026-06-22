from .pipeline import ingest_folder
from pathlib import Path
from typing import Optional


def ingest(folder: str | Path, db_path: Optional[Path] = None, **kw) -> int:
    """Tier 2 — knowledge: field notes, algarve-geology KB, paleontology papers (~500 tok chunks)."""
    return ingest_folder(folder, tier=2, db_path=db_path, **kw)
