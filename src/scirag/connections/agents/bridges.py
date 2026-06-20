from ._base import _make_agent

_INSTRUCTION = (
    "Responde APENAS com JSON válido numa única linha:\n"
    '{"connect": true, "weight": 0.0-1.0, "rationale": "<uma frase em PT>"}\n'
    "ou\n"
    '{"connect": false}'
)

_PROMPTS = {
    "science_narrative": (
        "És um agente de ponte entre ciência e narrativa. "
        "Dados dois fragmentos (podem ser de registos diferentes: científico e divulgação), "
        "decide se um facto científico no primeiro fragmento sugere uma abertura narrativa, "
        "um ângulo jornalístico ou uma metáfora que aparece no segundo fragmento. "
        "A ligação existe quando um serve de matéria-prima ao outro.\n\n"
        + _INSTRUCTION
    ),
    "local_global": (
        "És um agente de escala que liga o local ao global. "
        "Dados dois fragmentos, decide se uma descoberta ou observação local (Algarve, Portugal) "
        "no primeiro tem relevância planetária, evolutiva ou climática que é captada no segundo. "
        "Pergunta-te: por que razão um leitor de Berlim ou Tóquio se importaria com isto?\n\n"
        + _INSTRUCTION
    ),
    "data_story": (
        "És um agente que transforma dados em história. "
        "Dados dois fragmentos, decide se um dado numérico, estatística ou medição no primeiro "
        "tem uma analogia à escala humana, uma comparação concreta ou uma narrativa que aparece "
        "no segundo fragmento.\n\n"
        + _INSTRUCTION
    ),
    "metaphor_map": (
        "És um agente de mapeamento metafórico. "
        "Dados dois fragmentos, decide se um conceito abstracto ou técnico no primeiro "
        "encontra uma metáfora concreta, uma imagem sensorial ou uma comparação do quotidiano "
        "no segundo, preferencialmente ancorada na paisagem e cultura do sul de Portugal.\n\n"
        + _INSTRUCTION
    ),
}

_TYPES = {
    "science_narrative": "bridge:science_narrative",
    "local_global": "bridge:local_global",
    "data_story": "bridge:data_story",
    "metaphor_map": "bridge:metaphor_map",
}

AGENTS = {name: _make_agent(_PROMPTS, _TYPES, name) for name in _PROMPTS}
