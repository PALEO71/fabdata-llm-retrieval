from __future__ import annotations
from typing import List
import numpy as np


def _get_embeddings_fn():
    """Lazy import — avoids failing at module load if OPENAI_API_KEY is absent."""
    from fdllmret.services.openai import get_embeddings
    return get_embeddings


def embed_texts(texts: List[str]) -> List[np.ndarray]:
    """Return one float32 numpy array per text."""
    get_embeddings = _get_embeddings_fn()
    raw = get_embeddings(texts)
    return [np.array(v, dtype=np.float32) for v in raw]


def to_blob(vec: np.ndarray) -> bytes:
    return vec.astype(np.float32).tobytes()


def from_blob(blob: bytes) -> np.ndarray:
    return np.frombuffer(blob, dtype=np.float32)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def top_k_semantic(
    query_vec: np.ndarray,
    candidates: list[tuple[str, bytes]],
    k: int,
) -> list[tuple[str, float]]:
    """Rank candidates by cosine similarity. candidates = [(node_id, blob), ...]."""
    scored = [
        (node_id, cosine(query_vec, from_blob(blob)))
        for node_id, blob in candidates
        if blob is not None
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
