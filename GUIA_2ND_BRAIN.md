# Guia do Segundo Cérebro / Second Brain Guide
### Para o Luís — escrito como se tivesses 14 anos / Written as if you were 14

---

# PARTE 1 — PORTUGUÊS

## O que é o Segundo Cérebro?

Imagina que tens uma pasta física em casa onde guardas todos os artigos, recortes de jornal, anotações e livros que leste. Quando precisas de escrever um texto sobre dinossauros do Algarve, vais à pasta, encontras tudo o que já leste sobre o tema e usas isso para escrever melhor.

O **Segundo Cérebro** é essa pasta — mas no computador, organizada, com memória e ligada ao Claude.

Está guardado em: `C:\Users\hvieira\second-brain\`

---

## Como está organizado por dentro?

```
second-brain/
├── sources/        ← aqui ficam os documentos que adicionas (NUNCA editar)
├── wiki/           ← aqui o Claude escreve páginas de conhecimento
│   ├── Index.md    ← o índice de tudo
│   ├── recaps/     ← resumos semanais
│   └── [páginas de temas]
└── log.md          ← diário do que entrou e quando
```

**Regra de ouro:** A pasta `sources/` é como uma biblioteca pública — podes adicionar livros mas nunca os riscar nem mover.

---

## As 4 ferramentas (skills)

### 1. `sb-capture` — Adicionar UMA coisa
**Quando usar:** Encontraste um artigo, PDF, vídeo ou texto interessante e queres guardar.

**O que faz:**
- Guarda o conteúdo em `sources/` com a data de hoje
- O Claude lê e atualiza as páginas wiki afetadas
- Fica tudo ligado e citado

**Como usar no Claude Desktop:**
1. Abre uma conversa nova
2. Cola o texto, o link ou arrasta o ficheiro
3. Escreve: *"Captura isto para o meu segundo cérebro"*
4. O Claude usa o skill `sb-capture` e faz tudo automaticamente

---

### 2. `sb-sync` — Adicionar MUITAS coisas de uma vez
**Quando usar:** Tens 10 PDFs que queres adicionar de uma vez, sem fazer um por um.

**O que faz:**
- Verifica quais os ficheiros em `sources/` que ainda não foram processados
- Processa todos por ordem, do mais antigo para o mais recente
- Atualiza a wiki com tudo de uma vez no final

**Como usar:**
1. Copia os ficheiros (PDFs, Word, etc.) para `C:\Users\hvieira\second-brain\sources\`
2. No Claude Desktop escreve: *"Faz um sync do meu segundo cérebro"*
3. Espera — pode demorar alguns minutos dependendo de quantos ficheiros há

---

### 3. `sb-digest` — Resumo semanal
**Quando usar:** Ao fim de semana, para ver o que entrou na semana.

**O que faz:**
- Lê o `log.md` dos últimos 7 dias
- Escreve um resumo em `wiki/recaps/AAAA-Wxx-recap.md`
- Mostra ligações entre temas que não tinhas visto

**Como usar:**
- No Claude Desktop escreve: *"Faz o digest semanal do meu segundo cérebro"*
- Lê o resumo e fica a par do que o teu cérebro aprendeu esta semana

---

### 4. `sb-lint` — Limpeza e manutenção
**Quando usar:** Uma vez por mês, para manter tudo saudável.

**O que faz:**
- Verifica se há afirmações sem fonte citada
- Encontra páginas "órfãs" (sem ligações a outras)
- Lista páginas com mais de 90 dias sem atualização
- Mostra contradições para tu decidires

**Como usar:**
- No Claude Desktop escreve: *"Faz um lint/auditoria do meu segundo cérebro"*
- O Claude dá-te um relatório — tu decides o que fazer com cada problema

---

## Rotina recomendada

### Todos os dias (2 minutos)
- Se encontraste algo interessante → usa `sb-capture`

### Todas as semanas (domingo, 10 minutos)
- Tens novos ficheiros em massa → usa `sb-sync`
- Lê o que entrou → usa `sb-digest`

### Todo o mês (30 minutos)
- Mantém tudo limpo → usa `sb-lint`

---

## Como ligar o 2nd Brain ao RAG (scirag)?

O scirag é o motor de busca inteligente que trabalha **em paralelo** com o 2nd Brain:

```
Adicionas um documento
        │
        ├── sb-capture/sb-sync → wiki do 2nd Brain (leitura humana)
        │
        └── scirag ingest → base de dados do RAG (pesquisa semântica)
