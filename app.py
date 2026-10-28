
import streamlit as st
from pathlib import Path

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="GenAI Research Studio",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM STYLING ----------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0b1020 0%, #111a30 55%, #101326 100%);
        color: #f1f5f9;
    }

    [data-testid="stSidebar"] {
        background-color: #0b1120;
        border-right: 1px solid #27344d;
    }

    .hero {
        padding: 30px;
        border-radius: 20px;
        background: linear-gradient(120deg, #172554, #312e81, #4c1d95);
        border: 1px solid #4f46e5;
        margin-bottom: 24px;
    }

    .hero h1 {
        color: white;
        font-size: 38px;
        margin-bottom: 8px;
    }

    .hero p {
        color: #dbeafe;
        font-size: 16px;
    }

    .section-title {
        font-size: 23px;
        font-weight: 700;
        margin: 22px 0 12px 0;
        color: #f8fafc;
    }

    .feature-card {
        background: rgba(30, 41, 59, 0.85);
        border: 1px solid #334155;
        border-radius: 15px;
        padding: 20px;
        min-height: 190px;
        margin-bottom: 12px;
    }

    .feature-icon {
        font-size: 30px;
        margin-bottom: 10px;
    }

    .feature-card h3 {
        color: #c4b5fd;
        font-size: 19px;
        margin-bottom: 8px;
    }

    .feature-card p {
        color: #cbd5e1;
        font-size: 14px;
    }

    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.75);
        padding: 18px;
        border: 1px solid #334155;
        border-radius: 12px;
    }

    .footer {
        text-align: center;
        color: #94a3b8;
        padding: 25px 0;
        font-size: 13px;
    }

    .stButton > button {
        border-radius: 9px;
        border: 1px solid #6366f1;
        background: #312e81;
        color: white;
    }

    .stButton > button:hover {
        background: #4338ca;
        border-color: #818cf8;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 🧠 GenAI Studio")
    st.caption("Your intelligent AI workspace")
    st.divider()

    st.markdown("### NAVIGATION")
    st.page_link("app.py", label="🏠 Dashboard", icon="🏠")
    st.page_link(
        "pages/1_Document_Analyzer.py",
        label="📄 Document Analyzer"
    )
    st.page_link(
        "pages/2_AI_Writing_Studio.py",
        label="✍️ AI Writing Studio"
    )
    st.page_link(
        "pages/3_Text_to_SQL.py",
        label="🗄️ Text-to-SQL"
    )
    st.page_link(
        "pages/4_AI_Image_Generator.py",
        label="🎨 AI Image Generator"
    )
    st.page_link(
        "pages/5_Text_Intelligence.py",
        label="📊 Text Intelligence"
    )

    st.divider()
    st.markdown("### PROJECT STATUS")
    st.success("Dashboard initialized")
    st.info("AI modules are being developed.")

    st.markdown("---")
    st.caption("GenAI Research Studio | M.Tech CSE")

# ---------------- HERO SECTION ----------------
st.markdown("""
<div class="hero">
    <h1>🧠 GenAI Research Studio</h1>
    <p>
        One intelligent workspace for document understanding,
        content generation, data analysis and creative AI.
    </p>
    <p>Explore. Generate. Analyze. Innovate.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- METRICS ----------------
st.markdown('<div class="section-title">Workspace Overview</div>',
            unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("AI Modules", "05", help="Five planned application modules")

with col2:
    st.metric("Core Technology", "GenAI")

with col3:
    st.metric("Data Workspace", "Ready")

with col4:
    st.metric("Project Version", "0.1.0")

# ---------------- FEATURE CARDS ----------------
st.markdown('<div class="section-title">Explore AI Capabilities</div>',
            unsafe_allow_html=True)

features = [
    (
        "📄",
        "Document Analyzer",
        "Upload documents, generate summaries and explore document content.",
        "pages/1_Document_Analyzer.py",
        "Open Document Analyzer"
    ),
    (
        "✍️",
        "AI Writing Studio",
        "Create reports, introductions, conclusions and other written content.",
        "pages/2_AI_Writing_Studio.py",
        "Open Writing Studio"
    ),
    (
        "🗄️",
        "Text-to-SQL Assistant",
        "Translate natural-language questions into database queries.",
        "pages/3_Text_to_SQL.py",
        "Open Text-to-SQL"
    ),
    (
        "🎨",
        "AI Image Generator",
        "Turn text prompts into visual creations using a generative model.",
        "pages/4_AI_Image_Generator.py",
        "Open Image Generator"
    ),
    (
        "📊",
        "Text Intelligence",
        "Explore text preprocessing, classification and sentiment analysis.",
        "pages/5_Text_Intelligence.py",
        "Open Text Intelligence"
    ),
    (
        "🔬",
        "AI Evaluation Lab",
        "A future module for testing outputs and comparing model performance.",
        None,
        None
    )
]

for start in range(0, len(features), 3):
    columns = st.columns(3)

    for column, feature in zip(columns, features[start:start + 3]):
        icon, title, description, page, button_text = feature

        with column:
            st.markdown(
                f"""
                <div class="feature-card">
                    <div class="feature-icon">{icon}</div>
                    <h3>{title}</h3>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            if page:
                st.page_link(page, label=button_text, icon="➡️")
            else:
                st.caption("Planned for a later development phase")

# ---------------- QUICK START ----------------
st.markdown(
    '<div class="section-title">Quick Start</div>',
    unsafe_allow_html=True
)

st.info(
    "Choose a module from the sidebar or the feature cards. "
    "The dashboard is ready; the individual AI modules will be "
    "implemented and connected in the next steps."
)

# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
    GenAI Research Studio · Intelligent Systems Workspace<br>
    Built with Python and Streamlit
</div>
""", unsafe_allow_html=True)
