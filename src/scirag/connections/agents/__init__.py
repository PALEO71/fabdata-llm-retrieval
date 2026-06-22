from .topical import AGENTS as _T
from .bridges import AGENTS as _B
from .place import AGENTS as _PL
from .voice_form import AGENTS as _VF
from .temporal import AGENTS as _TMP
from .pedagogical import AGENTS as _PED
from .bilingual import AGENTS as _BIL

REGISTRY: dict = {**_T, **_B, **_PL, **_VF, **_TMP, **_PED, **_BIL}
