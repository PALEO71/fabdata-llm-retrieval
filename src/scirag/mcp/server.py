"""scirag MCP server — 8 tools for a Portuguese science communicator's personal RAG."""
from __future__ import annotations
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastmcp import FastMCP

from ..db import get_conn
from ..embed import embed_texts, from_blob, to_blob, top_k_semantic

mcp = FastMCP("scirag — RAG pessoal para comunicador de ciência português")

SYNTH_MODEL = os.getenv("SCIRAG_SYNTH_MODEL", "claude-sonnet-4-6")

_MODE_PROMPTS = {
    "divulgacao": (
        "Escreves para o Sul Informação, jornal do Algarve. O leitor é curioso, culto mas não "
        "especialista. Escreve um texto de divulgação científica de 500–650 palavras. "
        "Começa com uma abertura forte (frase de impacto ou situação concreta). "
        "Evita jargão sem explicação. Usa comparações concretas ancoradas no sul de Portugal. "
        "Termina com uma frase que deixa o leitor a pensar. "
        "Proibido: 'delve', 'crucial', 'todavia', 'outrossim', 'é importante notar'."
    ),
    "pedagogico": (
        "Escreves material pedagógico para uma aula ou oficina de ciências (público: secundário ou universidade). "
        "Estrutura do mais simples para o mais complexo. Usa subtítulos claros. "
        "Inclui 2–3 questões de reflexão no final. Aproximadamente 400–500 palavras."
    ),
    "investigacao": (
        "Escreves uma síntese académica em português científico. "
        "Usa linguagem técnica precisa. Refere os fragmentos como fontes com [Fonte: título]. "
        "Postura neutra: apresenta evidências antes de conclusões. "
        "Assinala incertezas e limitações onde existam. Aproximadamente 400–600 palavras."
    ),
}

_anthro_client = None


def _get_anthro():
    global _anthro_client
    if _anthro_client is None:
        import anthropic
        _anthro_client = anthropic.Anthropic()
    return _anthro_client


def _fts_search(conn, query: str, top_k: int, writing_mode, tier) -> list[dict]:
    import re
    safe = re.sub(r'["\'\-\+\*\(\)\:]', ' ', query).strip()
    if not safe:
        return []
    tokens = safe.split()
    fts_query = " ".join(f'"{t}"' for t in tokens if t)
    where_clauses = ["id IN (SELECT node_id FROM nodes_fts WHERE nodes_fts MATCH ?)"]
    params: list = [fts_query]
    if writing_mode:
        where_clauses.append("writing_mode = ?")
        params.append(writing_mode)
    if tier is not None:
        where_clauses.append("tier = ?")
        params.append(tier)
    where = " AND ".join(where_clauses)
    rows = conn.execute(
        f"SELECT id, content, title, writing_mode, tier, source_id "
        f"FROM nodes WHERE {where} LIMIT ?",
        params + [top_k],
    ).fetchall()
    return [dict(r) for r in rows]


def _sem_search(conn, query: str, top_k: int, writing_mode, tier, candidate_ids=None) -> list[dict]:
    q_vec = embed_texts([query])[0]
    where = "embedding IS NOT NULL"
    params: list = []
    if writing_mode:
        where += " AND writing_mode = ?"
        params.append(writing_mode)
    if tier is not None:
        where += " AND tier = ?"
        params.append(tier)
    if candidate_ids:
        placeholders = ",".join("?" * len(candidate_ids))
        where += f" AND id IN ({placeholders})"
        params.extend(candidate_ids)
    rows = conn.execute(
        f"SELECT id, content, title, writing_mode, tier, source_id, embedding FROM nodes WHERE {where}",
        params,
    ).fetchall()
    candidates = [(r["id"], r["embedding"]) for r in rows]
    scored = top_k_semantic(q_vec, candidates, top_k)
    score_map = {s[0]: s[1] for s in scored}
    result_rows = conn.execute(
        f"SELECT id, content, title, writing_mode, tier, source_id FROM nodes "
        f"WHERE id IN ({','.join('?' * len(score_map))})",
        list(score_map),
    ).fetchall() if score_map else []
    return [{**dict(r), "score": score_map[r["id"]]} for r in result_rows]


# ── Tool 1: search ────────────────────────────────────────────────────────────

