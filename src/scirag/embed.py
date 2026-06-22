from __future__ import annotations
import os
from typing import List
import numpy as np

# Portuguese-friendly multilingual model. Override via env var if needed.
_MODEL_NAME = os.getenv("SCIRAG_EMBED_MODEL", "paraphrase-multilingual-mpnet-base-v2")
_model = None


def _get_model():
    """Lazy load — model downloads once (~420 MB) then is cached locally."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def embed_texts(texts: List[str]) -> List[np.ndarray]:
    """Return one L2-normalised float32 numpy array per text."""
    vecs = _get_model().encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,  # L2 norm → dot product = cosine similarity
        show_progress_bar=False,
    )
    return [v.astype(np.float32) for v in vecs]


def to_blob(vec: np.ndarray) -> bytes:
    return vec.astype(np.float32).tobytes()


def from_blob(blob: bytes) -> np.ndarray:
    return np.frombuffer(blob, dtype=np.float32)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    # Embeddings are L2-normalised, so dot product equals cosine similarity.
    return float(np.dot(a, b))


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
