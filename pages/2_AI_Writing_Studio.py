
import requests
import streamlit as st
from datetime import datetime

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Writing Studio | GenAI Research Studio",
    page_icon="✍️",
    layout="wide",
)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2:3b"

# ============================================================
# STYLING
# ============================================================

st.markdown("""
<style>
.writing-hero {
    padding: 28px;
    border-radius: 17px;
    background: linear-gradient(120deg, #312e81, #6d28d9, #9333ea);
    border: 1px solid #8b5cf6;
    margin-bottom: 24px;
}
.writing-hero h1 { color: white; }
.writing-hero p { color: #ede9fe; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="writing-hero">
    <h1>✍️ AI Writing Studio</h1>
    <p>
        Generate original content using a locally running language model.
        Create reports, research abstracts, introductions and more.
    </p>
</div>
""", unsafe_allow_html=True)

st.caption(
    f"Model: {MODEL_NAME} · Local inference through Ollama · "
    "No paid API key required"
)

# ============================================================
# SESSION STATE
# ============================================================

if "writing_draft" not in st.session_state:
    st.session_state.writing_draft = ""

if "writing_history" not in st.session_state:
    st.session_state.writing_history = []

if "writing_notice" not in st.session_state:
    st.session_state.writing_notice = ""

# ============================================================
# WRITING OPTIONS
# ============================================================

st.subheader("Create your content")

left, right = st.columns(2, gap="large")

with left:
    content_type = st.selectbox(
        "Content type",
        [
            "Research Abstract",
            "Research Introduction",
            "Technical Report",
            "Project Documentation",
            "Blog Article",
            "Professional Email",
            "Essay",
            "Executive Summary",
            "Project Proposal",
            "Conclusion",
        ],
    )

    topic = st.text_input(
        "Topic or subject",
        placeholder="e.g. Generative AI in healthcare",
    )

    audience = st.selectbox(
        "Target audience",
        [
            "General audience",
            "Students",
            "Academic researchers",
            "Software developers",
            "Business professionals",
            "Technical experts",
        ],
    )

    tone = st.selectbox(
        "Writing tone",
        [
            "Professional",
            "Academic",
            "Creative",
            "Simple and easy to understand",
            "Formal",
            "Persuasive",
        ],
    )

    length = st.select_slider(
        "Draft length",
        options=["Short", "Medium", "Long"],
        value="Medium",
    )

with right:
    key_points = st.text_area(
        "Instructions and key points",
        placeholder=(
            "Enter one point per line\n"
            "Example:\n"
            "Introduction to the topic\n"
            "Benefits and applications\n"
            "Challenges and future scope"
        ),
        height=210,
    )

    additional_instructions = st.text_area(
        "Additional instructions (optional)",
        placeholder=(
            "e.g. Use headings, provide examples, "
            "include limitations..."
        ),
        height=100,
    )

# ============================================================
# GENERATION
# ============================================================

generate_col, clear_col = st.columns([3, 1])

generate_clicked = generate_col.button(
    "✨ Generate with Local AI",
    type="primary",
    use_container_width=True,
)

clear_clicked = clear_col.button(
    "🗑️ Clear Draft",
    use_container_width=True,
)

if clear_clicked:
    st.session_state.writing_draft = ""
    st.session_state.writing_notice = ""
    st.rerun()