@mcp.tool()
def search(
    query: str,
    mode: str = "hybrid",
    top_k: int = 10,
    writing_mode: Optional[str] = None,
    tier: Optional[int] = None,
) -> str:
    """
    Search the personal corpus.

    mode: 'fts' (keyword), 'semantic' (embedding), or 'hybrid' (FTS then semantic rerank).
    writing_mode: filter by 'divulgacao', 'pedagogico', or 'investigacao'.
    tier: filter by ingestion tier (1–4).
    """
    with get_conn() as conn:
        if mode == "fts":
            results = _fts_search(conn, query, top_k, writing_mode, tier)
        elif mode == "semantic":
            results = _sem_search(conn, query, top_k, writing_mode, tier)
        else:  # hybrid
            fts = _fts_search(conn, query, top_k * 3, writing_mode, tier)
            candidate_ids = [r["id"] for r in fts]
            results = _sem_search(conn, query, top_k, writing_mode, tier, candidate_ids)

    return json.dumps(results, ensure_ascii=False, indent=2)


# ── Tool 2: connect ───────────────────────────────────────────────────────────

@mcp.tool()
def connect(
    from_id: str,
    to_id: str,
    connection_type: str,
    rationale: str,
    weight: float = 0.8,
) -> str:
    """Manually add a typed connection between two nodes."""
    with get_conn() as conn:
        for nid in (from_id, to_id):
            if not conn.execute("SELECT 1 FROM nodes WHERE id = ?", (nid,)).fetchone():
                return json.dumps({"error": f"Node not found: {nid}"})
        conn_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{from_id}|{to_id}|manual"))
        conn.execute(
            """INSERT OR REPLACE INTO connections
               (id, from_node, to_node, connection_type, agent_name, weight, rationale, created_at)
               VALUES (?, ?, ?, ?, 'manual', ?, ?, ?)""",
            (conn_id, from_id, to_id, connection_type, weight, rationale,
             datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    return json.dumps({"id": conn_id, "status": "created"})


# ── Tool 3: wiki ──────────────────────────────────────────────────────────────

@mcp.tool()
def wiki(theme: str, recompile: bool = False) -> str:
    """
    Get or recompile a thematic wiki page from the author's own corpus.

    theme: one of the 8 seed themes (e.g. 'paleontologia_algarve', 'tempo_profundo').
    recompile: if True, rebuilds even if a cached version exists.
    """
    with get_conn() as conn:
        if not recompile:
            row = conn.execute(
                "SELECT theme, content, last_compiled, version FROM wikis WHERE theme = ?",
                (theme,),
            ).fetchone()
            if row:
                return json.dumps(dict(row), ensure_ascii=False, indent=2)

    from ..wiki.compiler import compile_wiki
    result = compile_wiki(theme)
    return json.dumps(result, ensure_ascii=False, indent=2)


# ── Tool 4: synthesize ────────────────────────────────────────────────────────

@mcp.tool()
def synthesize(
    query: str,
    writing_mode: str = "investigacao",
    node_ids: Optional[str] = None,
    persist: bool = True,
) -> str:
    """
    Generate a synthesis in a target writing mode.

    writing_mode: 'divulgacao', 'pedagogico', or 'investigacao'.
    node_ids: optional JSON array of node IDs to use instead of running a search.
    """
    with get_conn() as conn:
        if node_ids:
            ids = json.loads(node_ids)
            placeholders = ",".join("?" * len(ids))
            rows = conn.execute(
                f"SELECT id, content, title, source_id FROM nodes WHERE id IN ({placeholders})",
                ids,
            ).fetchall()
        else:
            results = json.loads(search(query, mode="hybrid", top_k=8,
                                        writing_mode=writing_mode))
            ids = [r["id"] for r in results]
            placeholders = ",".join("?" * len(ids)) if ids else "NULL"
            rows = conn.execute(
                f"SELECT id, content, title, source_id FROM nodes WHERE id IN ({placeholders})",
                ids,
            ).fetchall() if ids else []

        if not rows:
            return json.dumps({"error": "No nodes found. Run search or ingest content first."})

        context = "\n\n---\n\n".join(
            f"[Fonte: {r['title'] or r['source_id']}]\n{r['content']}"
            for r in rows
        )
        system = _MODE_PROMPTS.get(writing_mode, _MODE_PROMPTS["investigacao"])
        resp = _get_anthro().messages.create(
            model=SYNTH_MODEL,
            max_tokens=1500,
            system=system,
            messages=[{"role": "user", "content": f"Query: {query}\n\nFragmentos:\n\n{context}"}],
        )
        content = resp.content[0].text
        result = {"query": query, "writing_mode": writing_mode, "content": content,
                  "node_count": len(rows)}

        if persist:
            synth_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc).isoformat()
            conn.execute(
                """INSERT INTO syntheses (id, title, content, query, node_ids, writing_mode, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (synth_id, query[:80], content, query,
                 json.dumps([r["id"] for r in rows]), writing_mode, now),
            )
            conn.commit()
            result["synthesis_id"] = synth_id

    return json.dumps(result, ensure_ascii=False, indent=2)


# ── Tool 5: reingest ──────────────────────────────────────────────────────────

@mcp.tool()
def reingest(source_id: str, chunk_size: Optional[int] = None) -> str:
    """Re-chunk and re-embed a source document (useful after editing the source)."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, title, full_text, tier, metadata FROM sources WHERE id = ?",
            (source_id,),
        ).fetchone()
        if not row:
            return json.dumps({"error": f"Source not found: {source_id}"})

        tier = row["tier"] or 1
        text = row["full_text"] or ""
        meta = json.loads(row["metadata"] or "{}")

        from ..ingest.pipeline import TIER_CHUNK_SIZES, TIER_MODES, _chunk_text, BATCH
        cs = chunk_size or TIER_CHUNK_SIZES.get(tier, 300)
        writing_mode = TIER_MODES.get(tier, "investigacao")
        chunks = _chunk_text(text, cs)

        conn.execute("DELETE FROM nodes WHERE source_id = ?", (source_id,))

        node_rows = []
        now = datetime.now(timezone.utc).isoformat()
        for i in range(0, len(chunks), BATCH):
            batch = chunks[i: i + BATCH]
            vecs = embed_texts(batch)
            for j, (ct, vec) in enumerate(zip(batch, vecs)):
                node_rows.append((f"{source_id}_{i+j}", ct, row["title"],
                                  writing_mode, source_id, tier, now, to_blob(vec)))

        conn.executemany(
            """INSERT OR REPLACE INTO nodes
               (id, content, title, writing_mode, source_id, tier, created_at, embedding)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            node_rows,
        )
        conn.execute(
            "UPDATE sources SET ingested_at = ? WHERE id = ?",
            (now, source_id),
        )
        conn.commit()

    return json.dumps({"source_id": source_id, "nodes_created": len(node_rows)})


# ── Tool 6: random_walk ───────────────────────────────────────────────────────

@mcp.tool()
def random_walk(
    seed_id: str,
    steps: int = 5,
    connection_types: Optional[str] = None,
) -> str:
    """
    Follow connections from a seed node for serendipitous discovery.

    connection_types: optional JSON array of type strings to filter edges.
    """
    ctypes = json.loads(connection_types) if connection_types else None
    path = [seed_id]
    current = seed_id

    with get_conn() as conn:
        for _ in range(steps):
            where = "from_node = ?"
            params: list = [current]
            if ctypes:
                placeholders = ",".join("?" * len(ctypes))
                where += f" AND connection_type IN ({placeholders})"
                params.extend(ctypes)
            row = conn.execute(
                f"SELECT to_node FROM connections WHERE {where} "
                "ORDER BY weight DESC LIMIT 1",
                params,
            ).fetchone()
            if not row or row["to_node"] in path:
                break
            current = row["to_node"]
            path.append(current)

        placeholders = ",".join("?" * len(path))
        rows = conn.execute(
            f"SELECT id, content, title, writing_mode, tier FROM nodes WHERE id IN ({placeholders})",
            path,
        ).fetchall()
        node_map = {r["id"]: dict(r) for r in rows}

    return json.dumps(
        [node_map[nid] for nid in path if nid in node_map],
        ensure_ascii=False, indent=2,
    )


# ── Tool 7: pedagogy ──────────────────────────────────────────────────────────

@mcp.tool()
def pedagogy(
    query: str,
    level: str = "medio",
    concept_count: int = 5,
) -> str:
    """
    Build a concept ladder for a topic.

    level: starting level — 'basico', 'medio', or 'avancado'.
    Returns a sequence of nodes ordered from simple to complex.
    """
    with get_conn() as conn:
        # Find nodes with concept_ladder connections
        rows = conn.execute(
            "SELECT DISTINCT n.id, n.content, n.title, n.writing_mode "
            "FROM connections c JOIN nodes n ON n.id = c.from_node "
            "WHERE c.connection_type = 'pedagogical:concept_ladder' "
            "UNION "
            "SELECT DISTINCT n.id, n.content, n.title, n.writing_mode "
            "FROM connections c JOIN nodes n ON n.id = c.to_node "
            "WHERE c.connection_type = 'pedagogical:concept_ladder' "
            "LIMIT 100",
        ).fetchall()

        candidates = [dict(r) for r in rows]

        if not candidates:
            # Fall back to FTS search filtered by pedagogico mode
            fts = _fts_search(conn, query, concept_count * 2, "pedagogico", None)
            candidates = fts

        if not candidates:
            return json.dumps({"error": "No pedagogical content found. Ingest tier-3 content first."})

        # Ask Claude to order into a concept ladder
        context = "\n\n".join(
            f"ID: {n['id']}\nTítulo: {n.get('title','')}\nConteúdo: {n.get('content','')[:400]}"
            for n in candidates[:15]
        )
        resp = _get_anthro().messages.create(
            model=SYNTH_MODEL,
            max_tokens=800,
            system=(
                "Organiza os fragmentos fornecidos numa escada conceptual pedagógica "
                f"sobre o tema pedido. Nível de entrada: {level}. "
                f"Selecciona {concept_count} fragmentos e ordena-os do mais simples ao mais complexo. "
                "Responde em JSON: "
                '{"ladder": [{"id": "...", "level": "basico|medio|avancado", "reason": "..."}]}'
            ),
            messages=[{"role": "user", "content": f"Tema: {query}\n\nFragmentos:\n\n{context}"}],
        )
        text = resp.content[0].text.strip()
        start, end = text.find("{"), text.rfind("}") + 1
        ladder_data = json.loads(text[start:end]) if 0 <= start < end else {"ladder": []}

        # Hydrate with full content
        id_map = {n["id"]: n for n in candidates}
        for item in ladder_data.get("ladder", []):
            item["content"] = id_map.get(item["id"], {}).get("content", "")
            item["title"] = id_map.get(item["id"], {}).get("title", "")

    return json.dumps({"query": query, "level": level, **ladder_data},
                      ensure_ascii=False, indent=2)


# ── Tool 8: voice_match ───────────────────────────────────────────────────────

@mcp.tool()
def voice_match(
    content: str,
    target_mode: str = "divulgacao",
    top_k: int = 5,
) -> str:
    """
    Score content against a writing register and return exemplar nodes from the corpus.

    Use this at output time to calibrate register before finalising a text.
    target_mode: 'divulgacao', 'pedagogico', or 'investigacao'.
    """
    q_vec = embed_texts([content])[0]

    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, content, title, embedding FROM nodes WHERE writing_mode = ? AND embedding IS NOT NULL",
            (target_mode,),
        ).fetchall()

    candidates = [(r["id"], r["embedding"]) for r in rows]
    scored = top_k_semantic(q_vec, candidates, top_k)

    if not scored:
        return json.dumps({"error": f"No nodes with writing_mode='{target_mode}' found."})

    id_map = {r["id"]: dict(r) for r in rows}
    exemplars = [
        {"id": nid, "score": score,
         "title": id_map[nid].get("title", ""),
         "content": id_map[nid].get("content", "")[:400]}
        for nid, score in scored
    ]

    # Ask Claude for style notes comparing content to exemplars
    ex_text = "\n\n".join(f"Exemplar {i+1}: {e['content']}" for i, e in enumerate(exemplars[:3]))
    resp = _get_anthro().messages.create(
        model=SYNTH_MODEL,
        max_tokens=400,
        system=(
            f"Compara o texto submetido com exemplares do registo '{target_mode}' do corpus do autor. "
            "Identifica 2–3 ajustes concretos de voz, tom ou estrutura para aproximar o texto submetido "
            "do registo alvo. Sê específico e breve. Responde em PT."
        ),
        messages=[{"role": "user",
                   "content": f"Texto submetido:\n{content[:600]}\n\nExemplares do corpus:\n{ex_text}"}],
    )

    return json.dumps({
        "target_mode": target_mode,
        "exemplars": exemplars,
        "style_notes": resp.content[0].text,
    }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run()
