
import io
import re
import requests
import streamlit as st
from pypdf import PdfReader

st.set_page_config(
    page_title="RAG Document Q&A",
    page_icon="📚",
    layout="wide"
)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2:3b"

st.title("📚 RAG Document Q&A")
st.caption("Ask questions about your documents using local AI.")

st.info(
    "Your PDF is processed in this application. "
    "Its extracted text is sent to your local Ollama model for answers."
)

# Session state
if "rag_chunks" not in st.session_state:
    st.session_state.rag_chunks = []

if "rag_filename" not in st.session_state:
    st.session_state.rag_filename = ""

if "rag_history" not in st.session_state:
    st.session_state.rag_history = []

def clean_text(text):
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def split_into_chunks(text, chunk_size=1800, overlap=250):
    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - overlap

    return chunks

def retrieve_relevant_chunks(question, chunks, limit=4):
    """Lightweight keyword-based retrieval without ML libraries."""
    stop_words = {
        "the", "is", "are", "was", "were", "what", "when", "where",
        "who", "why", "how", "does", "do", "did", "can", "could",
        "would", "should", "and", "or", "to", "of", "in", "on",
        "for", "a", "an", "it", "this", "that", "with", "from",
        "explain", "describe", "tell", "me", "about"
    }

    terms = {
        word.lower()
        for word in re.findall(r"\b[a-zA-Z0-9]+\b", question)
        if len(word) > 2 and word.lower() not in stop_words
    }

    scored = []

    for index, chunk in enumerate(chunks):
        words = re.findall(r"\b[a-zA-Z0-9]+\b", chunk.lower())
        word_set = set(words)
        score = sum(1 for term in terms if term in word_set)

        if score > 0:
            scored.append((score, index, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [item[2] for item in scored[:limit]]

def ask_ollama(question, context):
    prompt = f"""
Answer the user's question using only the supplied document context.

Instructions:
- Do not invent facts that are absent from the context.
- If the context does not contain the answer, say so clearly.
- Explain the answer in simple, well-structured language.
- You may summarize or compare information found in the context.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a document question-answering assistant. "
                        "Ground your answers in the provided document."
                    )
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

# Sidebar
with st.sidebar:
    st.header("📖 Document Library")
    st.write("Upload a PDF to begin.")

    uploaded_file = st.file_uploader(
        "Choose a PDF document",
        type=["pdf"]
    )

    if uploaded_file is not None:
        if st.button("Process PDF", type="primary", use_container_width=True):
            try:
                reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))

                page_texts = []
                progress = st.progress(0)

                for i, page in enumerate(reader.pages):
                    page_texts.append(page.extract_text() or "")
                    progress.progress((i + 1) / max(len(reader.pages), 1))

                full_text = clean_text("\n".join(page_texts))

                if not full_text:
                    st.error(
                        "No selectable text found. This may be a scanned PDF. "
                        "OCR support is not included yet."
                    )
                else:
                    st.session_state.rag_chunks = split_into_chunks(full_text)
                    st.session_state.rag_filename = uploaded_file.name
                    st.session_state.rag_history = []

                    st.success("PDF processed successfully!")

            except Exception as error:
                st.error(f"Could not process PDF: {error}")

    if st.session_state.rag_chunks:
        st.divider()
        st.write("**Current document**")
        st.write(st.session_state.rag_filename)
        st.metric("Text chunks", len(st.session_state.rag_chunks))

        if st.button("Clear document", use_container_width=True):
            st.session_state.rag_chunks = []
            st.session_state.rag_filename = ""
            st.session_state.rag_history = []
            st.rerun()

# Main content
if not st.session_state.rag_chunks:
    st.subheader("Get started")
    st.write("1. Upload a text-based PDF from the sidebar.")
    st.write("2. Click **Process PDF**.")
    st.write("3. Ask a question about the document.")
    st.caption(
        "This initial version uses keyword-based retrieval and local AI "
        "generation; it does not use vector embeddings yet."
    )
else:
    st.success(f"Loaded: {st.session_state.rag_filename}")

    question = st.text_area(
        "Ask a question about your document",
        placeholder="Example: What are the main findings of this paper?",
        height=100
    )

    if st.button("🔍 Ask Local AI", type="primary"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            relevant_chunks = retrieve_relevant_chunks(
                question,
                st.session_state.rag_chunks
            )

            if not relevant_chunks:
                st.warning(
                    "No matching passages were found. Try using keywords "
                    "from the document."
                )
            else:
                context = "\n\n---\n\n".join(relevant_chunks)

                with st.spinner("Reading document and generating an answer..."):
                    try:
                        answer = ask_ollama(question.strip(), context)

                        st.session_state.rag_history.append({
                            "question": question.strip(),
                            "answer": answer,
                            "sources": relevant_chunks
                        })

                    except requests.exceptions.ConnectionError:
                        st.error(
                            "Cannot connect to Ollama. Make sure Ollama is "
                            "running and the model is installed."
                        )
                    except requests.exceptions.Timeout:
                        st.error("Ollama took too long to respond. Try again.")
                    except Exception as error:
                        st.error(f"Error generating answer: {error}")

    if st.session_state.rag_history:
        st.divider()
        st.subheader("💡 Answers")

        for item in reversed(st.session_state.rag_history):
            with st.container(border=True):
                st.markdown(f"**Question:** {item['question']}")
                st.markdown(item["answer"])

                with st.expander("View retrieved document passages"):
                    for i, source in enumerate(item["sources"], start=1):
                        st.markdown(f"**Passage {i}**")
                        st.write(source)

        if st.button("Clear question history"):
            st.session_state.rag_history = []
            st.rerun()

st.divider()
st.caption("GenAI Research Studio | Local RAG prototype")
