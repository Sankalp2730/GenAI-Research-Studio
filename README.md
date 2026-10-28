# GenAI Research Studio

An integrated Generative AI platform built with Python, Streamlit, and Ollama. The application brings together document analysis, AI writing, natural-language-to-SQL conversion, text intelligence, document question answering using Retrieval-Augmented Generation (RAG), and model evaluation in one interface.

## Features

- **Document Analyzer:** Extract and analyze text from documents.
- **AI Writing Studio:** Generate drafts for abstracts, reports, proposals, and other content using a locally hosted language model.
- **AI Text-to-SQL:** Convert natural-language questions into SQL queries and retrieve results from an SQLite database.
- **AI Image Generator:** Create detailed image prompts using customizable styles, moods, lighting, composition, and color options.
- **Text Intelligence:** Analyze text statistics, estimate sentiment using a word dictionary, extract frequent keywords, and request AI-powered summaries.
- **RAG Document Q&A:** Upload text-based PDFs, retrieve relevant passages, and ask questions using a local language model.
- **Model Evaluation Lab:** Measure response latency and output size, then manually review relevance, accuracy, and instruction following.
- **System Health Dashboard:** Check local model availability, database access, and required project files.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| User interface | Streamlit |
| Local language model | Ollama |
| Language model | Llama 3.2 3B |
| Database | SQLite |
| PDF processing | pypdf |
| API communication | Requests |
| Text processing | Python standard library |

## Project Structure

```text
GenAI-Research-Studio/
├── app.py
├── pages/
│   ├── 1_Document_Analyzer.py
│   ├── 2_AI_Writing_Studio.py
│   ├── 3_Text_to_SQL.py
│   ├── 4_AI_Image_Generator.py
│   ├── 5_Text_Intelligence.py
│   ├── 6_RAG_Document_QA.py
│   ├── 7_Model_Evaluation.py
│   └── 8_System_Health.py
├── data/
│   └── research_studio.db
├── .venv/
└── README.md
```

## Requirements

- Windows, macOS, or Linux
- Python compatible with the installed Streamlit and project dependencies
- Ollama
- The `llama3.2:3b` model
- Sufficient memory to run the local model

## Installation

### 1. Clone or download the project

Open a terminal in the project directory.

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install streamlit requests pypdf
```

Install any additional dependencies required by your existing modules.

### 4. Install Ollama

Download Ollama from:

https://ollama.com/download/windows

Pull the model:

```powershell
ollama pull llama3.2:3b
```

### 5. Run the application

```powershell
streamlit run app.py
```

Open the local address displayed in your terminal, typically:

http://localhost:8501

## How It Works

1. The user selects a module from the Streamlit sidebar.
2. The application processes the supplied text, document, or question.
3. Modules requiring generative AI send prompts to the local Ollama API.
4. SQLite-backed queries retrieve information from the sample database.
5. The application displays generated responses, extracted information, or query results.

## Current Implementation Notes

- The RAG module uses keyword-based passage retrieval rather than vector embeddings.
- Sentiment analysis uses a lightweight word dictionary and is not a trained classifier.
- Text-to-SQL uses generated SQL with restrictive checks and read-only database execution.
- The image-generation module builds image prompts; local GPU-based image generation is not currently integrated.
- Model evaluation reports response timing and output size and supports manual quality review.

These limitations are documented so users can distinguish implemented features from planned enhancements.

## Privacy and Safety

The project is designed to use a locally hosted language model rather than a paid cloud AI API. Document text sent to Ollama is processed through the local Ollama service. Avoid uploading sensitive documents to an application unless you have reviewed its data handling and logging behavior.

Generated content may contain errors and should be reviewed before professional or academic use.

## Future Enhancements

- Semantic document retrieval using embeddings and a vector database
- More robust SQL validation and query auditing
- Improved sentiment analysis and named-entity recognition
- Automated evaluation metrics and benchmark datasets
- Local image-generation model integration
- Unit tests, error logging, and deployment support

## Author

Developed as an academic Generative AI project exploring local language models, NLP, RAG, database interaction, and model evaluation.
