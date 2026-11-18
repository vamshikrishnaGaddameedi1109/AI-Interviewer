"""Chat screen: question/answer loop between candidate and AI interviewer with voice input and output."""

import streamlit as st
from interview.llm import call_llm
from interview.prompts import (
    build_batch_questions_messages,
    parse_questions_json,
    MAX_QUESTIONS_PER_REQUEST,
)
from interview.flow import reset_interview
from interview.voice import (
    render_voice_player_widget,
    voice_input_widget,
)
from ui.assets import get_interviewer_avatar_uri, get_candidate_avatar_uri
from ui.theme import render_header


def _render_generation_error(error_msg: str) -> None:
    """Display generation failure clearly with Retry and Back to Setup actions."""
    st.error(f"⚠️ Unable to generate interview questions: {error_msg}")
    col_retry, col_reset = st.columns(2)
    with col_retry:
        if st.button("🔄 Retry", key="retry_question_gen_btn", type="primary", use_container_width=True):
            st.session_state.last_error = None
            st.session_state.generating_questions = False
            st.rerun()
    with col_reset:
        if st.button("⬅️ Back to Setup", key="back_to_setup_btn", use_container_width=True):
            reset_interview()
            st.rerun()


def _ensure_next_question(role: str, resume: str, total_q: int, next_q_num: int) -> bool:
    """
    Ensure question `next_q_num` exists in `generated_questions` and append it to
    `conversation_history`. Uses batch generation (up to 5 questions per request)
    with single-flight guarding, a loading indicator, and Retry UI on failure.
    Returns True only if ready; otherwise triggers rerun or renders Retry UI and returns False.
    """
    generated = st.session_state.get("generated_questions", [])
    if len(generated) >= next_q_num:
        next_question = generated[next_q_num - 1]
        st.session_state.conversation_history.append(
            {"role": "assistant", "content": next_question}
        )
        st.session_state.question_number = next_q_num
        st.session_state.last_error = None
        st.rerun()
        return True

    # Do not re-fire Gemini automatically while showing an existing error; wait for user Retry.
    if st.session_state.get("last_error"):
        _render_generation_error(st.session_state.last_error)
        return False

    # Prevent simultaneous duplicate Gemini requests across reruns.
    if st.session_state.get("generating_questions"):
        st.info("Generating interview questions... please wait.")
        return False

    remaining_needed = max(1, total_q - len(generated))
    batch_count = min(remaining_needed, MAX_QUESTIONS_PER_REQUEST)

    st.session_state.generating_questions = True
    try:
        with st.status(
            f"Generating {batch_count} tailored interview questions...",
            expanded=True,
        ) as status:
            st.write(f"Reviewing your **{role}** profile and preparing your question set...")
            messages = build_batch_questions_messages(
                role=role,
                resume_text=resume,
                count=batch_count,
                existing_questions=generated,
            )
            raw_response = call_llm(
                messages,
                temperature=0.6,
                json_mode=True,
                max_output_tokens=700,
                disable_thinking=True,
                timeout_ms=12000,
            )
            new_questions = parse_questions_json(raw_response, max_count=batch_count)
            st.session_state.generated_questions = generated + new_questions
            st.session_state.last_error = None
            status.update(label="Interview questions ready!", state="complete", expanded=False)

        next_question = st.session_state.generated_questions[next_q_num - 1]
        st.session_state.conversation_history.append(
            {"role": "assistant", "content": next_question}
        )
        st.session_state.question_number = next_q_num
        st.rerun()
        return True
    except Exception as e:
        st.session_state.last_error = str(e)
        _render_generation_error(str(e))
        return False
    finally:
        st.session_state.generating_questions = False


