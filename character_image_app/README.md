# Character Line-Art Prompt Builder

Turns the generic spec in
[`../character_image_style.schema.json`](../character_image_style.schema.json)
into a ready-to-use image prompt. Two interchangeable front-ends, same logic:

| File | Best for | Needs |
|------|----------|-------|
| [`index.html`](index.html) | **Mobile / phone**, offline, zero install | just a browser |
| [`app.py`](app.py) | Desktop / Python users | `pip install streamlit` |

## Mobile (HTML) — recommended for phones

`index.html` is a single self-contained file (no server, no build). Use it by either:

- **Opening it directly** — email/AirDrop/save the file to your phone and open it
  in your browser; or
- **Hosting it** anywhere static (GitHub Pages, Netlify, or any web server) and
  bookmarking the URL — then "Add to Home Screen" for an app-like icon.

It's mobile-first (responsive layout, 16px inputs to avoid iOS zoom, copy-to-clipboard
buttons, and it remembers your last entry via the browser). It has the **same fields**
as the Streamlit version, compiles the **same prompt**, and can download the JSON.

**One-tap presets:** chips at the top load a fully filled-in **Elvis Presley**,
**Dracula**, or **Charles Darwin** (and a **Clear** button) — so on a phone you can
load an example and just tweak a few fields instead of typing everything.

It also includes an optional collapsible **Generate image** section where you paste
*your own* OpenAI key (kept in your browser's localStorage, sent directly to OpenAI) —
leave it blank to stay in compile-only mode.

## Desktop (Streamlit)

Fill in the form (physical / psychological / professional traits), click
**Compile prompt**, and you get:

1. **The final prompt string** — copy/paste into any image tool.
2. **The populated JSON instance** — view or download.

The purple line-art *style* is locked (read from the schema's `art_style`
block) so every character comes out in the same consistent series.

## Run

```bash
pip install streamlit          # only dependency for compile-only mode
streamlit run character_image_app/app.py
```

Then open the URL Streamlit prints (default http://localhost:8501).

## Optional: in-app image generation

The app runs in **compile-only mode** by default (no API key needed).
If you set an OpenAI key before launching, a **Generate image** button
appears and calls `gpt-image-1` directly:

```bash
pip install openai
export OPENAI_API_KEY=sk-...
streamlit run character_image_app/app.py
```

## How it works

- `art_style` is read from the schema — the fixed look (purple `#B026FF`
  strokes, no fills/shading, blank faces, dashed baseline).
- The form collects the `subject` and `composition` fields.
- `compile_prompt()` mirrors the schema's `prompt_template.substitution_notes`,
  including the conditional height annotation and title-label clauses.
