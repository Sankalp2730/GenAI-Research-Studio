
import time
import requests
import streamlit as st

st.set_page_config(
    page_title="Model Evaluation Lab",
    page_icon="🧪",
    layout="wide"
)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2:3b"

st.title("🧪 Model Evaluation Lab")
st.caption("Benchmark and evaluate your local generative AI model.")

st.info(
    "This evaluation lab measures response latency and output size, "
    "and provides a checklist for reviewing answer quality."
)

tasks = {
    "Summarization": (
        "Summarize the following text in three bullet points: "
        "Generative AI can assist education by explaining difficult "
        "concepts, creating practice questions, and providing feedback. "
        "However, generated answers can contain errors, so learners "
        "should verify important information."
    ),
    "Question Answering": (
        "Context: SQLite is a lightweight relational database that stores "
        "data in a file. Question: What is SQLite, and where does it store data?"
    ),
    "Text Generation": (
        "Write a short paragraph explaining how generative AI can help "
        "software developers. Mention one benefit and one limitation."
    ),
    "Reasoning": (
        "A database has 120 products. There are 35 electronics products "
        "and 25 furniture products. The rest are stationery. How many "
        "stationery products are there? Explain the calculation."
    )
}

def run_model(prompt):
    start = time.perf_counter()

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant. Answer clearly and "
                        "follow the user's instructions."
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
    data = response.json()
    elapsed = time.perf_counter() - start

    answer = data["message"]["content"].strip()
    word_count = len(answer.split())

    return {
        "answer": answer,
        "latency": round(elapsed, 2),
        "word_count": word_count,
        "characters": len(answer),
        "model": data.get("model", MODEL_NAME)
    }

if "evaluation_runs" not in st.session_state:
    st.session_state.evaluation_runs = []

st.subheader("1. Run a benchmark")

selected_task = st.selectbox(
    "Choose a test",
    list(tasks.keys())
)

custom_prompt = st.text_area(
    "Prompt",
    value=tasks[selected_task],
    height=140
)

if st.button("▶ Run Evaluation", type="primary"):
    if not custom_prompt.strip():
        st.warning("Enter a prompt first.")
    else:
        try:
            with st.spinner("Running local model..."):
                result = run_model(custom_prompt.strip())

            result["task"] = selected_task
            result["prompt"] = custom_prompt.strip()
            result["review"] = {
                "relevant": False,
                "accurate": False,
                "instructions": False
            }

            st.session_state.evaluation_runs.append(result)

        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to Ollama. Check that it is running.")
        except requests.exceptions.Timeout:
            st.error("The model timed out. Try again with a shorter prompt.")
        except Exception as error:
            st.error(f"Evaluation failed: {error}")

if st.session_state.evaluation_runs:
    st.divider()
    st.subheader("2. Latest result")

    latest = st.session_state.evaluation_runs[-1]

    col1, col2, col3 = st.columns(3)
    col1.metric("Response time", f"{latest['latency']} sec")
    col2.metric("Output words", latest["word_count"])
    col3.metric("Output characters", latest["characters"])

    st.caption(f"Model: {latest['model']}")
    st.markdown("### Generated response")
    st.write(latest["answer"])

    st.divider()
    st.subheader("3. Human quality review")
    st.caption(
        "Review the answer yourself. These checks are not automatically "
        "scored and do not establish factual correctness."
    )

    review = latest["review"]

    review["relevant"] = st.checkbox(
        "The answer addresses the prompt",
        value=review["relevant"],
        key=f"relevant_{len(st.session_state.evaluation_runs)}"
    )

    review["accurate"] = st.checkbox(
        "The answer appears factually correct",
        value=review["accurate"],
        key=f"accurate_{len(st.session_state.evaluation_runs)}"
    )

    review["instructions"] = st.checkbox(
        "The answer follows the requested format",
        value=review["instructions"],
        key=f"instructions_{len(st.session_state.evaluation_runs)}"
    )

    st.subheader("4. Benchmark history")

    for index, run in enumerate(
        reversed(st.session_state.evaluation_runs), start=1
    ):
        with st.expander(f"{run['task']} — {run['latency']} sec"):
            st.write(f"**Prompt:** {run['prompt']}")
            st.write(f"**Words:** {run['word_count']}")
            st.write(f"**Response:** {run['answer']}")

    if st.button("Clear evaluation history"):
        st.session_state.evaluation_runs = []
        st.rerun()

st.divider()
st.caption("GenAI Research Studio | Model Evaluation")
