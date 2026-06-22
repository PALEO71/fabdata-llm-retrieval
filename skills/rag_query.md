# Skill: rag_query — Two-Pass Query Workflow

Use this workflow whenever the user asks you to write, research, or synthesise
using their personal corpus (scirag).

---

## Step 0 — Resolve writing mode

| Query signals | Resolved mode |
|---|---|
| "artigo", "coluna", "Sul Informação", "leitor", "divulg" | `divulgacao` |
| "aula", "oficina", "alunos", "exercício", "pedagog" | `pedagogico` |
| anything else | `investigacao` |

---

## Pass 1 — Orientation (broad, fast)

1. Call `search(query=<user query>, mode="fts", top_k=20)`
   - Note the titles and writing_mode values returned.
2. Identify 1–2 candidate wiki themes from the results.
3. Call `wiki(theme=<theme>)` for each candidate.
   - If the wiki returns an error (no content yet), skip and rely on search only.
4. From steps 1–3, collect a shortlist of up to 15 node IDs.

---

## Pass 2 — Synthesis (precise)

5. Call `search(query=<user query>, mode="semantic", top_k=5)`
   - These are the highest-signal nodes.
6. Merge with the Pass 1 shortlist; deduplicate.
7. Call `synthesize(query=<user query>, writing_mode=<resolved>, node_ids=<JSON array of IDs>)`
8. Optional — serendipity check:
   - Call `random_walk(seed_id=<top node from step 5>, steps=3)`
   - If the walk returns unexpected but relevant nodes, note them for the user.
9. Optional — register calibration:
   - Call `voice_match(content=<draft paragraph>, target_mode=<resolved>)`
   - Apply the style_notes to the final output.

---

## Output rules

- Always tell the user which writing mode was resolved and why.
- If fewer than 3 nodes were found, say so before synthesising — the corpus may need more content in that mode.
- Do not invent facts not present in the nodes. If the corpus is silent on a point, say so.
- Pedagogical outputs: include the concept ladder from `pedagogy()` if the user is preparing a class.

---

## Quick reference — tool call order

```
search(fts) → wiki(themes) → search(semantic) → synthesize
                                               ↘ random_walk (optional)
                                               ↘ voice_match  (optional)
```
