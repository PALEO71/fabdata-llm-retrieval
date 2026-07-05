# Character Line-Art Prompt Builder — Project Document

**Repository:** `PALEO71/fabdata-llm-retrieval`
**Branch:** `claude/character-image-json-schema-57z2xi`
**Document date:** 2026-07-05
**Directed by:** Laz Rodrigues (laz.rodrigues@gmail.com)
**Implemented by:** Claude (model `claude-opus-4-8`), Anthropic Claude Code

---

## 1. What the app is

The **Character Line-Art Prompt Builder** turns a person's or fictional
character's traits into a ready-to-use image-generation prompt that reproduces a
specific artistic style: **minimalist single-color (electric purple `#B026FF`)
line-art figures** in the "dimensions.com" architectural scale-figure look —
clean outline strokes, no fills or shading, largely featureless faces, a dashed
ground baseline, an optional height annotation, and an optional name banner or
label.

The core idea is a **separation of concerns**:

- the **art style** is fixed (locked to keep every image in one consistent
  series), while
- the **subject** — described through *physical*, *psychological* and
  *professional* traits — is what the user edits.

A set of mapping rules then translates those traits into concrete drawing
features (silhouette, wardrobe, props, pose, composition). Swap the traits, keep
the style, and recognizability comes "for free".

### How it works, end to end

1. The style and field structure live in the generic spec
   `character_image_style.schema.json`.
2. The user fills in a **form** (one field per spec property).
3. A **compile** step assembles the fields into a single prompt string
   (mirroring the spec's `prompt_template` substitution rules), plus a populated
   JSON instance.
4. The prompt is copied/pasted into any image tool — or, optionally, sent
   directly to an image API to render the picture.

### Feature summary

| Feature | Streamlit app (`app.py`) | Mobile HTML (`index.html`) |
|---|---|---|
| Form with physical/psychological/professional/composition fields | ✅ | ✅ |
| Compile to final prompt string | ✅ | ✅ |
| Populated JSON view + download | ✅ | ✅ |
| Locked art-style fingerprint (read from schema) | ✅ | ✅ (embedded) |
| Copy-to-clipboard buttons | — | ✅ |
| Remembers last entry (localStorage) | — | ✅ |
| One-tap presets (Elvis / Dracula / Darwin) | — | ✅ |
| Optional image generation | ✅ (env `OPENAI_API_KEY`) | ✅ (bring-your-own-key, client-side) |
| Runtime needed | Python + Streamlit | Just a browser (offline-capable) |

---

## 2. Files

```
character_image_style.schema.json     # the generic, reusable style + subject spec
character_image_app/
├── index.html                        # mobile-first single-file builder (latest front-end)
├── app.py                            # desktop Streamlit builder
├── README.md                         # how to run both front-ends
└── PROJECT_HISTORY.md                # this document
```

---

## 3. Chronological & authorship version sequence

All work was **directed by Laz Rodrigues** and **implemented by Claude
(`claude-opus-4-8`)** in a single Claude Code session on 2026-06-30. Each entry
below corresponds to one commit on branch
`claude/character-image-json-schema-57z2xi`.

| # | Date & time (UTC) | Commit | Author / Co-author | Milestone | User request that drove it |
|---|---|---|---|---|---|
| v1 | 2026-06-30 06:47 | `6e00bb1` | Claude (`claude-opus-4-8`) | **Generic JSON spec** — `character_image_style.schema.json`: art-style fingerprint, subject traits (physical/psychological/professional), feature-mapping rules, prompt template, and a worked Dracula example. | "Create a generic JSON to create images following the artistic style … based on the physical, psychological and professional characteristics." |
| v2 | 2026-06-30 07:25 | `a563e7c` | Claude (`claude-opus-4-8`) | **Streamlit app** — `app.py` + `README.md`: form UI, compile-to-prompt, JSON download, style read from the schema, optional image generation via `OPENAI_API_KEY`. | "I want an APP with the generic JSON in it with different fields to be manually inserted that after being filled generate an image." (Chosen: compile-only + Streamlit.) |
| v3 | 2026-06-30 07:41 | `2a35bf9` | Claude (`claude-opus-4-8`) | **Mobile HTML** — `index.html`: single self-contained file, same fields and identical compile logic (prompt parity verified), responsive layout, copy buttons, JSON download, localStorage persistence, optional bring-your-own-key client-side image generation. | "Is [it] possible to make an HTML with the same features? I should like to use it in mobile." |
| v4 | 2026-06-30 07:43 | `4cbecbc` | Claude (`claude-opus-4-8`) | **One-tap presets** — Elvis Presley, Dracula, Charles Darwin (+ Clear) chips that fill the whole form in one tap; session-restore refactored into a shared `applySpec()`; all presets verified to compile correctly. | "Do it." (Approving the offer to add preset characters.) |

**Authorship note.** Commits are recorded in git with author *Claude* and the
trailer `Co-Authored-By: Claude Opus 4.8`. The human author/director of the work
is **Laz Rodrigues**, who specified every requirement; Claude produced the code,
tests, and documentation. Model identity (`claude-opus-4-8`) is included here for
provenance at the user's explicit request.

---

## 4. Verification performed

- **v1:** JSON validated as well-formed (`json.load`).
- **v2:** `app.py` byte-compiled; `compile_prompt()` smoke-tested on the Elvis
  case.
- **v3:** JavaScript `compilePrompt()` output checked for **byte-for-byte
  parity** with the Python compiler on the same input.
- **v4:** All three presets executed through the compiler; each produced a
  correct, complete prompt (views, wardrobe, props, pose, title style, height
  annotation).

---

## 5. Possible next steps (not yet done)

- Mirror the presets into the Streamlit app as a dropdown.
- Publish `index.html` via GitHub Pages for a permanent, "Add to Home Screen"
  mobile URL (requires merging the branch to the default branch first).
- Add more presets, or a second art-style variant (e.g. shaded / two-tone).