def render_chat_screen() -> None:
    role = st.session_state.get("role", "Technical Candidate")
    resume = st.session_state.get("resume", "")
    q_num = st.session_state.get("question_number", 1)
    total_q = st.session_state.get("total_questions", 5)
    history = st.session_state.get("conversation_history", [])
    voice_enabled = st.session_state.get("enable_voice", True)
    voice_input_enabled = st.session_state.get("enable_voice_input", True)
    auto_play = st.session_state.get("auto_play_voice", True)

    if "last_played_msg_count" not in st.session_state:
        st.session_state.last_played_msg_count = 0

    # Immediate redirect if candidate has already answered all questions
    last_msg_early = history[-1] if history else None
    user_answers_early = len([m for m in history if m.get("role") == "user"])
    if last_msg_early and last_msg_early.get("role") == "user" and user_answers_early >= total_q:
        st.session_state.screen = "report"
        st.rerun()
        return

    # 1. Top Header with Step indicator
    render_header(current_screen="chat")

    # 2. Status & Quick Actions Bar
    col_info, col_progress, col_actions = st.columns([1.6, 1.4, 1.3])
    with col_info:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px; padding-top: 2px;">
                <span style="width: 8px; height: 8px; background: #38BDF8; border-radius: 50%; box-shadow: 0 0 6px #38BDF8;"></span>
                <span style="font-weight: 700; font-size: 0.95rem; color: #F8FAFC;">{role}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_progress:
        q_display = min(q_num, total_q)
        pct = min(max(q_display / total_q, 0.0), 1.0)
        st.markdown(
            f"""
            <div style="font-size: 0.8125rem; color: #94A3B8; text-align: center; font-variant-numeric: tabular-nums;">
                <span style="font-family: 'JetBrains Mono', monospace; color: #38BDF8; font-weight: 700;">Question {q_display:02d} / {total_q:02d}</span>
                <span style="margin: 0 6px; color: #475569;">·</span>
                <span style="color: #CBD5E1;">Active Simulation</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(pct)

    with col_actions:
        has_answers = any(m.get("role") == "user" for m in history)
        col_v1, col_v2, col_fin = st.columns([1, 1, 2.2])
        with col_v1:
            v_icon = "🔊" if voice_enabled else "🔇"
            if st.button(v_icon, help="Toggle AI voice reading aloud"):
                st.session_state.enable_voice = not voice_enabled
                st.rerun()
        with col_v2:
            mic_icon = "🎙️" if voice_input_enabled else "🎙️❌"
            if st.button(mic_icon, help="Toggle microphone input"):
                st.session_state.enable_voice_input = not voice_input_enabled
                st.rerun()
        with col_fin:
            if st.button("📊 View Score & Suggestions", help="Finish interview and generate score & improvement report", type="primary" if has_answers else "secondary"):
                if has_answers:
                    st.session_state.screen = "report"
                    st.rerun()
                else:
                    st.toast("Please answer at least one question before viewing evaluation.", icon="ℹ️")

    st.markdown("<hr style='border: none; border-top: 1px solid #1E293B; margin: 0.75rem 0 1.25rem 0;'>", unsafe_allow_html=True)

    # 3. STAR Framework Quick Reminder for Freshers
    with st.expander("💡 Fresher Answering Guide: Structuring Your Project & Behavioral Answers", expanded=False):
        c_s, c_t, c_a, c_r = st.columns(4)
        with c_s:
            st.markdown("<span style='color: #38BDF8; font-weight:700;'>S — Situation</span><br><span style='font-size: 0.8125rem; color:#94A3B8;'>Name your college project, hackathon, or internship challenge.</span>", unsafe_allow_html=True)
        with c_t:
            st.markdown("<span style='color: #38BDF8; font-weight:700;'>T — Task</span><br><span style='font-size: 0.8125rem; color:#94A3B8;'>What specific feature, bug fix, or algorithm were you responsible for?</span>", unsafe_allow_html=True)
        with c_a:
            st.markdown("<span style='color: #38BDF8; font-weight:700;'>A — Action</span><br><span style='font-size: 0.8125rem; color:#94A3B8;'>Explain the programming language, logic, and tools you chose.</span>", unsafe_allow_html=True)
        with c_r:
            st.markdown("<span style='color: #10B981; font-weight:700;'>R — Result</span><br><span style='font-size: 0.8125rem; color:#94A3B8;'>What was the outcome? How did you test it, and what did you learn?</span>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 0.8rem; color: #64748B; margin-top: 6px;'>Tip: In technical questions, state your approach out loud, mention time/space complexity (Big-O), and give code examples!</div>", unsafe_allow_html=True)

    # 4. Generate initial question batch (up to 5 questions) if conversation has not begun
    assistant_msgs = [m for m in history if m.get("role") in ("assistant", "model")]
    if not assistant_msgs:
        _ensure_next_question(role=role, resume=resume, total_q=total_q, next_q_num=1)
        return

    # 5. Render Conversation History with Studio Avatars
    interviewer_avatar = get_interviewer_avatar_uri() or "🤖"
    candidate_avatar = get_candidate_avatar_uri() or "👤"

    assistant_count = 0
    total_assistant_msgs = len([m for m in st.session_state.conversation_history if m.get("role") in ("assistant", "model")])

    for idx, msg in enumerate(st.session_state.conversation_history):
        role_type = msg.get("role")
        content = msg.get("content", "")

        if role_type in ("assistant", "model"):
            assistant_count += 1
            is_latest = (assistant_count == total_assistant_msgs)

            with st.chat_message("assistant", avatar=interviewer_avatar):
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.35rem;">
                        <span style="font-size: 0.75rem; font-weight: 700; color: #38BDF8; letter-spacing: 0.05em; text-transform: uppercase;">
                            Technical Interviewer · Question {assistant_count:02d} of {total_q:02d}
                        </span>
                    </div>
                    <div style="font-size: 1rem; line-height: 1.6; color: #F8FAFC; margin-bottom: 0.5rem;">
                        {content}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if voice_enabled:
                    should_autoplay = (
                        auto_play
                        and is_latest
                        and (st.session_state.last_played_msg_count < total_assistant_msgs)
                    )
                    if should_autoplay:
                        st.session_state.last_played_msg_count = total_assistant_msgs

                    render_voice_player_widget(
                        text=content,
                        autoplay=should_autoplay,
                        msg_idx=idx,
                    )
        else:
            with st.chat_message("user", avatar=candidate_avatar):
                st.markdown(
                    """
                    <div style="font-size: 0.75rem; font-weight: 700; color: #94A3B8; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 0.35rem;">
                        Your Response
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(f"<div style='font-size: 0.95rem; line-height: 1.6; color: #E2E8F0;'>{content}</div>", unsafe_allow_html=True)

    # 6. Handle Next Turn if Candidate just answered
    last_msg = st.session_state.conversation_history[-1] if st.session_state.conversation_history else None
    if last_msg and last_msg.get("role") == "user":
        # Check if interview question limit has been reached
        user_responses_count = len([m for m in st.session_state.conversation_history if m.get("role") == "user"])
        if user_responses_count >= total_q:
            st.session_state.screen = "report"
            st.rerun()
            return

        next_q_num = user_responses_count + 1
        _ensure_next_question(role=role, resume=resume, total_q=total_q, next_q_num=next_q_num)
        return

    # 7. Voice Dictation Widget
    if voice_input_enabled:
        st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
        spoken_data = voice_input_widget(key=f"voice_input_q_{q_num}_{len(history)}")

        if spoken_data and isinstance(spoken_data, dict) and spoken_data.get("action") == "submit":
            spoken_text = spoken_data.get("text", "").strip()
            ts = spoken_data.get("timestamp")

            if spoken_text and ts != st.session_state.get("last_voice_ts"):
                st.session_state.last_voice_ts = ts
                st.session_state.conversation_history.append(
                    {"role": "user", "content": spoken_text}
                )
                if len([m for m in st.session_state.conversation_history if m.get("role") == "user"]) >= total_q:
                    st.session_state.screen = "report"
                st.rerun()
                return

    # 8. Text Input Bar
    placeholder = (
        "Type your answer here, or click the mic button above to speak..."
        if voice_input_enabled
        else "Type your answer here and press Enter..."
    )
    user_input = st.chat_input(placeholder)

    if user_input is not None:
        clean_input = user_input.strip()
        if not clean_input:
            st.warning("Please enter a response before submitting.")
            return

        st.session_state.conversation_history.append(
            {"role": "user", "content": clean_input}
        )
        if len([m for m in st.session_state.conversation_history if m.get("role") == "user"]) >= total_q:
            st.session_state.screen = "report"
        st.rerun()
