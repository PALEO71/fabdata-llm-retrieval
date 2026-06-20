from ._base import _make_agent

_INSTRUCTION = (
    "Responde APENAS com JSON válido numa única linha:\n"
    '{"connect": true, "weight": 0.0-1.0, "term_pt": "...", "term_en": "...", '
    '"rationale": "<uma frase em PT sobre o par terminológico>"}\n'
    "ou\n"
    '{"connect": false}'
)

_PROMPTS = {
    "pt_en_bridge": (
        "És um agente de ponte terminológica PT/EN para ciência portuguesa. "
        "Dados dois fragmentos (um pode estar em português, outro em inglês, ou ambos misturados), "
        "decide se existe um par terminológico relevante: um termo técnico em PT e o seu equivalente EN, "
        "um falso amigo, uma escolha de tradução não-óbvia, ou um neologismo científico em adopção. "
        "Esta ligação é usada para construir um vocabulário bilingue do corpus.\n\n"
        + _INSTRUCTION
    ),
}

_TYPES = {"pt_en_bridge": "bilingual:pt_en"}

AGENTS = {name: _make_agent(_PROMPTS, _TYPES, name) for name in _PROMPTS}
