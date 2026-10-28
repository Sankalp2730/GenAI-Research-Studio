
import re
from collections import Counter

import requests
import streamlit as st

st.set_page_config(
    page_title="Text Intelligence",
    page_icon="🧠",
    layout="wide"
)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2:3b"

st.title("🧠 Text Intelligence")
st.caption("NLP analysis and text understanding powered by local AI.")

text = st.text_area(
    "Enter text to analyze",
    height=250,
    placeholder="Paste an article, research abstract, report, or other text..."
)

def analyze_text(content):
    words = re.findall(r"\b[\w'-]+\b", content.lower())
    sentences = [
        sentence.strip()
        for sentence in re.split(r"[.!?]+", content)
        if sentence.strip()
    ]

    positive_words = {
        "good", "great", "excellent", "success", "successful",
        "improve", "improved", "benefit", "benefits", "effective",
        "efficient", "positive", "strong", "innovative", "reliable",
        "accurate", "happy", "valuable", "growth", "progress"
    }

    negative_words = {
        "bad", "poor", "failure", "failed", "problem", "problems",
        "risk", "risks", "error", "errors", "weak", "negative",
        "difficult", "ineffective", "unreliable", "inaccurate",
        "harmful", "decline", "issue", "issues"
    }

    positive_count = sum(word in positive_words for word in words)
    negative_count = sum(word in negative_words for word in words)

    if positive_count > negative_count:
        sentiment = "Positive"
    elif negative_count > positive_count:
        sentiment = "Negative"
    else:
        sentiment = "Neutral or mixed"

    stop_words = {
        "the", "and", "for", "that", "with", "this", "from",
        "are", "was", "were", "have", "has", "had", "not",
        "but", "you", "your", "its", "into", "their", "they",
        "will", "can", "could", "would", "should", "about",
        "than", "then", "also", "such", "these", "those",
        "been", "being", "our", "out", "use", "using", "used"
    }

    keywords = [
        (word, count)
        for word, count in Counter(
            word for word in words
            if len(word) > 3 and word not in stop_words
        ).most_common(12)
    ]

    return {
        "words": words,
        "sentences": sentences,
        "positive": positive_count,
        "negative": negative_count,
        "sentiment": sentiment,
        "keywords": keywords
    }

def ask_local_ai(content, task):
    prompt = f"""
Analyze the text according to the requested task.

TASK:
{task}

TEXT:
{content}

Be accurate, clear, and concise. Do not invent information.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a careful NLP analysis assistant."
                },
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "options": {"temperature": 0.2}
        },
        timeout=300
    )

    response.raise_for_status()
    return response.json()["message"]["content"].strip()

if st.button("🔍 Analyze Text", type="primary"):
    if not text.strip():
        st.warning("Please enter some text first.")
    else:
        result = analyze_text(text)
        st.session_state["text_intelligence_result"] = result

if "text_intelligence_result" in st.session_state and text.strip():
    result = st.session_state["text_intelligence_result"]

    st.divider()
    st.subheader("📊 Text Statistics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Words", len(result["words"]))
    col2.metric("Sentences", len(result["sentences"]))
    col3.metric("Characters", len(text))
    col4.metric(
        "Reading time",
        f"{max(1, round(len(result['words']) / 200))} min"
    )

    st.subheader("😊 Basic Sentiment Analysis")
    st.write(f"**Estimated sentiment:** {result['sentiment']}")
    st.write(
        f"Positive keyword matches: {result['positive']} · "
        f"Negative keyword matches: {result['negative']}"
    )
    st.caption(
        "This initial sentiment score uses a small word dictionary. "
        "It is an estimate, not a trained sentiment classifier."
    )

    st.subheader("🔑 Frequent Keywords")
    if result["keywords"]:
        st.write(", ".join(
            f"{word} ({count})"
            for word, count in result["keywords"]
        ))
    else:
        st.write("No keywords found.")

    st.divider()
    st.subheader("✨ Local AI Analysis")

    task = st.selectbox(
        "Choose an AI task",
        [
            "Summarize the text in five bullet points",
            "Extract the main ideas and key findings",
            "Identify the topic, themes, and important entities",
            "Rewrite the text in simple language",
            "Generate five questions and answers based on the text"
        ]
    )

    if st.button("Generate AI Analysis"):
        if len(text) > 15000:
            st.warning(
                "For this prototype, use text shorter than 15,000 "
                "characters for a more reliable response."
            )
        else:
            try:
                with st.spinner("Analyzing with local Ollama AI..."):
                    answer = ask_local_ai(text, task)

                st.markdown("### AI Result")
                st.markdown(answer)

                st.download_button(
                    "Download AI analysis",
                    data=answer,
                    file_name="text_intelligence_analysis.txt",
                    mime="text/plain"
                )

            except requests.exceptions.ConnectionError:
                st.error(
                    "Cannot connect to Ollama. Check that Ollama is running."
                )
            except requests.exceptions.Timeout:
                st.error("Ollama timed out. Try shorter text.")
            except Exception as error:
                st.error(f"Analysis failed: {error}")

st.divider()
st.caption("GenAI Research Studio | Lightweight NLP + Local LLM")
