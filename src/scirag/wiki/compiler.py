from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ..db import get_conn
from .seeds import SEED_THEMES

MODEL = os.getenv("SCIRAG_WIKI_MODEL", "claude-3-5-sonnet-20241022")

_client = None


def _get_client():
    global _client
    if _client is None:
        import anthropic
        _client = anthropic.Anthropic()
    return _client


def _fetch_nodes_for_theme(conn, seed: dict) -> list[dict]:
    keywords = seed["keywords"][0] if seed["keywords"] else seed["title"]
    safe = keywords.replace('"', "").replace("'", "")
    rows = conn.execute(
        "SELECT n.id, n.content, n.title, n.writing_mode "
        "FROM nodes_fts f JOIN nodes n ON n.id = f.node_id "
        "WHERE nodes_fts MATCH ? ORDER BY rank LIMIT 25",
        (safe,),
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
        r = compile_wiki(theme, db_path)
        results[theme] = r.get("node_count", 0) if "error" not in r else -1
    return results
