"""Universal theme, typography, and layout styling for AI Interviewer."""

import streamlit as st


GLOBAL_THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

/* Global Font & Surface Reset */
html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    background-color: #070B14 !important;
    color: #F1F5F9 !important;
    -webkit-font-smoothing: antialiased;
}

/* Remove default Streamlit clutter */
#MainMenu, header[data-testid="stHeader"], footer {
    visibility: hidden !important;
    height: 0 !important;
}

div.block-container {
    padding-top: 1.25rem !important;
    padding-bottom: 3.5rem !important;
    max-width: 1180px !important;
    margin: 0 auto !important;
}

/* App Header & Step Navigation Bar */
.apex-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.875rem 1.5rem;
    margin-bottom: 1.75rem;
    background: #0E1526;
    border: 1px solid #1E293B;
    border-radius: 14px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
}

.apex-brand {
    font-size: 1.125rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #F8FAFC;
    display: flex;
    align-items: center;
    gap: 0.625rem;
}

.apex-brand-badge {
    width: 22px;
    height: 22px;
    background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 10px rgba(59, 130, 246, 0.4);
}

.apex-steps {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    font-size: 0.8125rem;
    font-weight: 600;
}

.step-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #64748B;
    transition: color 0.15s ease;
}

.step-item.active {
    color: #38BDF8;
}

.step-item.completed {
    color: #10B981;
}

.step-num {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #1E293B;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.6875rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
}

.step-item.active .step-num {
    background: #0284C7;
    color: #FFFFFF;
    box-shadow: 0 0 8px rgba(56, 189, 248, 0.5);
}

.step-item.completed .step-num {
    background: #059669;
    color: #FFFFFF;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    letter-spacing: -0.025em !important;
    color: #F8FAFC !important;
    font-weight: 700 !important;
}

/* Score displays */
.score-mono {
    font-family: 'JetBrains Mono', monospace !important;
    font-variant-numeric: tabular-nums !important;
}

/* Cards & Containers */
.glass-card {
    background: #0F172A;
    border: 1px solid #1E293B;
    border-radius: 14px;
    padding: 1.5rem;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.glass-card:hover {
    border-color: #334155;
}

/* Streamlit Inputs */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background-color: #0A0F1D !important;
    border: 1px solid #1E293B !important;
    border-radius: 10px !important;
    color: #F8FAFC !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.9375rem !important;
    transition: all 0.15s ease !important;
}

div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.25) !important;
}

/* Buttons */
button[kind="primary"] {
    background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
    border: 1px solid #3B82F6 !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.4rem !important;
    font-size: 0.9375rem !important;
    transition: all 0.15s ease !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3) !important;
}

button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%) !important;
    border-color: #60A5FA !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(37, 99, 235, 0.45) !important;
}

button[kind="secondary"] {
    background: #0E1626 !important;
    border: 1px solid #1E293B !important;
    border-radius: 10px !important;
    color: #CBD5E1 !important;
    font-weight: 600 !important;
    padding: 0.55rem 1.15rem !important;
    font-size: 0.875rem !important;
    transition: all 0.15s ease !important;
}

button[kind="secondary"]:hover {
    background: #17233D !important;
    border-color: #334155 !important;
    color: #F8FAFC !important;
}

/* Progress bar */
div[data-testid="stProgress"] > div > div > div > div {
    background: linear-gradient(90deg, #3B82F6 0%, #38BDF8 50%, #10B981 100%) !important;
    border-radius: 9999px !important;
}

div[data-testid="stProgress"] > div > div {
    background-color: #172033 !important;
    border-radius: 9999px !important;
    height: 9px !important;
}

/* Streamlit Tabs */
div[data-testid="stTabs"] button[role="tab"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9375rem !important;
    color: #94A3B8 !important;
    padding: 0.75rem 1.25rem !important;
    border-radius: 8px 8px 0 0 !important;
    transition: all 0.15s ease !important;
}

div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #38BDF8 !important;
    border-bottom: 2px solid #38BDF8 !important;
    background: rgba(56, 189, 248, 0.05) !important;
}

/* Chat Input Bar */
div[data-testid="stChatInput"] {
    background-color: #0E1626 !important;
    border: 1px solid #23334F !important;
    border-radius: 14px !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4) !important;
}

div[data-testid="stChatInput"] textarea {
    color: #F8FAFC !important;
    font-size: 0.95rem !important;
}

/* Chat Messages */
div[data-testid="stChatMessage"] {
    background: #0E1626 !important;
    border: 1px solid #1E293B !important;
    border-radius: 14px !important;
    padding: 1.25rem 1.4rem !important;
    margin-bottom: 1.15rem !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.25) !important;
}

div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: #091326 !important;
    border-color: #1E3A8A !important;
}

/* Audio Player */
audio {
    filter: invert(0.9) hue-rotate(180deg);
    border-radius: 8px;
    height: 36px;
    width: 100%;
}

/* Pulse animation for active simulation indicator */
@keyframes apexPulse {
    0% { transform: scale(0.95); opacity: 0.7; }
    50% { transform: scale(1.15); opacity: 1; }
    100% { transform: scale(0.95); opacity: 0.7; }
}

.live-pulse-dot {
    width: 8px;
    height: 8px;
    background-color: #10B981;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 8px #10B981;
    animation: apexPulse 2s infinite ease-in-out;
}
</style>
"""


def apply_theme() -> None:
    """Inject global CSS rules into the Streamlit applet."""
    st.markdown(GLOBAL_THEME_CSS, unsafe_allow_html=True)


def render_header(current_screen: str = "setup") -> None:
    """
    Renders top navigation header with clean stage indicator:
    1. Setup & Profile -> 2. Live Interview -> 3. Score & Improvement Report
    """
    s1_class = "completed" if current_screen in ("chat", "report") else "active"
    s2_class = "completed" if current_screen == "report" else ("active" if current_screen == "chat" else "")
    s3_class = "active" if current_screen == "report" else ""

    st.markdown(
        f"""
        <div class="apex-header">
            <div class="apex-brand">
                <div class="apex-brand-badge">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                    </svg>
                </div>
                <span>APEX INTERVIEWER</span>
            </div>
            <div class="apex-steps">
                <div class="step-item {s1_class}">
                    <span class="step-num">1</span>
                    <span>Setup</span>
                </div>
                <span style="color: #334155;">→</span>
                <div class="step-item {s2_class}">
                    <span class="step-num">2</span>
                    <span>Interview</span>
                </div>
                <span style="color: #334155;">→</span>
                <div class="step-item {s3_class}">
                    <span class="step-num">3</span>
                    <span>Score & Advice</span>
                </div>
            </div>
            <div>
                <span style="font-size: 0.75rem; color: #10B981; font-weight: 600; display: inline-flex; align-items: center; gap: 6px;">
                    <span class="live-pulse-dot"></span>
                    Simulation Ready
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
