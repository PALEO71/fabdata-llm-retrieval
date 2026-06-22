# SCIRAG — Referência Técnica Completa
*Sistema RAG pessoal para comunicador e investigador de ciência português*
*Gerado em 22/06/2026*

---

## O QUE É O SCIRAG

**Scirag** é um sistema de recuperação e síntese de informação (RAG — Retrieval-Augmented Generation) pessoal, construído sobre documentos e textos do próprio utilizador. Permite ao Claude Desktop pesquisar semanticamente num corpus pessoal antes de escrever ou responder.

### Função principal
Quando escreves uma pergunta no Claude Desktop, o scirag:
1. Procura nos teus documentos os fragmentos mais relevantes (busca FTS5 + reranking semântico)
2. Entrega esses fragmentos ao Claude como contexto
3. O Claude escreve a resposta usando **as tuas fontes**, no **teu estilo**

### Casos de uso
- Escrever artigos científicos com referências do teu corpus bibliográfico
- Escrever colunas de divulgação (Sul Informação, etc.) com as tuas notas e leituras
- Recuperar informação de formações, workshops e materiais pedagógicos
- Fazer sínteses temáticas sobre paleontologia, geologia, comunicação de ciência
- Ligar fragmentos de diferentes fontes que nunca tinhas relacionado

---

## ONDE ESTÁ INSTALADO

| Componente | Localização |
|---|---|
| **Código fonte** | `C:\Users\hvieira\fabdata-llm-retrieval\` |
| **Base de dados** | `C:\Users\hvieira\scirag.db` |
| **Gestor de pacotes** | `uv` (sempre usar `uv run python`, nunca `python` direto) |
| **Configuração MCP** | `C:\Users\hvieira\AppData\Roaming\Claude\claude_desktop_config.json` |
| **Branch git** | `claude/portuguese-science-rag-w6DHw` |
| **Repositório remoto** | `paleo71/fabdata-llm-retrieval` |

### Estrutura do código
```
C:\Users\hvieira\fabdata-llm-retrieval\
├── src/scirag/
│   ├── ingest/pipeline.py       ← ingere documentos → chunks → embeddings
│   ├── mcp/server.py            ← servidor MCP (8 ferramentas para Claude Desktop)
│   ├── wiki/compiler.py         ← compila páginas wiki temáticas
│   ├── connections/agents/      ← 17 agentes que ligam chunks entre si
│   ├── embed.py                 ← embeddings locais (sentence-transformers)
│   ├── db.py                    ← ligação SQLite
│   └── schema.sql               ← estrutura da base de dados
├── scripts/
│   ├── run_ingest.py            ← ingere uma pasta de documentos
│   ├── run_connections.py       ← corre agentes de ligação
│   └── run_wiki.py              ← compila páginas wiki
├── GUIA_2ND_BRAIN.md            ← guia de uso do 2nd Brain (PT + EN)
└── pyproject.toml               ← dependências do projeto
```

---

## ARQUITECTURA TÉCNICA

| Componente | Tecnologia | Detalhe |
|---|---|---|
| Base de dados | SQLite + FTS5 | Busca textual + armazenamento local |
| Embeddings | sentence-transformers | `paraphrase-multilingual-mpnet-base-v2` (multilíngue, 1.1GB, corre localmente) |
| Servidor MCP | FastMCP 2.x | Transporte STDIO, 8 ferramentas |
| Síntese / Wiki | Claude Sonnet | `claude-sonnet-4-6` |
| Agentes de ligação | Claude Haiku | `claude-haiku-4-5-20251001` |
| Gestão de pacotes | uv | Ambiente virtual isolado |

### Tiers (categorias de conteúdo)
| Tier | Modo | Chunk size | Tipo de conteúdo |
|---|---|---|---|
| 1 | divulgacao | 200 tokens | Colunas Sul Informação, textos de divulgação |
| 2 | investigacao | 500 tokens | Artigos científicos, bibliografia, investigação |
| 3 | pedagogico | 300 tokens | Formações, workshops, materiais didáticos |
| 4 | investigacao | 800 tokens | Documentos institucionais longos |

### Temas wiki compilados (8)
`paleontologia_algarve` · `geologia_territorio` · `comunicacao_ciencia_pt` · `tempo_profundo` · `especies_extincao` · `metodos_campo` · `ciencia_cidadania` · `vocabulario_pt_en`

### Grupos de agentes de ligação (7)
`topical` · `bridges` · `place` · `voice_form` · `temporal` · `pedagogical` · `bilingual`

---

## CORPUS INGERIDO (estado em 22/06/2026)

| Pasta | Tier | Conteúdo |
|---|---|---|
| `C:\LUIS\2026\FORMACAO GEO PALEO BLUEFLEET` | 3 (pedagógico) | Formação geologia/paleontologia Bluefleet → 37 nodes |
| `D:\A REPOR\PEGADAS LUZ SET 2022` | 2 (investigação) | Bibliografia artigo pegadas saurópode Praia da Luz → 241 fontes |
| *(outros)* | 2 | Geologia geral → 663 nodes (ingestão anterior) |

**Total aproximado:** ~900+ nodes na base de dados

---

## INSTALAÇÃO — ETAPAS REALIZADAS

### 1. Clonar o repositório
```bash
cd C:\Users\hvieira
git clone <repo> fabdata-llm-retrieval
cd fabdata-llm-retrieval
git checkout claude/portuguese-science-rag-w6DHw
```

### 2. Instalar dependências
```bash
uv sync
```
Dependências principais: `fastmcp`, `anthropic`, `sentence-transformers`, `tiktoken`, `pymupdf`, `pypdf`, `python-pptx`, `python-docx`, `numpy`

### 3. Configurar API key
Criar ficheiro `.env` na raiz do projeto:
```
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### 4. Criar base de dados
```bash
uv run python -c "from src.scirag.db import get_conn; get_conn()"
```

