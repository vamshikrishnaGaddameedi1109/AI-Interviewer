"""Main application entry point for AI Interviewer."""

import streamlit as st
from interview.flow import init_session_state
from ui.setup import render_setup_screen
from ui.chat import render_chat_screen
from ui.report import render_report_screen


def main() -> None:
    # Configure page settings
    st.set_page_config(
        page_title="AI Interviewer",
        page_icon="🎯",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

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
