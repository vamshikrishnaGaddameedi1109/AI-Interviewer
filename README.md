# AI Interviewer 🎯

A working MVP of an AI-powered technical and behavioral interviewer web application built with Python, Streamlit, and Google Gemini.

Candidates enter a job role (and optionally paste a resume), answer structured interview questions one at a time, and receive an objective, scored feedback report at the end.

---

## Features

- **Setup Screen**: Enter target job role, optionally paste resume, and configure voice input/output preferences.
- **Voice Input (Web Speech API)**: Speak interview answers directly using your browser's microphone with real-time speech-to-text transcription.
- **Voice Output (Speech Synthesis)**: Questions are spoken aloud using audio speech synthesis with automatic playback and interactive audio controls.
- **Dynamic Interview (6 Questions)**: Conducts a structured multi-topic technical & behavioral interview with realistic follow-up probing.
- **Single-Turn Decision**: Generates questions and natural follow-up decisions in a single LLM invocation per candidate turn.
- **Comprehensive Scored Report**:
  - Overall performance score (0–100) and recommendation status.
  - 2–3 sentence executive summary.
  - Key strengths and prioritized areas to improve.
  - Per-question breakdown with 0–10 score, candidate answer summary, and constructive feedback.
  - Downloadable JSON session transcript.

---

## Tech Stack

- **Python 3.10+**
- **Streamlit** (multi-screen navigation via `st.session_state`)
- **Google Gemini** (`google-genai` official Python SDK, model `gemini-3.8-flash`)
- **python-dotenv** for environment configuration

---

## Folder Structure

```text
ai-interviewer/
├── app.py
├── interview/
│   ├── __init__.py
│   ├── flow.py         # Session state helpers, question counter, stop condition
│   ├── prompts.py      # System prompt + templates as constants/functions
│   ├── evaluator.py    # Builds evaluation prompt, calls LLM, parses JSON
│   └── llm.py          # Single wrapper function call_llm(messages, temperature)
├── ui/
│   ├── __init__.py
│   ├── setup.py        # Role + resume input screen
│   ├── chat.py         # Question/answer loop screen
│   └── report.py       # Final score screen
├── data/sessions/       # Gitignored optional JSON session transcripts
├── .env.example
├── requirements.txt
└── README.md
```

---

## Setup & Running Locally

1. **Clone or navigate to the project repository**:
   ```bash
   cd ai-interviewer
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your API Key**:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and set your `GEMINI_API_KEY`:
   ```env
   GEMINI_API_KEY="your_api_key_here"
   ```

5. **Run the Streamlit application**:
   ```bash
   streamlit run app.py
   ```
   Open your browser at `http://localhost:8501` (or port specified in Streamlit console).
