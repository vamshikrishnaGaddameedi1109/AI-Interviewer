"""Chat screen: question/answer loop between candidate and AI interviewer with voice input and output."""

import streamlit as st
from interview.llm import call_llm
from interview.prompts import build_question_prompt
from interview.flow import (
    format_conversation_for_prompt,
    should_stop,
    reset_interview,
)
from interview.voice import (
    render_voice_player_widget,
    voice_input_widget,
)
from ui.assets import get_interviewer_avatar_uri, get_candidate_avatar_uri


def render_chat_screen() -> None:
    role = st.session_state.get("role", "Technical Candidate")
    resume = st.session_state.get("resume", "")
    q_num = st.session_state.get("question_number", 1)
    total_q = st.session_state.get("total_questions", 6)
    history = st.session_state.get("conversation_history", [])
    voice_enabled = st.session_state.get("enable_voice", True)
    voice_input_enabled = st.session_state.get("enable_voice_input", True)
    auto_play = st.session_state.get("auto_play_voice", True)

    if "last_played_msg_count" not in st.session_state:
        st.session_state.last_played_msg_count = 0

    # 1. Top Bar Contract
    col_brand, col_stage, col_actions = st.columns([1.6, 1.4, 1.0])
    with col_brand:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; padding-top: 4px;">
                <span style="width: 8px; height: 8px; background: #3B82F6; border-radius: 2px;"></span>
                <span style="font-weight: 700; font-size: 1rem; color: #F8FAFC;">{role}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_stage:
        q_percent = min(max(q_num / total_q, 0.0), 1.0)
        st.markdown(
            f"""
            <div style="font-size: 0.8125rem; color: #94A3B8; text-align: center; font-variant-numeric: tabular-nums;">
                <span style="font-family: 'JetBrains Mono', monospace; color: #60A5FA; font-weight: 600;">Question {q_num:02d} / {total_q:02d}</span>
                <span style="margin: 0 6px;">·</span>
                <span>Active Simulation</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(q_percent)
    with col_actions:
        col_v1, col_v2, col_end = st.columns([1, 1, 1])
        with col_v1:
            vout_icon = "🔊" if voice_enabled else "🔇"
            if st.button(vout_icon, help="Toggle AI voice reading aloud"):
                st.session_state.enable_voice = not voice_enabled
                st.rerun()
        with col_v2:
            vin_icon = "🎙️" if voice_input_enabled else "🎙️ OFF"
            if st.button(vin_icon, help="Toggle microphone speech input"):
                st.session_state.enable_voice_input = not voice_input_enabled
                st.rerun()
        with col_end:
            if st.button("⏹️", help="End session early and view report"):
                if any(m.get("role") == "user" for m in history):
                    st.session_state.screen = "report"
                    st.rerun()
                else:
                    reset_interview()
                    st.rerun()

    st.markdown("<hr style='border: none; border-top: 1px solid #1E293B; margin: 1rem 0 1.5rem 0;'>", unsafe_allow_html=True)

    # 2. Answering Strategy Guide (Collapsible Drawer)
    with st.expander("💡 Candidate Strategy & Answering Framework (Click to expand)", expanded=False):
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.markdown("**S — Situation**\n\nSet context, team scope, and the baseline challenge.")
        with col_s2:
            st.markdown("**T — Task**\n\nDefine your specific role and objective.")
        with col_s3:
            st.markdown("**A — Action**\n\nDetail technical decisions, tradeoffs, and tools used.")
        with col_s4:
            st.markdown("**R — Result**\n\nState measurable outcomes (latency, uptime, revenue).")

    # 3. Generate Question 1 if conversation has not begun
    assistant_msgs = [m for m in history if m.get("role") in ("assistant", "model")]
    if not assistant_msgs:
        with st.spinner("Interviewer is reviewing your profile and preparing the opening question..."):
            try:
                opening_prompt = build_question_prompt(
                    role=role,
                    resume_text=resume,
                    question_number=1,
                    total_questions=total_q,
                    conversation_history="",
                )
                question_1 = call_llm(opening_prompt, temperature=0.7)
                st.session_state.conversation_history.append(
                    {"role": "assistant", "content": question_1}
                )
                st.rerun()
            except Exception as e:
                st.error(
                    f"⚠️ **Unable to initiate interview session:** {str(e)}\n\n"
                    "The service may be experiencing high demand. Please click Retry below."
                )
                col_retry, col_back = st.columns(2)
                with col_retry:
                    if st.button("🔄 Retry Opening Question", type="primary", use_container_width=True):
                        st.rerun()
                with col_back:
                    if st.button("⬅️ Back to Setup", use_container_width=True):
                        reset_interview()
                        st.rerun()
                return

    # 4. Render Conversation History with Studio Avatars
    interviewer_avatar = get_interviewer_avatar_uri() or "🤖"
    candidate_avatar = get_candidate_avatar_uri() or "👤"

    assistant_count = 0
    total_assistant_msgs = len([m for m in st.session_state.conversation_history if m.get("role") in ("assistant", "model")])

    for idx, msg in enumerate(st.session_state.conversation_history):
        role_type = msg.get("role")
        content = msg.get("content", "")

        if role_type in ("assistant", "model"):
            assistant_count += 1
            is_latest_question = (assistant_count == total_assistant_msgs)

            with st.chat_message("assistant", avatar=interviewer_avatar):
                st.markdown(
                    f"""
                    <div style="font-size: 0.75rem; font-weight: 600; color: #60A5FA; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 0.35rem;">
                        Senior Interviewer · Question {assistant_count:02d} of {total_q:02d}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(f"<div style='font-size: 1rem; line-height: 1.6; color: #F8FAFC;'>{content}</div>", unsafe_allow_html=True)

                if voice_enabled:
                    should_autoplay = (
                        auto_play
                        and is_latest_question
                        and (st.session_state.last_played_msg_count < total_assistant_msgs)
                    )
                    if should_autoplay:
                        st.session_state.last_played_msg_count = total_assistant_msgs

                    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                    render_voice_player_widget(
                        text=content,
                        autoplay=should_autoplay,
                        msg_idx=idx,
                    )
        else:
            with st.chat_message("user", avatar=candidate_avatar):
                st.markdown(
                    """
                    <div style="font-size: 0.75rem; font-weight: 600; color: #94A3B8; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 0.35rem;">
                        Candidate Response
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(f"<div style='font-size: 0.9375rem; line-height: 1.6; color: #E2E8F0;'>{content}</div>", unsafe_allow_html=True)

    # 5. Handle Pending Assistant Turn After Candidate Responded
    last_msg = st.session_state.conversation_history[-1] if st.session_state.conversation_history else None
    if last_msg and last_msg.get("role") == "user":
        if should_stop(st.session_state.question_number, st.session_state.total_questions):
            st.session_state.screen = "report"
            st.rerun()
            return

        next_q_number = st.session_state.question_number + 1
        formatted_history = format_conversation_for_prompt(st.session_state.conversation_history)
        next_prompt = build_question_prompt(
            role=role,
            resume_text=resume,
            question_number=next_q_number,
            total_questions=total_q,
            conversation_history=formatted_history,
        )

        with st.spinner("Interviewer is analyzing your response and formulating the next question..."):
            try:
                next_question = call_llm(next_prompt, temperature=0.7)
                st.session_state.conversation_history.append(
                    {"role": "assistant", "content": next_question}
                )
                st.session_state.question_number = next_q_number
                st.rerun()
            except Exception as e:
                st.error(
                    f"⚠️ **Could not generate question:** {str(e)}\n\n"
                    "Temporary service spike detected. Click Retry below to continue."
                )
                if st.button("🔄 Retry Generating Next Question", type="primary"):
                    st.rerun()
                return

    # 6. Web Speech API Voice Input Widget (when enabled)
    if voice_input_enabled:
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        spoken_data = voice_input_widget(key=f"voice_input_q_{q_num}")

        if spoken_data and isinstance(spoken_data, dict) and spoken_data.get("action") == "submit":
            spoken_text = spoken_data.get("text", "").strip()
            ts = spoken_data.get("timestamp")

            if spoken_text and ts != st.session_state.get("last_voice_ts"):
                st.session_state.last_voice_ts = ts
                st.session_state.conversation_history.append(
                    {"role": "user", "content": spoken_text}
                )
                st.rerun()
                return

    # 7. Candidate Text Answer Input Bar
    placeholder = (
        "Type your response, or use the microphone widget above..."
        if voice_input_enabled
        else "Type your response to the interviewer..."
    )
    user_input = st.chat_input(placeholder)

    if user_input is not None:
        clean_input = user_input.strip()
        if not clean_input:
            st.warning("Please provide a response before submitting.")
            return

        st.session_state.conversation_history.append(
            {"role": "user", "content": clean_input}
        )
        st.rerun()
