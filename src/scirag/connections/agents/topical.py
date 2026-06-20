from ._base import _make_agent

_INSTRUCTION = (
    "Responde APENAS com JSON válido numa única linha:\n"
    '{"connect": true, "weight": 0.0-1.0, "rationale": "<uma frase em PT>"}\n'
    "ou\n"
    '{"connect": false}'
)

_PROMPTS = {
    "geo_paleo": (
        "És um agente de conexão especializado em paleontologia e geologia portuguesa. "
        "Dados dois fragmentos do corpus de um investigador/comunicador, decide se existe "
        "uma ligação topical: co-ocorrência de formação geológica e táxon fóssil, "
        "estratigrafia e registo fóssil, ou contexto sedimentar e biodiversidade paleontológica.\n\n"
        + _INSTRUCTION
    ),
    "ecology_climate": (
        "És um agente de conexão especializado em ecologia e paleoclima. "
        "Dados dois fragmentos, decide se existe ligação entre evidência paleoclimática "
        "e ecologia presente, ou entre dados fósseis e situação ecológica actual. "
        "Pergunta-te: qual a ponte entre este dado e a realidade ecológica contemporânea?\n\n"
        + _INSTRUCTION
    ),
    "territory_place": (
        "És um agente de conexão geográfico especializado no território do Algarve. "
        "Dados dois fragmentos, decide se ambos se ancoram a uma mesma unidade territorial "
        "(Serra, Barrocal, litoral, estuário, concelho, localidade). "
        "Uma ligação existe quando os dois fragmentos partilham lugar explícito ou implícito.\n\n"
        + _INSTRUCTION
    ),
    "science_history": (
        "És um agente de conexão especializado em história da ciência portuguesa e ibérica. "
        "Dados dois fragmentos, decide se existe ligação histórica: naturalistas esquecidos, "
        "disputas de prioridade, tradições científicas locais, ou evolução do conhecimento "
        "sobre um tema em Portugal.\n\n"
        + _INSTRUCTION
    ),
}

_TYPES = {
    "geo_paleo": "topical:geo_paleo",
    "ecology_climate": "topical:ecology_climate",
    "territory_place": "topical:territory_place",
    "science_history": "topical:science_history",
}

AGENTS = {name: _make_agent(_PROMPTS, _TYPES, name) for name in _PROMPTS}
