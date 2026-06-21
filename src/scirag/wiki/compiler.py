from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ..db import get_conn
from .seeds import SEED_THEMES

MODEL = os.getenv("SCIRAG_WIKI_MODEL", "claude-sonnet-4-6")

_client = None


def _get_client():
    global _client
    if _client is None:
        import anthropic
        _client = anthropic.Anthropic()
    return _client


def _ensure_fts(conn) -> None:
    """Rebuild FTS5 index if it is empty but nodes exist (handles INSERT OR REPLACE timing)."""
    fts_count = conn.execute("SELECT COUNT(*) FROM nodes_fts").fetchone()[0]
    if fts_count == 0:
        node_count = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        if node_count > 0:
            print(f"  [FTS5] index empty — rebuilding from {node_count} nodes...")
            conn.execute(
                "INSERT INTO nodes_fts(node_id, content, title) "
                "SELECT id, content, COALESCE(title, '') FROM nodes"
            )
            conn.commit()


def _fetch_nodes_for_theme(conn, seed: dict) -> list[dict]:
    import re
    _ensure_fts(conn)
    keywords = seed["keywords"][0] if seed["keywords"] else seed["title"]
    # Strip FTS5 special chars then quote each token
    tokens = re.sub(r'["\'\-\+\*\(\)\:]', ' ', keywords).split()
    # OR between terms so any keyword match qualifies (chunks are small)
    fts_query = " OR ".join(f'"{t}"' for t in tokens if t)
    if not fts_query:
        fts_query = f'"{seed["title"]}"'
    rows = conn.execute(
        "SELECT id, content, title, writing_mode FROM nodes "
        "WHERE id IN (SELECT node_id FROM nodes_fts WHERE nodes_fts MATCH ?) "
        "LIMIT 25",
        (fts_query,),
    ).fetchall()
    nodes = [dict(r) for r in rows]

    if nodes:
        placeholders = ",".join("?" * len(nodes))
        ids = [n["id"] for n in nodes]
        extra = conn.execute(
            f"SELECT DISTINCT n.id, n.content, n.title, n.writing_mode "
            f"FROM connections c JOIN nodes n ON n.id = c.to_node "
            f"WHERE c.from_node IN ({placeholders}) LIMIT 10",
            ids,
        ).fetchall()
        seen = {n["id"] for n in nodes}
        for r in extra:
            if r["id"] not in seen:
                nodes.append(dict(r))
                seen.add(r["id"])

    return nodes


def compile_wiki(theme: str, db_path: Optional[Path] = None) -> dict:
    seed = SEED_THEMES.get(theme)
    if not seed:
        return {"error": f"Unknown theme: {theme}. Available: {list(SEED_THEMES)}"}

    with get_conn(db_path) as conn:
        nodes = _fetch_nodes_for_theme(conn, seed)
        if not nodes:
            return {"error": f"No nodes found for theme '{theme}'. Ingest content first."}

        context = "\n\n---\n\n".join(
            f"[{n.get('title', 'sem título')} | {n.get('writing_mode', '')}]\n{n.get('content', '')[:600]}"
            for n in nodes[:20]
        )

        system = (
            "És o compilador de uma wiki pessoal de um investigador e comunicador de ciência português. "
            "Com base nos fragmentos do seu corpus, escreve uma página wiki temática em PT-PT.\n\n"
            "Formato obrigatório:\n"
            "```yaml\n---\ntitle: <título>\ntype: topic\ndomain: <domain>\nlang: pt-PT\n"
            "last_updated: <data hoje>\n---\n```\n\n"
            "Depois:\n"
            "## Introdução (150–200 palavras, registo neutro e factual)\n"
            "## Conceitos-chave (lista com breve descrição de cada)\n"
            "## Padrões no corpus (o que o investigador escreve sobre este tema — sem inventar)\n"
            "## Ligações (temas relacionados no formato [[tema]])\n"
            "## EN summary (50–80 palavras em inglês)\n\n"
            "Proibido: 'delve', 'crucial', 'todavia', 'outrossim', 'é importante notar', 'em conclusão'."
        )

        user = (
            f"Tema: {seed['title']}\nDescrição: {seed['description']}\n"
            f"Domínio: {seed['domain']}\n\nFragmentos do corpus:\n\n{context}"
        )

        resp = _get_client().messages.create(
            model=MODEL,
            max_tokens=1800,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        content = resp.content[0].text

        wiki_id = f"wiki_{theme}"
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """INSERT OR REPLACE INTO wikis (id, theme, content, seed_node_ids, last_compiled, version)
               VALUES (?, ?, ?, ?, ?,
                       COALESCE((SELECT version + 1 FROM wikis WHERE theme = ?), 1))""",
            (wiki_id, theme, content,
             json.dumps([n["id"] for n in nodes[:20]]), now, theme),
        )
        conn.commit()

    return {"theme": theme, "content": content, "node_count": len(nodes)}


def compile_all(db_path: Optional[Path] = None) -> dict[str, int]:
    results = {}
    for theme in SEED_THEMES:
        print(f"  compiling wiki: {theme}")
        try:
            r = compile_wiki(theme, db_path)
        except Exception as exc:
            print(f"    [exception] {exc}")
            results[theme] = -1
            continue
        if "error" in r:
            print(f"    [error] {r['error']}")
        results[theme] = r.get("node_count", 0) if "error" not in r else -1
    return results
