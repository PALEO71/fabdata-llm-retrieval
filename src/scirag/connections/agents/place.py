from ._base import _make_agent

_INSTRUCTION = (
    "Responde APENAS com JSON válido numa única linha:\n"
    '{"connect": true, "weight": 0.0-1.0, "rationale": "<uma frase em PT indicando o lugar>"}\n'
    "ou\n"
    '{"connect": false, "reason": "não-localizável"}'
)

_PROMPTS = {
    "algarve_anchor": (
        "És um agente de ancoragem geográfica ao Algarve. "
        "O teu papel é verificar se os dois fragmentos podem ser ligados "
        "através de uma referência geográfica ao Algarve ou ao sul de Portugal "
        "(serras, barrocal, litoral, concelhos, rios, praias, baías, grutas, afloramentos). "
        "Se um fragmento não tiver âncora geográfica, verifica se o contexto implica uma. "
        "Sinaliza como 'não-localizável' apenas se absolutamente nenhuma ligação geográfica for possível.\n\n"
        + _INSTRUCTION
    ),
}

_TYPES = {"algarve_anchor": "place:algarve_anchor"}

AGENTS = {name: _make_agent(_PROMPTS, _TYPES, name) for name in _PROMPTS}
