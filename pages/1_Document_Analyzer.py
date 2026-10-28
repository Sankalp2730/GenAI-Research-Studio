
import re
from collections import Counter

import streamlit as st
from pypdf import PdfReader

st.set_page_config(
    page_title="Document Analyzer | GenAI Research Studio",
    page_icon="📄",
    layout="wide",
)


# ---------- TEXT PROCESSING HELPERS ----------

STOP_WORDS = set("""
a an the and or but if while is am are was were be been being
to of in on at for from by with about as into through during
it its this that these those i you he she we they them their
what which who whom where when why how can could would should
do does did have has had not no so than too very also
""".split())


def tokenize(text):
    return re.findall(r"\b[a-zA-Z0-9'-]+\b", text.lower())


def get_sentences(text):
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", text)
        if len(sentence.strip().split()) >= 4
    ]


def summarize(text, percentage=25):
    sentences = get_sentences(text)

    if not sentences:
        return "Not enough readable text to generate a summary."

    words = [
        word for word in tokenize(text)
        if word not in STOP_WORDS and len(word) > 2
    ]
    frequencies = Counter(words)

    if not frequencies:
        return "No meaningful keywords were found in the document."

    max_frequency = max(frequencies.values())
    normalized = {
        word: count / max_frequency
        for word, count in frequencies.items()
    }

    scores = []
    for sentence in sentences:
        sentence_words = [
            word for word in tokenize(sentence)
            if word not in STOP_WORDS and len(word) > 2
        ]
        score = sum(normalized.get(word, 0) for word in sentence_words)
        scores.append(score / max(len(sentence_words), 1))

    count = max(1, round(len(sentences) * percentage / 100))
    ranked_indices = sorted(
        range(len(sentences)),
        key=lambda i: scores[i],
        reverse=True,
    )[:count]

    return " ".join(sentences[i] for i in sorted(ranked_indices))


def extract_keywords(text, limit=15):
    words = [
        word for word in tokenize(text)
        if word not in STOP_WORDS and len(word) > 2
        and not word.isdigit()
    ]

    frequencies = Counter(words)
    return frequencies.most_common(limit)


def find_relevant_sentences(question, text, limit=3):
    question_words = {
        word for word in tokenize(question)
        if word not in STOP_WORDS and len(word) > 2
    }

    if not question_words:
        return []

    candidates = get_sentences(text)
    scored = []

    for index, sentence in enumerate(candidates):
        sentence_words = {
            word for word in tokenize(sentence)
            if word not in STOP_WORDS and len(word) > 2
        }

        overlap = question_words.intersection(sentence_words)

        if overlap:
            score = len(overlap) / len(question_words)
            scored.append((score, index, sentence))

    scored.sort(key=lambda item: (-item[0], item[1]))
    return [(score, sentence) for score, _, sentence in scored[:limit]]


# ---------- HEADER ----------

st.title("📄 Document Analyzer")
st.caption(
    "Extract information, summarize documents, discover keywords "
    "and retrieve relevant passages."
)

st.info(
    "Lightweight NLP mode: this version uses Python's built-in text "
    "processing and does not require SciPy or scikit-learn."
)


# ---------- DOCUMENT UPLOAD ----------

uploaded_file = st.file_uploader(
    "Upload a text-based PDF document",
    type=["pdf"],
)

if uploaded_file is not None:
    try:
        reader = PdfReader(uploaded_file)
        document_text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )
        page_count = len(reader.pages)

        if not document_text.strip():
            st.warning(
                "No selectable text was found. This may be a scanned PDF. "
                "OCR support can be added later."
            )
            st.stop()

    except Exception as error:
        st.error(f"Could not read this PDF: {error}")
        st.stop()

    st.success(f"Loaded document: {uploaded_file.name}")

    words = tokenize(document_text)
    sentences = get_sentences(document_text)

    # ---------- METRICS ----------

    col1, col2, col3 = st.columns(3)
    col1.metric("Total words", f"{len(words):,}")
    col2.metric("Characters", f"{len(document_text):,}")
    col3.metric("Pages", page_count)

    st.divider()

    # ---------- FEATURE TABS ----------

    tab1, tab2, tab3, tab4 = st.tabs([
        "📖 Document",
        "📝 Summary",
        "🔑 Keywords",
        "💬 Ask Document",
    ])

    with tab1:
        st.subheader("Extracted document text")

        st.text_area(
            "Document contents",
            value=document_text,
            height=350,
            label_visibility="collapsed",
        )

        st.download_button(
            "⬇️ Download extracted text",
            data=document_text,
            file_name="extracted_document.txt",
            mime="text/plain",
        )

    with tab2:
        st.subheader("Automatic document summary")

        percentage = st.slider(
            "Summary length",
            min_value=10,
            max_value=50,
            value=25,
            step=5,
            format="%d%%",
        )

        if st.button("Generate Summary", type="primary"):
            st.session_state["doc_summary"] = summarize(
                document_text,
                percentage,
            )

        if st.session_state.get("doc_summary"):
            st.write(st.session_state["doc_summary"])

            st.download_button(
                "⬇️ Download summary",
                data=st.session_state["doc_summary"],
                file_name="document_summary.txt",
                mime="text/plain",
            )

        st.caption(
            "Summary sentences are selected using word frequencies. "
            "This is extractive NLP, not an LLM-generated summary."
        )

    with tab3:
        st.subheader("Important keywords")

        if st.button("Extract Keywords"):
            st.session_state["doc_keywords"] = extract_keywords(
                document_text
            )

        keywords = st.session_state.get("doc_keywords", [])

        if keywords:
            keyword_columns = st.columns(3)

            for index, (word, frequency) in enumerate(keywords):
                with keyword_columns[index % 3]:
                    st.metric(word.title(), frequency)

    with tab4:
        st.subheader("Ask questions about your document")

        st.caption(
            "Find passages that share important words with your question."
        )

        question = st.text_input(
            "Your question",
            placeholder="What is the main objective of this paper?",
        )

        if st.button("Find Answer", type="primary"):
            if not question.strip():
                st.warning("Please enter a question.")
            else:
                results = find_relevant_sentences(
                    question,
                    document_text,
                )

                if results:
                    st.markdown("### Relevant passages")

                    for index, (score, sentence) in enumerate(
                        results,
                        start=1,
                    ):
                        st.markdown(f"**Passage {index}**")
                        st.write(sentence)
                        st.caption(
                            f"Keyword overlap score: {score:.0%}"
                        )
                else:
                    st.warning(
                        "No matching passages were found. Try using "
                        "keywords that appear in the document."
                    )

else:
    st.markdown("### Explore your documents")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("📖 Extract")
        st.write("Read PDF contents and calculate document statistics.")

    with col2:
        st.subheader("📝 Summarize")
        st.write("Identify important sentences from long documents.")

    with col3:
        st.subheader("💬 Retrieve")
        st.write("Find passages related to a question.")
