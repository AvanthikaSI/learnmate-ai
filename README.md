# 🎓 LearnMate AI

> **A general-purpose AI learning assistant for any topic built with Python, Streamlit, Google Gemini API, and SQLite.**

LearnMate AI transforms complex subjects into intuitive, bite-sized lessons. Designed for students and engineers, it provides concept breakdowns, real-world industry case studies, automated conceptual quizzes, intelligent answer evaluation, multi-turn follow-up conversations, and one-click study note exports (Markdown, TXT, and PDF).

---

## 🌟 Key Features

- **Multi-Activity Learning Engine**:
  - 📌 **Explain Concept**: High-level intuition (TL;DR), core mechanics, real-world analogies, and key takeaways.
  - 🌍 **Real-Life Example**: How tech leaders (Netflix, Google, Uber) and modern distributed systems apply the concept in practice.
  - 📝 **Generate Quiz**: 4 conceptual multiple-choice questions with a separate, spoiler-free answer key & explanations.
  - ❓ **Ask Anything**: Targeted answers to your specific queries, edge cases, and doubts.
  - 🎯 **Evaluate Answer**: Submit your reasoning or code, get constructive grading (Correct / Partially Correct / Needs Revision) and model solutions.
- **Persistent Sessions & Chat History**:
  - Powered by local **SQLite** (`learnmate.db`) with cascading deletes and indexing.
  - Reopen past sessions, rename them, continue conversations, or delete completed ones.
- **Conversational Context (Multi-Turn Chat)**:
  - Maintains conversation history across follow-ups so you can ask "Why?" or "Show me a C++ implementation" without re-explaining the topic.
- **Multi-Format Study Note Exports**:
  - 📝 **Markdown (`.md`)**: Formatted for Obsidian, Notion, or GitHub.
  - 📄 **Plain Text (`.txt`)**: Clean text format for quick reading.
  - 📑 **PDF (`.pdf`)**: Styled document with headers, metadata, and auto-pagination via `fpdf2`.
- **Security & Cloud Ready**:
  - Safe API key handling via `.env` or Streamlit Community Cloud secrets (`st.secrets`).
  - Zero API key leaks; protected by `.gitignore`.

---

## 🏗️ Architecture & Project Structure

```text
LearnMate-AI/
├── .venv/               # Virtual environment (Python 3.10+)
├── .env                 # Local secrets / GEMINI_API_KEY (git-ignored)
├── .env.example         # Template for environment configuration
├── .gitignore           # Excludes .venv, .env, *.db, cache files
├── app.py               # Main Streamlit UI, session management & execution
├── database.py          # SQLite persistence layer (sessions & interactions)
├── prompts.py           # Pedagogical system persona and activity templates
├── exporter.py          # Export utility (Markdown, Plain Text, PDF)
├── test_app.py          # Automated test suite (unit & integration tests)
├── requirements.txt     # Python package dependencies
└── README.md            # Complete project documentation
```

---

## 🚦 Roadmap & Implementation Status

| Phase | Milestone | Status | Key Deliverables |
|---|---|:---:|---|
| **Phase 1** | Foundation & UI | ✅ Completed | Folder structure, `.venv`, initial Streamlit UI, `requirements.txt`, `.gitignore` |
| **Phase 2** | AI Persona & Gemini | ✅ Completed | `TUTOR_PERSONA`, modern `google-genai` SDK, secure key loading via `python-dotenv` |
| **Phase 3** | SQLite Storage | ✅ Completed | `database.py` with `sessions` and `interactions` tables, indexing, transactions |
| **Phase 4** | Chat Management | ✅ Completed | Create, reopen, continue, rename, and delete learning sessions in sidebar |
| **Phase 5** | Interactive Learning | ✅ Completed | Multi-turn chat context, answer evaluation (`Evaluate Answer`), follow-ups |
| **Phase 6** | Exports | ✅ Completed | `exporter.py` generating Markdown, TXT, and styled PDF files via `fpdf2` |
| **Phase 7** | UI & UX Refinement | ✅ Completed | Badges, activity icons, session cards, responsive columns, and error handling |
| **Phase 8** | Testing & Deployment | ✅ Completed | `test_app.py` unit test suite, `st.secrets` cloud support, `.env.example` |

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10 or higher installed on Windows, macOS, or Linux.
- A free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 2. Activate the Virtual Environment
- **Windows (PowerShell)**:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **Windows (Command Prompt)**:
  ```cmd
  .\.venv\Scripts\activate.bat
  ```
- **Linux / macOS**:
  ```bash
  source .venv/bin/activate
  ```

### 3. Configure Your Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Open `.env` and set your key:
```env
GEMINI_API_KEY=AIzaSy...your_actual_key_here
```
*(Alternatively, you can type your key into the sidebar directly in the running app).*

### 4. Run the Application
```powershell
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Running the Automated Test Suite

We have included a full test suite verifying database CRUD, prompt generation, export formats, and security rules:
```powershell
python test_app.py
```
Expected output:
```text
....
----------------------------------------------------------------------
Ran 4 tests in 0.151s

OK
```

---

## ☁️ Deploying to Streamlit Community Cloud

1. Push your repository to **GitHub** (ensure `.env` and `*.db` remain in `.gitignore`).
2. Log into [Streamlit Community Cloud](https://share.streamlit.io/).
3. Connect your repository and select `app.py` as the main entry point.
4. Under **Advanced Settings > Secrets**, paste:
   ```toml
   GEMINI_API_KEY = "your_actual_api_key_here"
   ```
5. Click **Deploy**!
