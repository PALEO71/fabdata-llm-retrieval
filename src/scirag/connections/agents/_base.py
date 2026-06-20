from __future__ import annotations
import json
import os
from typing import Optional

MODEL = os.getenv("SCIRAG_AGENT_MODEL", "claude-3-5-haiku-20241022")

_client = None


def _get_client():
    global _client
    if _client is None:
        import anthropic
        _client = anthropic.Anthropic()
    return _client


def run_agent(
    system_prompt: str,
    node_a: dict,
    node_b: dict,
    connection_type: str,
) -> Optional[dict]:
    """
    Ask Claude to decide whether two nodes are connected.
    Returns a dict with connect/weight/rationale/type, or None on failure.
    """
    user = (
        f"Nó A\nTítulo: {node_a.get('title', '(sem título)')}\n"
        f"Conteúdo: {node_a.get('content', '')[:800]}\n\n"
        f"Nó B\nTítulo: {node_b.get('title', '(sem título)')}\n"
        f"Conteúdo: {node_b.get('content', '')[:800]}"
    )
    try:
        resp = _get_client().messages.create(
            model=MODEL,
            max_tokens=200,
            system=system_prompt,
            messages=[{"role": "user", "content": user}],
        )
        text = resp.content[0].text.strip()
        start, end = text.find("{"), text.rfind("}") + 1
        if 0 <= start < end:
            result = json.loads(text[start:end])
            if result.get("connect"):
                result["type"] = connection_type
            return result
    except Exception:
        pass
    return None


def _make_agent(prompts: dict, types: dict, name: str):
    def agent(node_a: dict, node_b: dict) -> Optional[dict]:
        return run_agent(prompts[name], node_a, node_b, types[name])
    agent.__name__ = name
    return agent
