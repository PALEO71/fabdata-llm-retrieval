# Character Line-Art Prompt Builder

A small [Streamlit](https://streamlit.io) app that turns the generic spec in
[`../character_image_style.schema.json`](../character_image_style.schema.json)
into a ready-to-use image prompt.

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
