"""Setup screen: candidate enters job role, optionally pastes resume, and configures interview preferences."""

import streamlit as st
from interview.flow import start_interview
from interview.llm import get_api_key
from ui.theme import render_top_bar
from ui.assets import get_hero_room_uri


def render_setup_screen() -> None:
    # 1. Top Bar Contract
    render_top_bar(
        brand_title="APEX INTERVIEWER",
        stage_label="Practice Session · AI Simulation · Audio Enabled",
    )

    # 2. Hero Section with Generated Architectural Visual
    hero_uri = get_hero_room_uri()
    if hero_uri:
        st.markdown(
            f"""
            <div style="
                position: relative;
                border-radius: 14px;
                overflow: hidden;
                margin-bottom: 2rem;
                border: 1px solid #1E293B;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
                height: 220px;
                background: url('{hero_uri}') center center / cover no-repeat;
            ">
                <div style="
                    position: absolute;
                    inset: 0;
                    background: linear-gradient(180deg, rgba(9, 13, 22, 0.4) 0%, rgba(9, 13, 22, 0.88) 85%);
                    display: flex;
                    flex-direction: column;
                    justify-content: flex-end;
                    padding: 1.5rem 2rem;
                ">
                    <div style="font-size: 0.8125rem; font-weight: 600; color: #60A5FA; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 0.25rem;">
                        Interactive Simulation Studio
                    </div>
                    <h1 style="font-size: 1.75rem; font-weight: 700; color: #FFFFFF; margin: 0 0 0.5rem 0; line-height: 1.25;">
                        Master Your Next Technical & Leadership Interview
                    </h1>
                    <div style="font-size: 0.875rem; color: #94A3B8; display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
                        <span>Speech Dictation</span>
                        <span aria-hidden="true">·</span>
                        <span>Voice Audio Output</span>
                        <span aria-hidden="true">·</span>
                        <span>Adaptive Follow-ups</span>
                        <span aria-hidden="true">·</span>
                        <span>Rubric Scored Report</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="interview-card" style="margin-bottom: 2rem;">
                <h1 style="font-size: 1.75rem; font-weight: 700; margin: 0 0 0.5rem 0;">Master Your Next Interview</h1>
                <p style="color: #94A3B8; margin: 0;">Practice one question at a time with realistic follow-up probing, browser speech dictation, and rubric scoring.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    api_key = get_api_key()
    if not api_key:
        st.warning(
            "⚠️ **No GEMINI_API_KEY detected.** Please add your `GEMINI_API_KEY` to the `.env` file "
            "or container environment variables to enable question generation and evaluation."
        )

    # 3. Two-Column Workspace Layout
    col_main, col_sidebar = st.columns([1.8, 1.2], gap="large")

    with col_main:
        st.markdown("### 1. Position & Experience")
        
        role_default = st.session_state.get("role", "")
        role_input = st.text_input(
            "Target Job Role or Specialization *",
            value=role_default,
            placeholder="e.g. Senior Backend Engineer, Staff Machine Learning Lead, Cloud Architect...",
            help="The interviewer tailors technical depth, problem scenarios, and behavioral probes to this title.",
        )

        resume_default = st.session_state.get("resume", "")
        resume_input = st.text_area(
            "Candidate Resume Highlights or Background (Optional)",
            value=resume_default,
            height=160,
            placeholder="Paste your past experience, tech stack (Python, Go, React, Kubernetes), key projects, or achievements here...\n\nIf provided, questions will probe your actual work accomplishments and architectural decisions.",
            help="Optional: Paste text to contextualize technical and background questions.",
        )
        if resume_input:
            st.caption(f"📝 {len(resume_input):,} characters provided · Background loaded for interviewer")

        st.markdown("### 2. Session Format")
        col_q, col_diff = st.columns(2)
        with col_q:
            question_count = st.selectbox(
                "Interview Length",
                options=[4, 6, 8],
                index=1,
                format_func=lambda x: f"{x} Questions (Standard Comprehensive)" if x == 6 else (f"{x} Questions (Fast Mock Drill)" if x == 4 else f"{x} Questions (Staff / In-Depth Drill)"),
                help="Select how many questions the interview will cover before generating your feedback report.",
            )
        with col_diff:
            seniority = st.selectbox(
                "Seniority Target",
                options=["Mid-Level Engineer", "Senior Engineer", "Staff / Principal / Tech Lead"],
                index=1,
                help="Calibrates the interviewer's technical depth, system tradeoffs, and leadership expectations.",
            )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        start_btn = st.button("🚀 Begin Structured Interview", type="primary", use_container_width=True)

        if start_btn:
            clean_role = role_input.strip()
            if not clean_role:
                st.error("Please specify a target job role before starting.")
                return

            full_role_title = f"{seniority} - {clean_role}" if not clean_role.lower().startswith(("senior", "staff", "principal", "lead", "mid")) else clean_role

            start_interview(
                role=full_role_title,
                resume=resume_input,
                enable_voice=st.session_state.get("enable_voice", True),
                enable_voice_input=st.session_state.get("enable_voice_input", True),
                total_questions=question_count,
            )
            st.rerun()

    with col_sidebar:
        # Audio & Voice Settings Card
        st.markdown("### 🎙️ Audio Preferences")
        with st.container():
            st.markdown(
                """
                <div style="background: #111827; border: 1px solid #1E293B; border-radius: 12px; padding: 1.125rem; margin-bottom: 1.25rem;">
                """,
                unsafe_allow_html=True,
            )
            voice_out = st.toggle(
                "🔊 Voice Output (Spoken Questions)",
                value=st.session_state.get("enable_voice", True),
                help="AI Interviewer speaks questions aloud using browser/speech synthesis.",
            )
            auto_play = st.toggle(
                "▶️ Auto-play Spoken Audio",
                value=st.session_state.get("auto_play_voice", True),
                disabled=not voice_out,
                help="Automatically play the question audio as soon as asked.",
            )
            voice_in = st.toggle(
                "🎙️ Voice Input (Web Speech API)",
                value=st.session_state.get("enable_voice_input", True),
                help="Speak your responses directly using your microphone with real-time browser transcription.",
            )
            st.session_state.enable_voice = voice_out
            st.session_state.auto_play_voice = auto_play
            st.session_state.enable_voice_input = voice_in

            st.markdown(
                """
                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 0.5rem; line-height: 1.4;">
                    Candidates can speak or type answers interchangeably at any point during the session.
                </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Quick Preset Roles
        st.markdown("### 📋 Quick Preset Roles")
        st.caption("Click to load a pre-configured target track:")

        presets = [
            ("Senior Python Engineer", "Distributed systems, FastAPI, async architectures"),
            ("Full-Stack Tech Lead", "React, Node.js, system design, API contracts"),
            ("ML / AI Systems Engineer", "LLM integration, pipelines, model deployment"),
            ("DevOps & Cloud Architect", "Kubernetes, CI/CD, AWS/GCP infrastructure"),
            ("Engineering Manager", "Team execution, 1-on-1s, technical strategy"),
        ]

        for title, subtitle in presets:
            col_t, col_b = st.columns([2.2, 0.8])
            with col_t:
                st.markdown(
                    f"""
                    <div style="line-height: 1.3; padding: 4px 0;">
                        <span style="font-size: 0.875rem; font-weight: 600; color: #F8FAFC;">{title}</span><br>
                        <span style="font-size: 0.75rem; color: #64748B;">{subtitle}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_b:
                if st.button("Select", key=f"btn_preset_{title}", use_container_width=True):
                    start_interview(
                        role=title,
                        resume=resume_default,
                        enable_voice=st.session_state.get("enable_voice", True),
                        enable_voice_input=st.session_state.get("enable_voice_input", True),
                        total_questions=6,
                    )
                    st.rerun()