```

**Depois de um sb-sync, corre também:**
```
uv run python scripts/run_ingest.py --tier 1 --folder "C:\Users\hvieira\second-brain\sources"
```

Assim o Claude pode não só ler a wiki, mas também **pesquisar semanticamente** em tudo o que escreveste e leste.

---

## Exemplo prático completo

**Situação:** Encontraste um artigo científico sobre pegadas de dinossauros no Algarve.

**Passo 1 — Adicionar ao 2nd Brain:**
- Arrasta o PDF para uma conversa no Claude Desktop
- Escreves: *"Captura este artigo para o meu segundo cérebro"*
- O Claude guarda-o em `sources/` e atualiza a wiki de paleontologia

**Passo 2 — Adicionar ao RAG:**
- No terminal: `uv run python scripts/run_ingest.py --tier 2 --folder "C:\Users\hvieira\second-brain\sources"`
- O artigo fica disponível para pesquisa semântica

**Passo 3 — Usar para escrever:**
- No Claude Desktop: *"Quero escrever uma coluna para o Sul Informação sobre pegadas de dinossauros"*
- O Claude usa o scirag para encontrar os melhores fragmentos do teu corpus
- Escreve no teu estilo, com as tuas fontes

---

---

# PART 2 — ENGLISH

## What is the Second Brain?

Imagine you have a physical folder at home where you keep all the articles, newspaper clippings, notes and books you've read. When you need to write about Algarve dinosaurs, you go to the folder, find everything you've already read on the topic, and use it to write better.

The **Second Brain** is that folder — but on the computer, organised, with memory, and connected to Claude.

Stored at: `C:\Users\hvieira\second-brain\`

---

## How is it organised inside?

```
second-brain/
├── sources/        ← documents you add (NEVER edit these)
├── wiki/           ← pages of knowledge Claude writes for you
│   ├── Index.md    ← the index of everything
│   ├── recaps/     ← weekly summaries
│   └── [topic pages]
└── log.md          ← diary of what came in and when
```

**Golden rule:** The `sources/` folder is like a public library — you can add books but never scribble on them or move them.

---

## The 4 tools (skills)

### 1. `sb-capture` — Add ONE thing
**When to use:** You found an article, PDF, video or text and want to save it.

**What it does:**
- Saves content in `sources/` with today's date
- Claude reads it and updates the affected wiki pages
- Everything is linked and cited

**How to use in Claude Desktop:**
1. Open a new conversation
2. Paste the text, link, or drag in the file
3. Write: *"Capture this for my second brain"*
4. Claude uses the `sb-capture` skill and does everything automatically

---

### 2. `sb-sync` — Add MANY things at once
**When to use:** You have 10 PDFs to add at once, without doing them one by one.

**What it does:**
- Checks which files in `sources/` haven't been processed yet
- Processes them all in order, oldest first
- Updates the wiki with everything at the end

**How to use:**
1. Copy files (PDFs, Word docs, etc.) to `C:\Users\hvieira\second-brain\sources\`
2. In Claude Desktop write: *"Sync my second brain"*
3. Wait — may take a few minutes depending on how many files there are

---

### 3. `sb-digest` — Weekly summary
**When to use:** At the weekend, to see what came in during the week.

**What it does:**
- Reads `log.md` from the last 7 days
- Writes a summary in `wiki/recaps/YYYY-Wxx-recap.md`
- Shows connections between topics you hadn't noticed

**How to use:**
- In Claude Desktop write: *"Do the weekly digest for my second brain"*
- Read the summary and stay on top of what your brain learned this week

---

### 4. `sb-lint` — Cleaning and maintenance
**When to use:** Once a month, to keep everything healthy.

**What it does:**
- Checks for claims without a cited source
- Finds "orphan" pages (no links to others)
- Lists pages not updated for more than 90 days
- Shows contradictions for you to decide on

**How to use:**
- In Claude Desktop write: *"Lint/audit my second brain"*
- Claude gives you a report — you decide what to do with each issue

---

## Recommended routine

### Every day (2 minutes)
- Found something interesting → use `sb-capture`

### Every week (Sunday, 10 minutes)
- Have new files in bulk → use `sb-sync`
- See what came in → use `sb-digest`

### Every month (30 minutes)
- Keep everything clean → use `sb-lint`

---

## How to connect the 2nd Brain to the RAG (scirag)?

Scirag is the intelligent search engine that works **in parallel** with the 2nd Brain:

```
You add a document
        │
        ├── sb-capture/sb-sync → 2nd Brain wiki (human reading)
        │
        └── scirag ingest → RAG database (semantic search)
```

**After an sb-sync, also run:**
```
uv run python scripts/run_ingest.py --tier 1 --folder "C:\Users\hvieira\second-brain\sources"
```

This way Claude can not only read the wiki, but also **semantically search** everything you've written and read.

---

## Complete practical example

**Situation:** You found a scientific article about dinosaur footprints in the Algarve.

**Step 1 — Add to 2nd Brain:**
- Drag the PDF into a Claude Desktop conversation
- Write: *"Capture this article for my second brain"*
- Claude saves it in `sources/` and updates the palaeontology wiki

**Step 2 — Add to RAG:**
- In terminal: `uv run python scripts/run_ingest.py --tier 2 --folder "C:\Users\hvieira\second-brain\sources"`
- The article becomes available for semantic search

**Step 3 — Use it to write:**
- In Claude Desktop: *"I want to write a column for Sul Informação about dinosaur footprints"*
- Claude uses scirag to find the best fragments from your corpus
- Writes in your style, with your sources

---

*Guia criado em 21/06/2026 — Sistema scirag + 2nd Brain de Luís Azevedo Rodrigues*