### 5. Configurar Claude Desktop (MCP)
Editar `C:\Users\hvieira\AppData\Roaming\Claude\claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "scirag": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\hvieira\\fabdata-llm-retrieval",
        "run",
        "python",
        "-m",
        "scirag.mcp.server"
      ],
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-api03-..."
      }
    }
  }
}
```
Reiniciar o Claude Desktop. O scirag aparece em **Conectores** com toggle azul.

---

## COMANDOS DO DIA-A-DIA

### Ingerir uma nova pasta de documentos
```bash
cd C:\Users\hvieira\fabdata-llm-retrieval
uv run python scripts/run_ingest.py --tier 2 --folder "D:\caminho\para\pasta"
```
- `--tier 1` → divulgação · `--tier 2` → investigação · `--tier 3` → pedagógico
- Ficheiros já ingeridos são automaticamente ignorados (`skip_existing=True`)
- Ficheiros vazios (0 bytes) e corrompidos são ignorados sem abortar

### Correr agentes de ligação (após nova ingestão)
```bash
uv run python scripts/run_connections.py --group topical
uv run python scripts/run_connections.py --group bridges
uv run python scripts/run_connections.py --group place
```
*(Usa Claude Haiku — custo baixo, ~$0.10–0.20 por grupo)*

### Recompilar wiki (após nova ingestão)
```bash
uv run python scripts/run_wiki.py --all
```
*(Usa Claude Sonnet — corre rápido, ~2 min para os 8 temas)*

### Atualizar código (pull do repositório)
```bash
git pull origin claude/portuguese-science-rag-w6DHw
```

---

## FORMATOS DE FICHEIROS SUPORTADOS

`.pdf` · `.txt` · `.md` · `.pptx` · `.docx`

Nota: ficheiros `~$*.docx` (ficheiros de bloqueio temporários do Word) são automaticamente ignorados.

---

## AS 8 FERRAMENTAS MCP (visíveis no Claude Desktop)

| Ferramenta | O que faz |
|---|---|
| `search` | Busca semântica + FTS5 no corpus |
| `synthesize` | Gera síntese sobre um tema usando os fragmentos encontrados |
| `get_wiki` | Lê uma página wiki compilada |
| `list_wikis` | Lista os temas wiki disponíveis |
| `get_source` | Recupera o texto completo de uma fonte |
| `list_sources` | Lista fontes ingeridas (com filtros) |
| `get_connections` | Mostra ligações entre um node e outros |
| `stats` | Estatísticas da base de dados (nodes, sources, wikis) |

---

## INTEGRAÇÃO COM O 2ND BRAIN

O scirag corre **em paralelo** com o 2nd Brain (`C:\Users\hvieira\second-brain\`):

```
Adicionas um documento
        │
        ├── sb-capture / sb-sync → wiki do 2nd Brain (leitura humana)
        │
        └── scirag ingest → base de dados RAG (pesquisa semântica)
```

Depois de um `sb-sync`, correr também:
```bash
uv run python scripts/run_ingest.py --tier 1 --folder "C:\Users\hvieira\second-brain\sources"
```

---

## CUSTOS API (estimativa)

| Operação | Modelo | Custo estimado |
|---|---|---|
| Ingestão de documentos | Nenhum (embeddings locais) | $0.00 |
| Agentes de ligação (por grupo) | Haiku | ~$0.05–0.20 |
| Compilação wiki (8 temas) | Sonnet | ~$0.10–0.30 |
| Cada pergunta no Claude Desktop | Sonnet (síntese) | ~$0.01–0.05 |

Os embeddings correm **localmente** — sem custo e sem enviar texto para a internet.

---

## PROXIMOS PASSOS PENDENTES

- [ ] Ingerir Tier 1 — colunas de divulgação (Sul Informação e outros)
- [ ] Ingerir Tier 3 — materiais pedagógicos de outros workshops
- [ ] Correr grupos de ligação: `voice_form`, `temporal`, `pedagogical`, `bilingual`
- [ ] Escrever artigo científico das pegadas de saurópode da Praia da Luz usando scirag

---

*Sistema construído por Claude Code (Anthropic) em junho de 2026 para Luís Azevedo Rodrigues / Centro Ciência Viva de Lagos*