if generate_clicked:
    if not topic.strip():
        st.warning("Please enter a topic before generating.")
    else:
        word_targets = {
            "Short": "approximately 150–250 words",
            "Medium": "approximately 400–600 words",
            "Long": "approximately 800–1200 words",
        }

        points_text = (
            key_points.strip()
            if key_points.strip()
            else "Choose relevant subtopics for the subject."
        )

        prompt = f"""
You are a skilled writer assisting users in a Generative AI
Research Studio.

Create an original {content_type.lower()}.

TOPIC:
{topic.strip()}

TARGET AUDIENCE:
{audience}

WRITING TONE:
{tone}

LENGTH:
{word_targets[length]}

KEY POINTS AND REQUIREMENTS:
{points_text}

ADDITIONAL INSTRUCTIONS:
{additional_instructions.strip() or "No additional instructions."}

REQUIREMENTS:
1. Write the requested content directly.
2. Use clear, logical organization and useful headings where appropriate.
3. Avoid repetitive filler and unsupported factual claims.
4. Do not invent references, statistics, or research findings.
5. If discussing academic research, clearly distinguish established
   information from suggestions or hypothetical examples.
6. Return only the finished draft, without describing these instructions.
"""

        try:
            with st.spinner(
                "Local AI is writing your draft. "
                "The first response may take a little longer..."
            ):
                response = requests.post(
                    OLLAMA_URL,
                    json={
                        "model": MODEL_NAME,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "You are a helpful, accurate, "
                                    "professional writing assistant."
                                ),
                            },
                            {
                                "role": "user",
                                "content": prompt,
                            },
                        ],
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                        },
                    },
                    timeout=300,
                )

                response.raise_for_status()
                payload = response.json()

                draft = (
                    payload.get("message", {}).get("content", "")
                ).strip()

                if not draft:
                    st.error(
                        "The model returned an empty response. "
                        "Please try again."
                    )
                else:
                    st.session_state.writing_draft = draft
                    st.session_state.writing_notice = (
                        f"Generated locally using {MODEL_NAME}"
                    )

                    st.session_state.writing_history.insert(
                        0,
                        {
                            "topic": topic.strip(),
                            "type": content_type,
                            "time": datetime.now().strftime(
                                "%d %b %Y, %I:%M %p"
                            ),
                            "draft": draft,
                        },
                    )

                    st.session_state.writing_history = (
                        st.session_state.writing_history[:5]
                    )

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to Ollama. Make sure Ollama is "
                "running on your computer and try again."
            )

        except requests.exceptions.Timeout:
            st.error(
                "The model took too long to respond. Try a shorter "
                "draft or check your computer's available resources."
            )

        except requests.exceptions.HTTPError as error:
            st.error(f"Ollama returned an HTTP error: {error}")

        except Exception as error:
            st.error(f"Draft generation failed: {error}")

# ============================================================
# GENERATED DRAFT
# ============================================================

st.divider()
st.subheader("📄 Your Draft")

if st.session_state.writing_draft:
    st.success(
        st.session_state.writing_notice
        or "Draft available"
    )

    edited_draft = st.text_area(
        "Review and edit your draft",
        value=st.session_state.writing_draft,
        height=420,
        key="writing_editor",
    )

    download_col, save_col = st.columns(2)

    download_col.download_button(
        "⬇️ Download as Markdown",
        data=edited_draft,
        file_name="ai_generated_draft.md",
        mime="text/markdown",
        use_container_width=True,
    )

    if save_col.button(
        "💾 Save Edited Draft",
        use_container_width=True,
    ):
        st.session_state.writing_draft = edited_draft
        st.session_state.writing_notice = "Edited draft saved in this session."
        st.success("Your edited draft has been saved for this session.")

    word_count = len(edited_draft.split())

    metric_col1, metric_col2 = st.columns(2)
    metric_col1.metric("Word Count", word_count)
    metric_col2.metric(
        "Characters",
        len(edited_draft),
    )

else:
    st.info(
        "Enter a topic and click Generate with Local AI "
        "to create your first draft."
    )

# ============================================================
# RECENT WRITING SESSIONS
# ============================================================

with st.expander("🕘 Recent writing sessions"):
    history = st.session_state.writing_history

    if history:
        for index, item in enumerate(history):
            st.markdown(
                f"**{item['topic']}** — {item['type']}"
            )
            st.caption(item["time"])

            if st.button(
                "Load this draft",
                key=f"load_draft_{index}",
            ):
                st.session_state.writing_draft = item["draft"]
                st.session_state.writing_notice = (
                    f"Loaded draft: {item['topic']}"
                )
                st.rerun()

            st.divider()
    else:
        st.caption(
            "Generated drafts will appear here during this session."
        )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "GenAI Research Studio · AI Writing Studio · "
    "Powered by Ollama and a local language model"
)

st.caption(
    "Review generated content for factual accuracy before using it "
    "in academic or professional work."
)
