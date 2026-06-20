from ._base import _make_agent

_INSTRUCTION = (
    "Responde APENAS com JSON válido numa única linha:\n"
    '{"connect": true, "weight": 0.0-1.0, "level_a": "basico|medio|avancado", '
    '"level_b": "basico|medio|avancado", "rationale": "<uma frase em PT>"}\n'
    "ou\n"
    '{"connect": false}'
)

_PROMPTS = {
    "concept_ladder": (
        "És um agente de escada conceptual para ensino de ciências. "
        "Dados dois fragmentos, decide se formam um degrau numa progressão pedagógica: "
        "básico (conceito introdutório, sem pré-requisitos), "
        "médio (requer conceitos básicos, aprofunda), "
        "avançado (requer conceitos médios, especialização). "
        "Atribui um nível a cada fragmento e decide se formam um par pedagogicamente útil.\n\n"
        + _INSTRUCTION
    ),
}

_TYPES = {"concept_ladder": "pedagogical:concept_ladder"}

AGENTS = {name: _make_agent(_PROMPTS, _TYPES, name) for name in _PROMPTS}
