"""Main application entry point for AI Interviewer."""

import os
import sys

_PYLIBS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "__pypackages__")
if os.path.isdir(_PYLIBS_DIR) and _PYLIBS_DIR not in sys.path:
    sys.path.insert(0, _PYLIBS_DIR)

import streamlit as st
from interview.flow import init_session_state
from ui.theme import apply_theme
from ui.setup import render_setup_screen
from ui.chat import render_chat_screen
from ui.report import render_report_screen


def main() -> None:
    # Configure page settings with wide layout for responsive desktop presence
    st.set_page_config(
        page_title="AI Technical & Behavioral Interviewer",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Apply global modern typography, palette, and component design
    apply_theme()

    # Initialize all session state variables
    init_session_state()

    # Screen routing based on session state
    current_screen = st.session_state.get("screen", "setup")

    if current_screen == "setup":
        render_setup_screen()
    elif current_screen == "chat":
        render_chat_screen()
    elif current_screen == "report":
        render_report_screen()
    else:
        st.session_state.screen = "setup"
        render_setup_screen()


if __name__ == "__main__":
    main()
