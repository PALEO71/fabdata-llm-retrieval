from ._base import _make_agent

_INSTRUCTION = (
    "Responde APENAS com JSON válido numa única linha:\n"
    '{"connect": true, "weight": 0.0-1.0, "rationale": "<uma frase em PT>"}\n'
    "ou\n"
    '{"connect": false}'
)

_PROMPTS = {
    "deep_time": (
        "És um agente de tempo profundo. "
        "Dados dois fragmentos, decide se um ancora numa escala temporal geológica "
        "(milhões de anos, eras, períodos, épocas) e o outro oferece uma tradução "
        "dessa escala para tempo humano — uma história, uma analogia, uma comparação concreta. "
        "A ligação existe quando um serve de escala e o outro de ponte narrativa.\n\n"
        + _INSTRUCTION
    ),
    "tension_finder": (
        "És um agente de contradições e tensões intelectuais. "
        "Dados dois fragmentos do corpus do mesmo investigador, decide se existe "
        "uma contradição, uma tensão ou uma evolução de posição entre eles: "
        "identificações taxonómicas conflituantes, estimativas de idade divergentes, "
        "interpretações opostas, ou uma posição mais antiga que foi revisitada. "
        "Não procures perfeição — pequenas tensões produtivas são mais valiosas que contradições óbvias.\n\n"
        + _INSTRUCTION
    ),
    "update_tracker": (
        "És um agente de rastreamento de conhecimento. "
        "Dados dois fragmentos, decide se o segundo supera, revisa ou actualiza "
        "informação contida no primeiro. A ligação 'supersedes' existe quando o segundo "
        "fragmento tornaria o primeiro parcialmente obsoleto se publicados juntos.\n\n"
        + _INSTRUCTION
    ),
}

_TYPES = {
    "deep_time": "temporal:deep_time",
    "tension_finder": "temporal:tension",
    "update_tracker": "temporal:supersedes",
}

AGENTS = {name: _make_agent(_PROMPTS, _TYPES, name) for name in _PROMPTS}
