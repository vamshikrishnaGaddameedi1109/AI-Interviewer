"""Session state management, flow control, and transcript formatting."""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import streamlit as st

TOTAL_QUESTIONS: int = 6
SESSIONS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sessions")


def init_session_state() -> None:
    """Initialize all session state variables if they do not exist."""
    if "screen" not in st.session_state:
        st.session_state.screen = "setup"
    if "role" not in st.session_state:
        st.session_state.role = ""
    if "resume" not in st.session_state:
        st.session_state.resume = ""
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "question_number" not in st.session_state:
        st.session_state.question_number = 1
    if "total_questions" not in st.session_state:
        st.session_state.total_questions = TOTAL_QUESTIONS
    if "evaluation_report" not in st.session_state:
        st.session_state.evaluation_report = None
    if "last_error" not in st.session_state:
        st.session_state.last_error = None
    if "enable_voice" not in st.session_state:
        st.session_state.enable_voice = True
    if "enable_voice_input" not in st.session_state:
        st.session_state.enable_voice_input = True
    if "auto_play_voice" not in st.session_state:
        st.session_state.auto_play_voice = True
    if "last_voice_ts" not in st.session_state:
        st.session_state.last_voice_ts = None


def start_interview(
    role: str,
    resume: str,
    enable_voice: bool = True,
    enable_voice_input: bool = True,
) -> None:
    """Transition state from setup to chat screen."""
    st.session_state.role = role.strip()
    st.session_state.resume = resume.strip()
    st.session_state.enable_voice = enable_voice
    st.session_state.enable_voice_input = enable_voice_input
    st.session_state.conversation_history = []
    st.session_state.question_number = 1
    st.session_state.total_questions = TOTAL_QUESTIONS
    st.session_state.evaluation_report = None
    st.session_state.last_error = None
    st.session_state.last_voice_ts = None
    st.session_state.screen = "chat"


def format_conversation_for_prompt(history: List[Dict[str, str]]) -> str:
    """Format conversation history list into a plain text representation for the LLM prompt."""
    if not history:
        return "No conversation yet."

    lines = []
    for item in history:
        role = item.get("role", "user")
        content = item.get("content", "").strip()
        speaker = "Interviewer" if role in ("assistant", "model") else "Candidate"
        lines.append(f"{speaker}: {content}")

    return "\n".join(lines)


def should_stop(question_number: int, total_questions: int = TOTAL_QUESTIONS) -> bool:
    """Check if the interview has reached its fixed question limit."""
    return question_number >= total_questions


def reset_interview() -> None:
    """Reset session state back to the setup screen."""
    st.session_state.screen = "setup"
    st.session_state.role = ""
    st.session_state.resume = ""
    st.session_state.conversation_history = []
    st.session_state.question_number = 1
    st.session_state.total_questions = TOTAL_QUESTIONS
    st.session_state.evaluation_report = None
    st.session_state.last_error = None
    st.session_state.last_voice_ts = None


def save_session_to_json(
    role: str,
    resume: str,
    conversation_history: List[Dict[str, str]],
    evaluation_report: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """
    Optionally dumps the completed interview session to a JSON file in data/sessions/.
    Returns the file path if successful, or None on error.
    """
    try:
        os.makedirs(SESSIONS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_role = "".join(c for c in role if c.isalnum() or c in ("-", "_")).lower() or "interview"
        filename = f"{timestamp}_{safe_role}.json"
        filepath = os.path.join(SESSIONS_DIR, filename)

        session_data = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "resume": resume,
            "total_questions": len([m for m in conversation_history if m.get("role") == "assistant"]),
            "conversation_history": conversation_history,
            "evaluation_report": evaluation_report,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)

        return filepath
    except Exception as e:
        print(f"Warning: Failed to save session to JSON: {e}")
        return None
