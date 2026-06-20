from __future__ import annotations
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ..db import get_conn
from .agents import REGISTRY

GROUPS: dict[str, list[str]] = {
    "topical":     ["geo_paleo", "ecology_climate", "territory_place", "science_history"],
    "bridges":     ["science_narrative", "local_global", "data_story", "metaphor_map"],
    "place":       ["algarve_anchor"],
    "voice_form":  ["divulgacao_voice", "pedagogico_form", "investigacao_form"],
    "temporal":    ["deep_time", "tension_finder", "update_tracker"],
    "pedagogical": ["concept_ladder"],
    "bilingual":   ["pt_en_bridge"],
}

ALL_AGENTS = [a for agents in GROUPS.values() for a in agents]


def _sample_pairs(conn, n: int) -> list[tuple[dict, dict]]:
    rows = conn.execute(
        "SELECT id, content, title, writing_mode, tier FROM nodes ORDER BY RANDOM() LIMIT ?",
        (n * 2,),
    ).fetchall()
    nodes = [dict(r) for r in rows]
    return [(nodes[i], nodes[i + 1]) for i in range(0, len(nodes) - 1, 2)]


def dispatch(
    group: str = "all",
    n_pairs: int = 50,
    db_path: Optional[Path] = None,
) -> int:
    agent_names = ALL_AGENTS if group == "all" else GROUPS.get(group, [])
    total = 0

    with get_conn(db_path) as conn:
        pairs = _sample_pairs(conn, n_pairs)
        if not pairs:
            print("  No nodes found — run ingest first.")
            return 0

        for name in agent_names:
            fn = REGISTRY.get(name)
            if fn is None:
                print(f"  Agent '{name}' not in registry, skipping.")
                continue

            written = 0
            for node_a, node_b in pairs:
                result = fn(node_a, node_b)
                if not result or not result.get("connect"):
                    continue
                conn_id = str(uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    f"{node_a['id']}|{node_b['id']}|{name}",
                ))
                conn.execute(
                    """INSERT OR REPLACE INTO connections
                       (id, from_node, to_node, connection_type, agent_name,
                        weight, rationale, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        conn_id,
                        node_a["id"], node_b["id"],
                        result.get("type", name), name,
                        float(result.get("weight", 0.8)),
                        result.get("rationale", ""),
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                written += 1

            conn.commit()
            print(f"  {name}: {written} connections written")
            total += written

    return total
