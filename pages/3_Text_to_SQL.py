
import csv
import io
import re
import sqlite3
from pathlib import Path

import requests
import streamlit as st

st.set_page_config(
    page_title="AI Text-to-SQL",
    page_icon="🗄️",
    layout="wide"
)

MODEL_NAME = "llama3.2:3b"
OLLAMA_URL = "http://localhost:11434/api/chat"

DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "research_studio.db"
)

st.title("🗄️ AI Text-to-SQL")
st.caption("Convert natural-language questions into SQL using local AI.")

st.info(
    "Ask questions in plain English. Ollama generates SQL, "
    "and SQLite executes approved read-only queries."
)

# Database schema supplied to the AI
SCHEMA = """
Database: research_studio.db

Table: products
Columns:
- id: product identifier, if present in the database
- name: product name
- category: product category
- price: product price
- stock: available stock quantity

Generate SQLite SELECT queries using the products table.
Use only columns that exist in the actual database.
"""

def get_columns():
    """Inspect the real database schema."""
    with sqlite3.connect(DB_PATH.as_uri() + "?mode=ro", uri=True) as conn:
        columns = conn.execute("PRAGMA table_info(products)").fetchall()
        return [column[1] for column in columns]

def generate_sql(question, columns):
    actual_schema = (
        "Table: products\n"
        "Available columns: " + ", ".join(columns)
    )

    prompt = f"""
Convert the user's question into one SQLite SELECT query.

{actual_schema}

Rules:
- Return SQL only, without Markdown or explanations.
- Use only the products table.
- Use only the listed columns.
- Generate exactly one SELECT statement.
- Do not generate INSERT, UPDATE, DELETE, DROP, ALTER,
  CREATE, PRAGMA, ATTACH, or other statements.
- Do not query SQLite system tables.
- Do not use multiple statements.
- Use SQLite-compatible syntax.

Question: {question}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "system",
                    "content": "You generate safe, read-only SQLite queries."
                },
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "options": {"temperature": 0}
        },
        timeout=300
    )

    response.raise_for_status()
    sql = response.json()["message"]["content"].strip()

    # Remove optional Markdown fences
    sql = re.sub(r"^```(?:sql)?\s*", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s*```$", "", sql).strip()

    return sql

def validate_sql(sql, columns):
    """Apply restrictive checks before executing the query."""
    cleaned = sql.strip()

    if not re.match(r"^SELECT\b", cleaned, re.IGNORECASE):
        raise ValueError("Only SELECT queries are allowed.")

    # Reject multiple statements and SQL comments
    if ";" in cleaned.rstrip(";"):
        raise ValueError("Multiple SQL statements are not allowed.")

    if "--" in cleaned or "/*" in cleaned or "*/" in cleaned:
        raise ValueError("SQL comments are not allowed.")

    # Reject potentially dangerous or indirect operations
    forbidden = re.compile(
        r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|"
        r"TRUNCATE|ATTACH|DETACH|PRAGMA|VACUUM|REINDEX|"
        r"LOAD_EXTENSION|GRANT|REVOKE|INTO|UNION)\b",
        re.IGNORECASE
    )

    if forbidden.search(cleaned):
        raise ValueError("The query contains a disallowed SQL operation.")

    # Permit only the products table
    table_refs = re.findall(
        r"\b(?:FROM|JOIN)\s+([A-Za-z_][A-Za-z0-9_]*)",
        cleaned,
        re.IGNORECASE
    )

    if not table_refs or any(
        table.lower() != "products" for table in table_refs
    ):
        raise ValueError("Queries must use only the products table.")

    # Block subqueries and other SQL structures that complicate validation
    if re.search(r"\b(SELECT)\b", cleaned, re.IGNORECASE).group(0).lower() != "select":
        raise ValueError("Invalid query structure.")

    # Ensure only one statement reaches SQLite
    cleaned = cleaned.rstrip(";").strip()

    return cleaned

def execute_query(sql):
    """Execute SQL against a read-only database connection."""
    with sqlite3.connect(DB_PATH.as_uri() + "?mode=ro", uri=True) as conn:
        conn.execute("PRAGMA query_only = ON")
        conn.set_authorizer(readonly_authorizer)
        cursor = conn.execute(sql)
        headers = [item[0] for item in cursor.description or []]
        rows = cursor.fetchmany(201)

    if len(rows) > 200:
        rows = rows[:200]

    return headers, rows

def readonly_authorizer(action, arg1, arg2, database, trigger):
    """Allow only reads from the products table."""
    allowed_reads = {
        sqlite3.SQLITE_SELECT,
        sqlite3.SQLITE_READ,
        sqlite3.SQLITE_FUNCTION,
    }

    if action not in allowed_reads:
        return sqlite3.SQLITE_DENY

    if action == sqlite3.SQLITE_READ:
        if database != "main" or arg1.lower() != "products":
            return sqlite3.SQLITE_DENY

    return sqlite3.SQLITE_OK

def to_csv(headers, rows):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    return output.getvalue()

if not DB_PATH.exists():
    st.error(f"Database not found: {DB_PATH}")
    st.stop()

try:
    columns = get_columns()
except Exception as error:
    st.error(f"Could not read the products table: {error}")
    st.stop()

with st.sidebar:
    st.header("Database")
    st.write("**File:** research_studio.db")
    st.write("**Table:** products")
    st.write("**Columns:**")
    for column in columns:
        st.write(f"- `{column}`")

    st.divider()
    st.caption("Execution is restricted to read-only queries.")

if "sql_result" not in st.session_state:
    st.session_state.sql_result = None

question = st.text_area(
    "Ask your database",
    placeholder="Example: Show products with stock below 20",
    height=100
)

st.write("**Try an example:**")

examples = [
    "Show all products",
    "Which product has the highest price?",
    "Show products with stock below 20",
    "Count the products in each category"
]

example_cols = st.columns(2)

for index, example in enumerate(examples):
    if example_cols[index % 2].button(
        example, use_container_width=True
    ):
        st.session_state.sql_example = example
        st.rerun()

if "sql_example" in st.session_state:
    question = st.session_state.pop("sql_example")

if st.button("🤖 Generate and Run SQL", type="primary"):
    if not question.strip():
        st.warning("Enter a question first.")
    else:
        try:
            with st.spinner("Generating SQL with local AI..."):
                sql = generate_sql(question.strip(), columns)

            safe_sql = validate_sql(sql, columns)

            with st.spinner("Running read-only query..."):
                headers, rows = execute_query(safe_sql)

            st.session_state.sql_result = {
                "question": question.strip(),
                "sql": safe_sql,
                "headers": headers,
                "rows": rows
            }

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to Ollama. Ensure Ollama is running "
                "and llama3.2:3b is installed."
            )
        except requests.exceptions.Timeout:
            st.error("Ollama timed out. Try a simpler question.")
        except Exception as error:
            st.error(f"Could not complete the query: {error}")

result = st.session_state.sql_result

if result:
    st.divider()
    st.subheader("Generated SQL")

    st.code(result["sql"], language="sql")

    st.subheader("Query Results")
    st.write(f"**Rows returned:** {len(result['rows'])}")

    if not result["rows"]:
        st.info("The query returned no matching rows.")
    else:
        st.write(result["headers"])

        for row_index, row in enumerate(result["rows"], start=1):
            with st.container(border=True):
                st.write(f"**Result {row_index}**")
                for name, value in zip(result["headers"], row):
                    st.write(f"**{name}:** {value}")

        st.download_button(
            "⬇️ Download results as CSV",
            data=to_csv(result["headers"], result["rows"]),
            file_name="sql_query_results.csv",
            mime="text/csv"
        )

st.divider()
st.caption("GenAI Research Studio | Local AI + SQLite")
