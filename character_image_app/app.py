"""
Character Line-Art Prompt Builder
=================================

A small Streamlit app that turns the generic character-image spec
(`character_image_style.schema.json`) into a ready-to-use prompt.

You fill in the form (one field per spec property), click *Compile*,
and the app produces:
  1. the final prompt string (copy/paste into any image tool), and
  2. the populated JSON instance (download or copy).

Optional: if an OPENAI_API_KEY is set in the environment, an extra
"Generate image" button appears and calls OpenAI's image API directly.
Without a key the app works fully in compile-only mode.

Run:
    streamlit run character_image_app/app.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import streamlit as st

# --------------------------------------------------------------------------- #
# Load the locked art-style fingerprint from the schema (single source of truth)
# --------------------------------------------------------------------------- #
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "character_image_style.schema.json"

try:
    SCHEMA = json.loads(SCHEMA_PATH.read_text())
    ART_STYLE = SCHEMA["art_style"]
except (FileNotFoundError, KeyError):
    # Fallback so the app still runs if the schema file is moved.
    ART_STYLE = {
        "line": {"color_primary": "#B026FF", "color_name": "vivid violet / electric purple"}
    }

STROKE_HEX = ART_STYLE["line"]["color_primary"]
STROKE_NAME = ART_STYLE["line"]["color_name"]


# --------------------------------------------------------------------------- #
# Prompt compiler — mirrors `prompt_template.substitution_notes` in the schema
# --------------------------------------------------------------------------- #
def compile_prompt(spec: dict) -> str:
    s = spec["subject"]
    phys, psych, prof = s["physical"], s["psychological"], s["professional"]
    comp = spec["composition"]

    views = comp["views"]["options_used"] or ["front"]
    views_list = ", ".join(views)

    facial = phys["hair"].get("facial_hair", "").strip()
    facial_clause = f" and {facial}" if facial and facial.lower() != "none" else ""

    height = phys["height"]
    height_clause = ""
    if height.get("show_on_drawing") and comp["annotations"]["height_dimension"].get("show"):
        fmt = comp["annotations"]["height_dimension"].get("format", "").strip()
        if fmt:
            height_clause = f", and a small top-left height annotation reading {fmt}"

    title_style = comp["title"]["style"]
    if title_style == "banner":
        title_clause = (
            f'Add a purple top banner with a star icon and the name '
            f'"{s["name"]}" in bold white'
        )
    elif title_style == "bold_label":
        title_clause = f'Add a bold purple name label "{s["name"]}"'
    else:
        title_clause = "No name label"

    return (
        f"Minimalist single-color line-art illustration in a clean architectural "
        f"scale-figure / dimensions.com style. Subject: {s['name']} — "
        f"{prof['occupation']}, {prof['era']}. Draw a full-body figure "
        f"({len(views)} view(s): {views_list}) using uniform-weight {STROKE_NAME} "
        f"({STROKE_HEX}) outline strokes only, NO fills, NO shading, on a pure white "
        f"background. Face is minimal/featureless; identity carried by silhouette, "
        f"{phys['hair'].get('style', '')} hair{facial_clause}, {phys['build']} build "
        f"and {phys['posture']} posture. Wardrobe: {_csv_list(prof['wardrobe'])}. "
        f"Props: {_csv_list(prof['iconic_props'])}. Pose conveys a "
        f"{psych['demeanor']}, {psych['energy_level']} attitude via "
        f"{prof['signature_action_or_pose']}. Include a dashed horizontal ground "
        f"baseline{height_clause}. {title_clause}. Flat 2D orthographic, infographic "
        f"aesthetic. Avoid: any color besides the purple stroke, gradients, "
        f"photorealism, detailed faces."
    )


def _csv_list(values: list[str]) -> str:
    return ", ".join(v for v in values if v) or "none"


# --------------------------------------------------------------------------- #
# Optional image generation (only active if OPENAI_API_KEY is present)
# --------------------------------------------------------------------------- #
def generate_image(prompt: str) -> bytes | None:
    """Call OpenAI's image API. Returns PNG bytes, or None if unavailable."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        import base64

        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        result = client.images.generate(
            model="gpt-image-1", prompt=prompt, size="1024x1536", n=1
        )
        return base64.b64decode(result.data[0].b64_json)
    except Exception as exc:  # surfaced in the UI
        st.error(f"Image generation failed: {exc}")
        return None


# --------------------------------------------------------------------------- #
# UI
# --------------------------------------------------------------------------- #
st.set_page_config(page_title="Character Line-Art Prompt Builder", page_icon="🎭", layout="wide")

st.markdown(
    f"<h1 style='color:{STROKE_HEX}'>🎭 Character Line-Art Prompt Builder</h1>",
    unsafe_allow_html=True,
)
st.caption(
    "Fill in the subject's traits → compile the prompt in the locked purple "
    "line-art style. Style settings are fixed to keep every image in the same series."
)

DEMEANORS = ["calm", "menacing", "charismatic", "shy", "confident", "eccentric", "playful", "brooding"]
ENERGIES = ["static", "composed", "dynamic", "theatrical"]
BUILDS = ["slim", "average", "athletic", "heavyset", "tall_and_lean", "broad"]
POSTURES = ["upright", "hunched", "relaxed", "imposing", "poised", "dynamic"]
VIEW_OPTIONS = ["front", "profile", "signature_action"]

