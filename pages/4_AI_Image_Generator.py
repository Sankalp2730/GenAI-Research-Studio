
import os
import base64
import io
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Image Generator | GenAI Research Studio",
    page_icon="🎨",
    layout="wide",
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

OUTPUT_DIR = PROJECT_ROOT / "data" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# STYLING
# ============================================================

st.markdown("""
<style>
.image-hero {
    padding: 28px;
    border-radius: 18px;
    background: linear-gradient(120deg, #581c87, #4338ca, #0e7490);
    border: 1px solid #818cf8;
    margin-bottom: 22px;
}
.image-hero h1 { color: white; }
.image-hero p { color: #ede9fe; }
.image-panel {
    border: 1px solid #334155;
    background: rgba(30, 41, 59, 0.65);
    padding: 18px;
    border-radius: 14px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="image-hero">
    <h1>🎨 AI Image Generator</h1>
    <p>Transform creative ideas into visual concepts using generative AI.</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================

if "image_result" not in st.session_state:
    st.session_state.image_result = None

if "image_prompt_history" not in st.session_state:
    st.session_state.image_prompt_history = []

# ============================================================
# PROMPT BUILDER
# ============================================================

st.subheader("✨ Create your image")

left, right = st.columns([1, 1], gap="large")

with left:
    subject = st.text_input(
        "What do you want to create?",
        placeholder="e.g. A futuristic AI research laboratory",
    )

    style = st.selectbox(
        "Art style",
        [
            "Photorealistic",
            "Digital art",
            "3D render",
            "Anime",
            "Watercolor",
            "Minimalist illustration",
            "Cinematic concept art",
        ],
    )

    mood = st.selectbox(
        "Mood and atmosphere",
        [
            "Professional and clean",
            "Futuristic",
            "Dreamy",
            "Dramatic",
            "Peaceful",
            "Vibrant and energetic",
        ],
    )

with right:
    lighting = st.selectbox(
        "Lighting",
        [
            "Soft natural lighting",
            "Cinematic lighting",
            "Neon lighting",
            "Golden hour",
            "Studio lighting",
        ],
    )

    composition = st.selectbox(
        "Composition",
        [
            "Wide landscape",
            "Square composition",
            "Portrait composition",
        ],
    )

    colors = st.text_input(
        "Preferred colors (optional)",
        placeholder="e.g. Purple, blue and silver",
    )

    extra_details = st.text_area(
        "Additional details",
        placeholder="Describe objects, background, details, etc.",
        height=100,
    )

# ============================================================
# PROMPT GENERATION
# ============================================================

if st.button("✨ Build Image Prompt", type="primary",
             use_container_width=True):

    if not subject.strip():
        st.warning("Enter a subject or idea first.")
    else:
        prompt_parts = [
            f"Create an image of {subject.strip()}.",
            f"Art style: {style}.",
            f"Mood: {mood}.",
            f"Lighting: {lighting}.",
            f"Composition: {composition}.",
        ]

        if colors.strip():
            prompt_parts.append(f"Color palette: {colors.strip()}.")

        if extra_details.strip():
            prompt_parts.append(
                f"Additional details: {extra_details.strip()}."
            )

        prompt_parts.append(
            "Create a coherent, visually polished image with "
            "clear composition and carefully rendered details."
        )

        st.session_state.image_built_prompt = " ".join(prompt_parts)

# ============================================================
# PROMPT PREVIEW
# ============================================================

built_prompt = st.session_state.get("image_built_prompt", "")

if built_prompt:
    st.divider()
    st.subheader("📝 Your enhanced prompt")

    edited_prompt = st.text_area(
        "Review or edit your prompt before generating",
        value=built_prompt,
        height=180,
        key="editable_image_prompt",
    )

    st.download_button(
        "⬇️ Download Prompt",
        data=edited_prompt,
        file_name="image_generation_prompt.txt",
        mime="text/plain",
    )

    st.caption(
        "Building a prompt is free. Generating an image with the API "
        "may incur charges depending on your account and model."
    )

    # ========================================================
    # ACTUAL IMAGE GENERATION
    # ========================================================

    st.subheader("🖼️ Generate image")

    image_api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not image_api_key:
        st.info(
            "Prompt Studio is ready. To generate an actual image, "
            "configure an OpenAI API key in your project's .env file. "
            "Image generation is optional; prompt building works without it."
        )
    else:
        st.warning(
            "Image generation uses an external API and may consume "
            "paid API credits. Click only when you want to generate."
        )

        if st.button(
            "🎨 Generate Actual Image",
            type="primary",
            use_container_width=True,
        ):
            with st.spinner("Generating your image..."):
                try:
                    response = requests.post(
                        "https://api.openai.com/v1/images/generations",
                        headers={
                            "Authorization": f"Bearer {image_api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": "gpt-image-1",
                            "prompt": edited_prompt,
                            "size": "1024x1024",
                        },
                        timeout=180,
                    )

                    if not response.ok:
                        st.error(
                            f"Image API error ({response.status_code}). "
                            "Check your API key, model access and billing."
                        )
                        with st.expander("Technical details"):
                            st.code(response.text[:3000])
                    else:
                        payload = response.json()
                        image_data = payload["data"][0].get("b64_json")

                        if not image_data:
                            st.error(
                                "The API response did not contain "
                                "an encoded image."
                            )
                        else:
                            image_bytes = base64.b64decode(image_data)
                            generated_image = Image.open(
                                io.BytesIO(image_bytes)
                            ).convert("RGB")

                            st.session_state.image_result = image_bytes

                            timestamp = datetime.now().strftime(
                                "%Y%m%d_%H%M%S"
                            )
                            output_path = (
                                OUTPUT_DIR / f"generated_{timestamp}.png"
                            )
                            generated_image.save(output_path)

                            st.success("Image generated successfully!")

                except requests.RequestException as error:
                    st.error(
                        f"Could not contact the image API: {error}"
                    )
                except Exception as error:
                    st.error(f"Image generation failed: {error}")

# ============================================================
# GENERATED IMAGE PREVIEW
# ============================================================

if st.session_state.image_result:
    st.divider()
    st.subheader("🖼️ Generated image")

    st.image(
        st.session_state.image_result,
        caption="Generated using the configured image model",
        use_container_width=True,
    )

    st.download_button(
        "⬇️ Download Generated Image",
        data=st.session_state.image_result,
        file_name="generated_image.png",
        mime="image/png",
        use_container_width=True,
    )

# ============================================================
# INFORMATION PANEL
# ============================================================

st.divider()

with st.expander("ℹ️ About this module"):
    st.write(
        "This module builds structured prompts from user-selected "
        "creative parameters. Actual image synthesis uses the configured "
        "OpenAI image-generation API. Prompt construction is local; "
        "image generation requires API access and may incur charges."
    )

st.caption(
    "GenAI Research Studio · AI Image Generator · Prototype v1.0"
)
