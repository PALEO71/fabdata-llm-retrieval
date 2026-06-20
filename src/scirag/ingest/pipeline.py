from __future__ import annotations
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from ..db import get_conn
from ..embed import embed_texts, to_blob

TIER_CHUNK_SIZES = {1: 200, 2: 500, 3: 300, 4: 800}
TIER_MODES = {1: "divulgacao", 2: "investigacao", 3: "pedagogico", 4: "investigacao"}
BATCH = 64


def _extract_text(path: Path) -> Optional[str]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        try:
            import fitz
            doc = fitz.open(str(path))
            return "\n".join(page.get_text() for page in doc)
        except Exception:
            from pypdf import PdfReader
            return "\n".join(p.extract_text() or "" for p in PdfReader(str(path)).pages)
    elif suffix in (".txt", ".md"):
        return path.read_text(encoding="utf-8", errors="replace")
    return None


def _chunk_text(text: str, chunk_size: int) -> List[str]:
    from fdllmret.services.chunks import get_text_chunks
    return get_text_chunks(text, chunk_size)


def ingest_folder(
    folder: str | Path,
    tier: int,
    db_path: Optional[Path] = None,
    exts: tuple = (".pdf", ".txt", ".md"),
    skip_existing: bool = True,
) -> int:
    folder = Path(folder)
    chunk_size = TIER_CHUNK_SIZES.get(tier, 300)
    writing_mode = TIER_MODES.get(tier, "investigacao")
    count = 0

    with get_conn(db_path) as conn:
        for fpath in sorted(folder.rglob("*")):
            if fpath.suffix.lower() not in exts:
                continue

            source_id = str(uuid.uuid5(uuid.NAMESPACE_URL, fpath.as_posix()))

            if skip_existing and conn.execute(
                "SELECT 1 FROM sources WHERE id = ?", (source_id,)
            ).fetchone():
                continue

            text = _extract_text(fpath)
            if not text or text.isspace():
                continue

            now = datetime.now(timezone.utc).isoformat()
            conn.execute(
                """INSERT OR REPLACE INTO sources
                   (id, title, source_type, language, tier, ingested_at, full_text, metadata)
                   VALUES (?, ?, 'file', 'pt', ?, ?, ?, ?)""",
                (source_id, fpath.stem, tier, now, text,
                 json.dumps({"file_path": str(fpath)})),
            )

            chunks = _chunk_text(text, chunk_size)
            if not chunks:
                conn.commit()
                continue

            node_rows: list[tuple] = []
            for i in range(0, len(chunks), BATCH):
                batch_texts = chunks[i: i + BATCH]
                vecs = embed_texts(batch_texts)
                for j, (ct, vec) in enumerate(zip(batch_texts, vecs)):
                    node_rows.append((
                        f"{source_id}_{i + j}",
                        ct, fpath.stem, writing_mode,
                        source_id, tier, now, to_blob(vec),
                    ))

            conn.executemany(
                """INSERT OR REPLACE INTO nodes
                   (id, content, title, writing_mode, source_id, tier, created_at, embedding)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                node_rows,
            )
            conn.commit()
            count += 1
            print(f"  ingested {fpath.name} → {len(node_rows)} nodes")

    return count