with st.form("spec_form"):
    st.subheader("Identity")
    c1, c2 = st.columns(2)
    name = c1.text_input("Name", placeholder="e.g. Elvis Presley")
    subj_type = c2.selectbox("Type", ["person", "fictional_character", "archetype"])

    st.subheader("Physical")
    p1, p2, p3 = st.columns(3)
    sex = p1.text_input("Sex / gender presentation", placeholder="male / female / …")
    age = p2.text_input("Approx. age", placeholder="late 30s")
    build = p3.selectbox("Build", BUILDS, index=2)

    p4, p5, p6, p7 = st.columns([2, 1, 1, 1])
    height_val = p4.text_input("Height value", placeholder="6'0\"")
    height_unit = p5.selectbox("Unit", ["ft_in", "m", "cm"])
    show_height = p6.checkbox("Show on drawing", value=True)
    height_fmt = p7.text_input("Annotation text", placeholder="6'0\" | 1.83 m")

    p8, p9, p10 = st.columns(3)
    hair_style = p8.text_input("Hair style", placeholder="pompadour")
    hair_length = p9.text_input("Hair length", placeholder="medium")
    facial_hair = p10.text_input("Facial hair", placeholder="sideburns / none")

    posture = st.selectbox("Posture", POSTURES)
    distinguishing = st.text_input("Distinguishing features (comma-separated)", placeholder="high collar, wide belt")

    st.subheader("Psychological")
    ps1, ps2 = st.columns(2)
    demeanor = ps1.selectbox("Demeanor", DEMEANORS, index=2)
    energy = ps2.selectbox("Energy level", ENERGIES, index=2)
    traits = st.text_input("Personality traits (comma-separated)", placeholder="charismatic, flamboyant")
    attitude = st.text_input("Signature attitude", placeholder="showman caught mid-song")

    st.subheader("Professional")
    pr1, pr2 = st.columns(2)
    occupation = pr1.text_input("Occupation", placeholder="rock 'n' roll singer")
    era = pr2.text_input("Era", placeholder="1970s Las Vegas")
    wardrobe = st.text_input("Wardrobe (comma-separated)", placeholder="jumpsuit, deep V-neck, bell-bottoms")
    props = st.text_input("Iconic props (comma-separated)", placeholder="microphone")
    signature_pose = st.text_input("Signature action / pose", placeholder="leaning back singing into a handheld mic")

    st.subheader("Composition")
    cc1, cc2 = st.columns(2)
    views = cc1.multiselect("Views", VIEW_OPTIONS, default=["signature_action"])
    title_style = cc2.selectbox("Name label style", ["bold_label", "banner", "none"])

    submitted = st.form_submit_button("⚡ Compile prompt", use_container_width=True)

# --------------------------------------------------------------------------- #
# Build spec + output
# --------------------------------------------------------------------------- #
if submitted:
    if not name.strip():
        st.warning("Please enter a name.")
        st.stop()

    spec = {
        "art_style": ART_STYLE,
        "subject": {
            "name": name.strip(),
            "type": subj_type,
            "physical": {
                "sex_gender_presentation": sex,
                "approx_age": age,
                "height": {"value": height_val, "unit": height_unit, "show_on_drawing": show_height},
                "build": build,
                "hair": {"style": hair_style, "length": hair_length, "facial_hair": facial_hair},
                "distinguishing_features": [v.strip() for v in distinguishing.split(",") if v.strip()],
                "posture": posture,
            },
            "psychological": {
                "personality_traits": [v.strip() for v in traits.split(",") if v.strip()],
                "demeanor": demeanor,
                "energy_level": energy,
                "signature_attitude": attitude,
            },
            "professional": {
                "occupation": occupation,
                "era": era,
                "wardrobe": [v.strip() for v in wardrobe.split(",") if v.strip()],
                "iconic_props": [v.strip() for v in props.split(",") if v.strip()],
                "signature_action_or_pose": signature_pose,
            },
        },
        "composition": {
            "views": {"count": len(views) or 1, "options_used": views},
            "title": {"style": title_style},
            "annotations": {"height_dimension": {"show": show_height, "format": height_fmt}},
        },
    }

    prompt = compile_prompt(spec)

    st.success("Prompt compiled.")
    st.subheader("📝 Final prompt")
    st.code(prompt, language="text")

    st.subheader("🧩 Populated JSON")
    st.download_button(
        "⬇ Download JSON",
        data=json.dumps(spec, indent=2),
        file_name=f"{name.strip().lower().replace(' ', '_')}_spec.json",
        mime="application/json",
    )
    with st.expander("Show JSON"):
        st.json(spec)

    # Optional image generation
    if os.environ.get("OPENAI_API_KEY"):
        st.subheader("🖼 Generate image")
        if st.button("Generate with OpenAI gpt-image-1"):
            with st.spinner("Generating…"):
                img = generate_image(prompt)
            if img:
                st.image(img, caption=name.strip())
    else:
        st.info(
            "💡 Compile-only mode. Set an `OPENAI_API_KEY` environment variable before "
            "launching to enable an in-app **Generate image** button."
        )
