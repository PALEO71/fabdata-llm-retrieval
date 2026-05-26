# fabdata-llm-retrieval

Personal RAG system for a Portuguese science communicator — built on SQLite + FTS5, with an MCP server, a phased ingestion pipeline, and a 17-agent connection layer.

## Overview

This repository contains two systems:

| System | Backend | Purpose |
|---|---|---|
| `fdllmret` | Redis + OpenAI embeddings | General document catalogue RAG (original) |
| `scirag` | SQLite + FTS5 + embeddings | Personal knowledge base for science writing and research |

The `scirag` system is the primary focus. It follows Karpathy's **accumulation model**: knowledge is compiled into the database at ingest and connection time, so queries are fast synthesis over pre-digested material rather than retrieval-then-generate at runtime.

## Three Writing Modes

All content in `scirag` is tagged to one of three registers:

| Mode | Context | Typical output |
|---|---|---|
| `divulgacao` | Science communication, opinion columns | 600-word lede-driven piece (Sul Informação style) |
| `pedagogico` | Workshops, classrooms | Scaffolded concept sequence |
| `investigacao` | Paleontology research practice | Cited synthesis with hedged claims |

## Architecture

```
scirag/
├── db.py              SQLite connection, migrations, FTS5 triggers
├── embed.py           Embedding storage/retrieval (numpy float32 BLOB)
├── ingest/            Phased ingestion pipeline (4 tiers)
├── connections/       17-agent connection layer
├── wiki/              Wiki compiler + 8 seed themes
└── mcp/server.py      FastMCP server exposing 8 tools
```

### Database Schema

Six tables:

- **nodes** — atomic content units (chunks, notes, figure captions); carries `writing_mode`, `tier`, `embedding`
- **sources** — documents, articles, field notes, columns
- **connections** — typed directed edges between nodes, written by the 17 connection agents
- **wikis** — LLM-compiled thematic Markdown pages, rebuilt from the connection graph
- **syntheses** — persisted on-demand generation outputs
- **figures** — visual assets with bilingual captions, linked to nodes

Full-text search via an FTS5 virtual table (`nodes_fts`) kept in sync with `nodes` by triggers.

### MCP Server — 8 Tools

| Tool | Description |
|---|---|
| `search` | FTS5 keyword, semantic, or hybrid search with optional mode/tier filters |
| `connect` | Explicitly add a typed connection between two nodes |
| `wiki` | Retrieve or recompile a thematic wiki page |
| `synthesize` | Generate a synthesis in a target writing mode |
| `reingest` | Re-chunk and re-embed a source document |
| `random_walk` | Follow connections from a seed node for discovery |
| `pedagogy` | Build a concept ladder (basico → medio → avancado) |
| `voice_match` | Score content against a writing mode register |

### Two-Pass Query Workflow

Defined as a companion skill (`skills/rag_query.md`):

1. **Pass 1 — Orientation:** `search(mode="fts", top_k=20)` + `wiki(theme)` → candidate node set
2. **Pass 2 — Synthesis:** `search(mode="semantic", top_k=5)` within candidates → `synthesize(writing_mode=<resolved>)`

Writing mode is resolved from query language: mentions of "artigo / coluna / Sul Informação" → `divulgacao`; "aula / oficina / alunos" → `pedagogico`; otherwise → `investigacao`.

## Ingestion Pipeline

Tiers run in sequence. Do **not** run all tiers at once.

| Tier | Label | Corpus | Chunk size |
|---|---|---|---|
| 1 | Voice | Published columns, divulgação pieces | ~200 tok |
| 2 | Knowledge | Field notes, algarve-geology KB, paleontology papers | ~500 tok |
| 3 | Pedagogy | Workshop notes, slides, teaching scripts | ~300 tok |
| 4 | Institutional | Formal papers, reports | ~800 tok |

```bash
python scripts/run_ingest.py --tier 1
python scripts/run_ingest.py --tier 2
# etc.
```

## Connection Layer — 17 Agents

Agents run after ingestion is complete, in configurable groups:

**Topical (4):** `geo_paleo`, `ecology_climate`, `territory_place`, `science_history`

**Cross-domain bridges (4):** `science_narrative`, `local_global`, `data_story`, `metaphor_map`

**Place-based (1):** `algarve_anchor`

**Voice & Form (3):** `divulgacao_voice`, `pedagogico_form`, `investigacao_form`

**Temporal & Dialectical (3):** `deep_time`, `tension_finder`, `update_tracker`

**Pedagogical (1):** `concept_ladder`

**Bilingual (1):** `pt_en_bridge`

```bash
python scripts/run_connections.py --group topical
python scripts/run_connections.py --group bridges
python scripts/run_connections.py --all
```

Each agent is given a pair of nodes and returns a typed connection with a one-sentence Portuguese rationale and a confidence weight (0–1).

## Wiki Layer — 8 Seed Themes

Compiled after the connection pass:

| Key | Theme |
|---|---|
| `paleontologia_algarve` | Core paleontology knowledge anchor |
| `geologia_territorio` | Landscape formation, rock types, deep time |
| `comunicacao_ciencia_pt` | The communicator's own practice |
| `tempo_profundo` | Deep time as narrative device |
| `especies_extincao` | Biodiversity, fossil record, conservation |
| `metodos_campo` | Fieldwork protocols, taphonomy, observation |
| `ciencia_cidadania` | Public science, policy, Sul Informação audience |
| `vocabulario_pt_en` | Bilingual terminology bridge |

```bash
python scripts/run_wiki.py --all
python scripts/run_wiki.py --theme paleontologia_algarve
```

## Setup

```bash
uv sync
cp .env.example .env   # add OPENAI_API_KEY, ANTHROPIC_API_KEY
```

Run the MCP server:

```bash
python -m scirag.mcp.server
```

## Dependencies

Core additions beyond the existing `fdllmret` stack:

- `fastmcp>=2.0` — MCP server framework
- `anthropic>=0.30` — connection agents (Claude Haiku for speed)
- `ulid-py>=1.1` — collision-free IDs
- `numpy>=2.0` — already present; used for cosine similarity over embeddings

No vector database extension required. For corpora exceeding ~200 k nodes, add `sqlite-vec`.

## Original fdllmret System

The original Redis-backed system remains intact under `src/fdllmret/`. It handles general document catalogue RAG with Redis JSON/Search, multi-size chunking, OpenAI ada-002 embeddings, and a full chatbot plugin. See the original documentation inline for usage.
