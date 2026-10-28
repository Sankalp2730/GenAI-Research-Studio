
import sqlite3
from pathlib import Path

import requests
import streamlit as st

st.set_page_config(
    page_title="System Health",
    page_icon="🩺",
    layout="wide"
)

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "pages"
DB_PATH = ROOT / "data" / "research_studio.db"
OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "llama3.2:3b"

st.title("🩺 System Health Dashboard")
st.caption("Check the status of GenAI Research Studio components.")

if st.button("🔄 Run Health Checks", type="primary"):
    st.session_state["run_health_checks"] = True

if "run_health_checks" not in st.session_state:
    st.session_state["run_health_checks"] = True

if st.session_state["run_health_checks"]:

    checks = []

    # 1. Ollama service
    try:
        response = requests.get(
            f"{OLLAMA_URL}/api/tags",
            timeout=5
        )
        response.raise_for_status()

        models = response.json().get("models", [])
        installed = [
            model.get("name", "")
            for model in models
        ]

        model_found = any(
            name == MODEL_NAME or name.startswith(MODEL_NAME + ":")
            for name in installed
        )

        checks.append({
            "component": "Ollama Service",
            "status": "PASS",
            "details": "Ollama API is responding."
        })

        checks.append({
            "component": "Local AI Model",
            "status": "PASS" if model_found else "WARNING",
            "details": (
                f"{MODEL_NAME} is installed."
                if model_found
                else f"{MODEL_NAME} was not found. Installed models: "
                     + (", ".join(installed) or "None")
            )
        })

    except Exception as error:
        checks.append({
            "component": "Ollama Service",
            "status": "FAIL",
            "details": str(error)
        })

        checks.append({
            "component": "Local AI Model",
            "status": "UNKNOWN",
            "details": "Cannot check models while Ollama is unavailable."
        })

    # 2. SQLite database
    if DB_PATH.exists():
        try:
            with sqlite3.connect(
                DB_PATH.as_uri() + "?mode=ro",
                uri=True
            ) as connection:
                tables = connection.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='table' AND name='products'"
                ).fetchone()

                if tables:
                    count = connection.execute(
                        "SELECT COUNT(*) FROM products"
                    ).fetchone()[0]

                    checks.append({
                        "component": "SQLite Database",
                        "status": "PASS",
                        "details": f"Database accessible; {count} products found."
                    })
                else:
                    checks.append({
                        "component": "SQLite Database",
                        "status": "WARNING",
                        "details": "Database exists, but products table is missing."
                    })

        except Exception as error:
            checks.append({
                "component": "SQLite Database",
                "status": "FAIL",
                "details": str(error)
            })
    else:
        checks.append({
            "component": "SQLite Database",
            "status": "FAIL",
            "details": f"Database not found: {DB_PATH}"
        })

    # 3. Project pages
    required_pages = [
        "1_Document_Analyzer.py",
        "2_AI_Writing_Studio.py",
        "3_Text_to_SQL.py",
        "4_AI_Image_Generator.py",
        "5_Text_Intelligence.py",
        "6_RAG_Document_QA.py",
        "7_Model_Evaluation.py",
    ]

    for page in required_pages:
        exists = (PAGES / page).is_file()
        checks.append({
            "component": page,
            "status": "PASS" if exists else "FAIL",
            "details": "File found." if exists else "File missing."
        })

    # 4. Data directory
    data_dir = ROOT / "data"

    checks.append({
        "component": "Data Directory",
        "status": "PASS" if data_dir.is_dir() else "FAIL",
        "details": str(data_dir)
    })

    # Summary
    passed = sum(item["status"] == "PASS" for item in checks)
    failed = sum(item["status"] == "FAIL" for item in checks)
    warnings = sum(
        item["status"] in ("WARNING", "UNKNOWN")
        for item in checks
    )

    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Passed", passed)
    col2.metric("Failed", failed)
    col3.metric("Warnings / Unknown", warnings)

    st.subheader("Component Details")

    for item in checks:
        with st.container(border=True):
            st.write(f"**{item['component']}**")

            if item["status"] == "PASS":
                st.success(item["status"])
            elif item["status"] == "FAIL":
                st.error(item["status"])
            else:
                st.warning(item["status"])

            st.caption(item["details"])

    if failed == 0 and warnings == 0:
        st.success("All configured checks passed.")
    elif failed > 0:
        st.warning("Some checks failed. Review the details above.")

st.divider()
st.caption("GenAI Research Studio | System Diagnostics")
