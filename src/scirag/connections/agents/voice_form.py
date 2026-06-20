from ._base import _make_agent

_INSTRUCTION = (
    "Responde APENAS com JSON válido numa única linha:\n"
    '{"connect": true, "weight": 0.0-1.0, "rationale": "<uma frase em PT>"}\n'
    "ou\n"
    '{"connect": false}'
)

_PROMPTS = {
    "divulgacao_voice": (
        "És um agente de reconhecimento de voz de divulgação científica. "
        "O corpus é de um comunicador de ciência português que escreve para o Sul Informação. "
        "Dados dois fragmentos, decide se ambos partilham o mesmo registo: "
        "abertura forte, analogias concretas, leitor não especialista como destinatário, "
        "ausência de jargão sem explicação. A ligação existe quando são exemplares da mesma voz.\n\n"
        + _INSTRUCTION
    ),
    "pedagogico_form": (
        "És um agente de reconhecimento de forma pedagógica. "
        "Dados dois fragmentos de materiais de ensino ou workshops, decide se existe "
        "uma sequência pedagogicamente lógica: o primeiro fragmento prepara o terreno "
        "para o segundo, ou ambos são degraus numa escada conceptual do mais simples "
        "para o mais complexo.\n\n"
        + _INSTRUCTION
    ),
    "investigacao_form": (
        "És um agente de ligação entre afirmação e evidência no registo académico. "
        "Dados dois fragmentos científicos, decide se um contém uma afirmação ou hipótese "
        "e o outro contém evidência, dados ou argumentação que a suporta ou contraria. "
        "A ligação existe quando um seria citado no outro num texto académico.\n\n"
        + _INSTRUCTION
    ),
}

_TYPES = {
    "divulgacao_voice": "voice:divulgacao",
    "pedagogico_form": "voice:pedagogico",
    "investigacao_form": "voice:investigacao",
}

AGENTS = {name: _make_agent(_PROMPTS, _TYPES, name) for name in _PROMPTS}
