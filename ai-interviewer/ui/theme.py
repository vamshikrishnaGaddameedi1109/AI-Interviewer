"""Universal theme, typography, and layout styling for AI Interviewer."""

import streamlit as st


GLOBAL_THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* Global Font & Surface Reset */
html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: #090D16 !important;
    color: #F1F5F9 !important;
    -webkit-font-smoothing: antialiased;
}

/* Remove default Streamlit clutter */
#MainMenu, header[data-testid="stHeader"], footer {
    visibility: hidden !important;
    height: 0 !important;
}

div.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1120px !important;
    margin: 0 auto !important;
}

/* Top Navigation Bar */
.top-bar-contract {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.875rem 1.25rem;
    margin-bottom: 1.75rem;
    background: #111827;
    border: 1px solid #1E293B;
    border-radius: 12px;
}

.top-bar-brand {
    font-size: 1.125rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #F8FAFC;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.top-bar-brand-mark {
    width: 10px;
    height: 10px;
    background: #3B82F6;
    border-radius: 2px;
    display: inline-block;
}

.top-bar-nav {
    display: flex;
    align-items: center;
    gap: 1rem;
    font-size: 0.8125rem;
    font-weight: 500;
    color: #94A3B8;
}

.top-bar-nav a {
    color: #94A3B8;
    text-decoration: none;
    transition: color 0.15s ease;
}

.top-bar-nav a:hover {
    color: #F1F5F9;
}

.top-bar-actions {
    display: flex;
    align-items: center;
    gap: 0.625rem;
}

/* Cards & Structural Panels */
.interview-card {
    background: #111827;
    border: 1px solid #1E293B;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.25rem;
    transition: border-color 0.2s ease;
}

.interview-card:hover {
    border-color: #334155;
}

/* Headings with balanced wraps */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    letter-spacing: -0.02em !important;
    text-wrap: balance !important;
    color: #F8FAFC !important;
}

/* Tabular figures for telemetry & scores */
.tabular-data, .metric-value, .score-number {
    font-family: 'JetBrains Mono', monospace !important;
    font-variant-numeric: tabular-nums !important;
}

/* Streamlit Widget Overrides */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] select {
    background-color: #0B0F19 !important;
    border: 1px solid #1E293B !important;
    border-radius: 8px !important;
    color: #F8FAFC !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.9375rem !important;
    padding: 0.625rem 0.875rem !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}

div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
}

/* Labels */
label[data-testid="stWidgetLabel"] p {
    font-size: 0.875rem !important;
    font-weight: 600 !important;
    color: #CBD5E1 !important;
    margin-bottom: 0.375rem !important;
}

/* Buttons */
button[kind="primary"] {
    background: #2563EB !important;
    border: 1px solid #3B82F6 !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.25rem !important;
    font-size: 0.875rem !important;
    transition: all 0.15s ease !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3) !important;
}

button[kind="primary"]:hover {
    background: #1D4ED8 !important;
    border-color: #60A5FA !important;
    transform: translateY(-1px) !important;
}

button[kind="secondary"] {
    background: #111827 !important;
    border: 1px solid #1E293B !important;
    border-radius: 8px !important;
    color: #CBD5E1 !important;
    font-weight: 500 !important;
    padding: 0.5rem 1rem !important;
    font-size: 0.875rem !important;
    transition: all 0.15s ease !important;
}

button[kind="secondary"]:hover {
    background: #1E293B !important;
    border-color: #334155 !important;
    color: #F8FAFC !important;
}

/* Progress bar */
div[data-testid="stProgress"] > div > div > div > div {
    background: linear-gradient(90deg, #2563EB 0%, #38BDF8 100%) !important;
    border-radius: 9999px !important;
}

div[data-testid="stProgress"] > div > div {
    background-color: #1E293B !important;
    border-radius: 9999px !important;
    height: 8px !important;
}

/* Expanders */
div[data-testid="stExpander"] {
    background: #111827 !important;
    border: 1px solid #1E293B !important;
    border-radius: 10px !important;
    margin-bottom: 0.75rem !important;
}

div[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: #F1F5F9 !important;
    padding: 0.75rem 1rem !important;
}

/* Chat Input Bar */
div[data-testid="stChatInput"] {
    background-color: #111827 !important;
    border: 1px solid #1E293B !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
}

div[data-testid="stChatInput"] textarea {
    background-color: transparent !important;
    color: #F8FAFC !important;
    font-size: 0.9375rem !important;
}

/* Chat Message Styling */
div[data-testid="stChatMessage"] {
    background: #111827 !important;
    border: 1px solid #1E293B !important;
    border-radius: 12px !important;
    padding: 1.125rem 1.25rem !important;
    margin-bottom: 1rem !important;
}

div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: #0F172A !important;
    border-color: #2563EB40 !important;
}

/* Alert boxes */
div[data-testid="stAlert"] {
    background: #111827 !important;
    border: 1px solid #1E293B !important;
    border-radius: 8px !important;
    padding: 0.875rem 1.125rem !important;
}

/* Audio Player */
audio {
    filter: invert(0.9) hue-rotate(180deg);
    border-radius: 8px;
    height: 38px;
    width: 100%;
}
</style>
"""


def apply_theme() -> None:
    """Inject global CSS rules into the Streamlit applet."""
    st.markdown(GLOBAL_THEME_CSS, unsafe_allow_html=True)


def render_top_bar(
    brand_title: str = "APEX INTERVIEWER",
    stage_label: str = "Technical & Behavioral Assessment",
    action_button_label: str = "Start New Session",
    on_action_click=None,
) -> None:
    """Renders the standard 3-zone Top Bar Contract."""
    st.markdown(
        f"""
        <div class="top-bar-contract">
          <div class="top-bar-brand">
            <span class="top-bar-brand-mark"></span>
            <span>{brand_title}</span>
          </div>
          <div class="top-bar-nav">
            <span>{stage_label}</span>
          </div>
          <div class="top-bar-actions">
            <span style="font-size: 0.75rem; color: #10B981; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;">
              <span style="width: 6px; height: 6px; background: #10B981; border-radius: 50%;"></span>
              System Ready
            </span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
