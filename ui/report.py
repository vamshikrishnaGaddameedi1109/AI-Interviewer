"""Report screen: displays calibrated score, category rubrics, actionable suggestions to improve, and model answer transformations."""

import json
import streamlit as st
from interview.evaluator import evaluate_interview
from interview.flow import reset_interview, save_session_to_json
from ui.theme import render_header


def _render_evaluation_error(error_msg: str) -> None:
    """Render evaluation failure with stable Retry and Start New Session buttons."""
    st.error(f"⚠️ Evaluation Error: {error_msg}")
    col_retry, col_reset = st.columns(2)
    with col_retry:
        if st.button("🔄 Retry Evaluation", key="retry_eval_btn", type="primary", use_container_width=True):
            st.session_state.evaluation_error = None
            st.session_state.evaluation_report = None
            st.rerun()
    with col_reset:
        if st.button("⬅️ Start New Session", key="reset_eval_btn", use_container_width=True):
            st.session_state.evaluation_error = None
            reset_interview()
            st.rerun()


def render_report_screen() -> None:
    role = st.session_state.get("role", "Technical Candidate")
    resume = st.session_state.get("resume", "")
    history = st.session_state.get("conversation_history", [])

    # 1. Top Header with Step Indicator (Step 3: Score & Advice)
    render_header(current_screen="report")

    # Guard: if no conversation history exists
    user_msgs = [m for m in history if m.get("role") == "user"]
    if not user_msgs:
        st.warning("No candidate responses found to evaluate. Please complete at least one question.")
        if st.button("⬅️ Return to Interview"):
            st.session_state.screen = "chat"
            st.rerun()
        return

    # Call evaluator on first load (with single-flight and error guards)
    if st.session_state.get("evaluation_report") is None:
        if st.session_state.get("evaluation_error"):
            _render_evaluation_error(st.session_state.evaluation_error)
            return

        if st.session_state.get("evaluating_report"):
            st.info("Analyzing your interview responses... please wait.")
            return

        st.session_state.evaluating_report = True
        try:
            with st.status("Analyzing your interview responses...", expanded=True) as status:
                try:
                    st.write(f"Reviewing {len(user_msgs)} candidate responses for **{role}**...")
                    report_data = evaluate_interview(
                        role=role,
                        resume_text=resume,
                        conversation_history=history,
                    )
                    st.session_state.evaluation_report = report_data
                    st.session_state.evaluation_error = None

                    saved_path = save_session_to_json(
                        role=role,
                        resume=resume,
                        conversation_history=history,
                        evaluation_report=report_data,
                    )
                    st.session_state.saved_session_file = saved_path
                    status.update(label="Evaluation complete!", state="complete", expanded=False)
                except Exception as e:
                    st.session_state.evaluation_error = str(e)
                    status.update(label="Evaluation failed", state="error", expanded=True)
        finally:
            st.session_state.evaluating_report = False

        if st.session_state.get("evaluation_error"):
            _render_evaluation_error(st.session_state.evaluation_error)
            return

    report = st.session_state.evaluation_report

    overall_score = int(report.get("overall_score", 70))
    overall_summary = report.get("overall_summary", "")
    rec_decision = report.get("hiring_recommendation", "")
    category_scores = report.get("category_scores", {})
    strengths = report.get("strengths", [])
    actionable_suggestions = report.get("actionable_suggestions", [])
    model_transformation = report.get("model_answer_transformation", {})
    study_topics = report.get("study_topics", [])
    comm_coaching = report.get("communication_coaching", {})
    question_breakdown = report.get("question_breakdown", [])

    # Letter grade and status badge
    if overall_score >= 90:
        grade = "A+"
        rec_label = rec_decision or "STRONG HIRE"
        rec_color = "#10B981"
        rec_bg = "rgba(16, 185, 129, 0.12)"
        rec_border = "rgba(16, 185, 129, 0.4)"
    elif overall_score >= 80:
        grade = "A"
        rec_label = rec_decision or "STRONG HIRE"
        rec_color = "#10B981"
        rec_bg = "rgba(16, 185, 129, 0.12)"
        rec_border = "rgba(16, 185, 129, 0.4)"
    elif overall_score >= 70:
        grade = "B+"
        rec_label = rec_decision or "HIRE / QUALIFIED"
        rec_color = "#38BDF8"
        rec_bg = "rgba(56, 189, 248, 0.12)"
        rec_border = "rgba(56, 189, 248, 0.4)"
    elif overall_score >= 60:
        grade = "B"
        rec_label = rec_decision or "LEANING HIRE"
        rec_color = "#F59E0B"
        rec_bg = "rgba(245, 158, 11, 0.12)"
        rec_border = "rgba(245, 158, 11, 0.4)"
    else:
        grade = "C"
        rec_label = rec_decision or "NEEDS PREPARATION"
        rec_color = "#EF4444"
        rec_bg = "rgba(239, 68, 68, 0.12)"
        rec_border = "rgba(239, 68, 68, 0.4)"

    # 2. Executive Score Hero Card
    st.markdown(
        f"""
        <div style="background: #0E1626; border: 1px solid #1E293B; border-radius: 16px; padding: 2rem; margin-bottom: 1.75rem; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);">
            <div style="display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; gap: 2rem;">
                <div style="flex: 1; min-width: 300px;">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.5rem;">
                        <span style="font-size: 0.8125rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em;">
                            Candidate Assessment Report
                        </span>
                        <span style="color: #475569;">·</span>
                        <span style="font-size: 0.8125rem; color: #38BDF8; font-weight: 600;">{role}</span>
                    </div>
                    <div style="display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px; border-radius: 8px; background: {rec_bg}; border: 1px solid {rec_border}; color: {rec_color}; font-size: 0.875rem; font-weight: 800; letter-spacing: 0.04em; margin-bottom: 1.15rem;">
                        <span>●</span>
                        <span>RECOMMENDATION: {rec_label.upper()}</span>
                    </div>
                    <p style="font-size: 1rem; line-height: 1.65; color: #E2E8F0; margin: 0;">
                        {overall_summary}
                    </p>
                </div>
                <div style="text-align: right; min-width: 180px; border-left: 1px solid #1E293B; padding-left: 2rem;">
                    <div style="font-size: 0.75rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.06em;">
                        Calibrated Score
                    </div>
                    <div style="display: flex; align-items: baseline; justify-content: flex-end; gap: 6px; margin: 0.25rem 0;">
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 3.5rem; font-weight: 800; color: #FFFFFF; line-height: 1;">
                            {overall_score}
                        </span>
                        <span style="font-size: 1.25rem; color: #64748B; font-weight: 600;">/100</span>
                    </div>
                    <div style="display: inline-block; padding: 2px 10px; border-radius: 6px; background: #1E293B; font-family: 'JetBrains Mono', monospace; font-size: 0.8125rem; font-weight: 700; color: #38BDF8;">
                        Grade {grade}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Four-Metric Rubric Breakdown Grid
    st.markdown("### 📊 Competency Rubric Scores")
    c1, c2, c3, c4 = st.columns(4)

    metrics = [
        ("Technical Depth", category_scores.get("technical_depth", overall_score), "Architecture & systems knowledge"),
        ("Problem Solving", category_scores.get("problem_solving", overall_score), "Tradeoffs, constraints & scaling"),
        ("Communication", category_scores.get("communication_clarity", overall_score), "STAR clarity & structure"),
        ("Role Alignment", category_scores.get("role_alignment", overall_score), "Domain & seniority match"),
    ]

    for col, (label, val, desc) in zip([c1, c2, c3, c4], metrics):
        with col:
            val_int = int(val)
            pct = min(max(val_int / 100.0, 0.0), 1.0)
            st.markdown(
                f"""
                <div style="background: #0E1626; border: 1px solid #1E293B; border-radius: 12px; padding: 1.15rem 1.25rem;">
                    <div style="font-size: 0.8125rem; font-weight: 700; color: #CBD5E1; margin-bottom: 0.35rem;">
                        {label}
                    </div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.75rem; font-weight: 800; color: #38BDF8;">
                        {val_int}<span style="font-size: 0.875rem; color: #64748B; font-weight: 600;"> / 100</span>
                    </div>
                    <div style="font-size: 0.72rem; color: #64748B; margin-top: 0.25rem; line-height: 1.4;">
                        {desc}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(pct)

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # 4. Tabbed Deep-Dive: Suggestions to Improve, Model Answer, Questions, Full Transcript
    tab_improve, tab_questions, tab_strengths, tab_export = st.tabs([
        "🚀 Suggestions to Improve (Targeted)",
        "📝 Per-Question Review",
        "✅ Key Strengths",
        "📄 Export & Transcript",
    ])

    with tab_improve:
        st.markdown("### 🎯 Priority Action Items for Your Next Interview")
        st.caption("Concrete tactics and feedback generated directly from your responses in this session.")

        if actionable_suggestions:
            for idx, item in enumerate(actionable_suggestions, 1):
                prio = item.get("priority", "High")
                cat = item.get("category", "Interview Technique")
                title = item.get("title", f"Improvement Recommendation #{idx}")
                advice = item.get("advice", "")
                action_item = item.get("action_item", "")

                is_high = prio.lower() == "high"
                badge_bg = "rgba(239, 68, 68, 0.15)" if is_high else "rgba(245, 158, 11, 0.15)"
                badge_color = "#F87171" if is_high else "#FBBF24"
                border_left = "#EF4444" if is_high else "#F59E0B"

                st.markdown(
                    f"""
                    <div style="background: #0E1626; border: 1px solid #1E293B; border-left: 4px solid {border_left}; border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 1rem;">
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem; flex-wrap: wrap; gap: 8px;">
                            <span style="font-weight: 700; font-size: 1.05rem; color: #FFFFFF;">{title}</span>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="font-size: 0.75rem; color: #94A3B8; font-weight: 600;">{cat}</span>
                                <span style="font-size: 0.6875rem; font-weight: 800; padding: 3px 8px; border-radius: 6px; background: {badge_bg}; color: {badge_color}; text-transform: uppercase;">
                                    {prio} Priority
                                </span>
                            </div>
                        </div>
                        <p style="font-size: 0.9375rem; line-height: 1.6; color: #CBD5E1; margin: 0 0 0.75rem 0;">
                            {advice}
                        </p>
                        <div style="background: #090F1C; border: 1px solid #1E293B; border-radius: 8px; padding: 0.75rem 1rem;">
                            <span style="font-size: 0.75rem; font-weight: 700; color: #38BDF8; text-transform: uppercase; letter-spacing: 0.05em;">Action Drill: </span>
                            <span style="font-size: 0.875rem; color: #E2E8F0;">{action_item}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No critical improvement areas identified. You performed at an exceptional caliber!")

        # Model Answer Transformation ("Before vs. After")
        if model_transformation and model_transformation.get("ideal_model_answer"):
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            st.markdown("### 💡 Model Answer Transformation: How to Answer Better")
            st.caption("Here is how to answer this question with clear logic, foundational depth, and structured examples:")

            q_text = model_transformation.get("question", "Challenging Question")
            flaw = model_transformation.get("candidate_flaw", "Needed more concrete impact and architectural tradeoffs.")
            ideal_ans = model_transformation.get("ideal_model_answer", "")
            takeaway = model_transformation.get("key_takeaway", "Structure your answer with STAR and quantify impact.")

            st.markdown(
                f"""
                <div style="background: #0E1626; border: 1px solid #1E293B; border-radius: 14px; padding: 1.5rem; margin-bottom: 1.5rem;">
                    <div style="font-size: 0.8125rem; font-weight: 700; color: #94A3B8; margin-bottom: 0.25rem;">
                        INTERVIEW QUESTION ANALYZED:
                    </div>
                    <div style="font-size: 1rem; font-weight: 600; color: #F8FAFC; margin-bottom: 1rem;">
                        "{q_text}"
                    </div>
                    
                    <div style="background: rgba(239, 68, 68, 0.08); border-left: 3px solid #EF4444; border-radius: 6px; padding: 0.75rem 1rem; margin-bottom: 1rem;">
                        <span style="font-size: 0.75rem; font-weight: 700; color: #F87171; text-transform: uppercase;">Area Lacking in Candidate's Response:</span><br>
                        <span style="font-size: 0.875rem; color: #FCA5A5;">{flaw}</span>
                    </div>

                    <div style="background: rgba(16, 185, 129, 0.08); border-left: 3px solid #10B981; border-radius: 6px; padding: 0.875rem 1.125rem; margin-bottom: 1rem;">
                        <div style="font-size: 0.75rem; font-weight: 700; color: #34D399; text-transform: uppercase; margin-bottom: 0.35rem;">
                            ★ Exemplar High-Scoring Response (STAR Framework):
                        </div>
                        <div style="font-size: 0.9375rem; line-height: 1.65; color: #E2E8F0;">
                            {ideal_ans}
                        </div>
                    </div>

                    <div style="font-size: 0.8125rem; color: #38BDF8; font-weight: 600;">
                        🔑 Key Takeaway Rule: <span style="color: #CBD5E1; font-weight: 400;">{takeaway}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Recommended Study Topics
        if study_topics:
            st.markdown("### 📚 Topics & Frameworks to Review Before Your Real Interview")
            cols = st.columns(2)
            for idx, topic in enumerate(study_topics):
                with cols[idx % 2]:
                    st.markdown(
                        f"""
                        <div style="background: #0E1626; border: 1px solid #1E293B; border-radius: 10px; padding: 0.875rem 1rem; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 10px;">
                            <span style="color: #38BDF8; font-weight: 700;">#{idx+1}</span>
                            <span style="font-size: 0.875rem; color: #F8FAFC; font-weight: 600;">{topic}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        # Communication Coaching
        if comm_coaching:
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            st.markdown("### 🎙️ Delivery & Communication Coaching")
            c_p, c_st, c_ex = st.columns(3)
            with c_p:
                st.markdown(
                    f"""
                    <div style="background: #0E1626; border: 1px solid #1E293B; border-radius: 10px; padding: 1rem; height: 100%;">
                        <div style="font-weight: 700; font-size: 0.875rem; color: #38BDF8; margin-bottom: 0.35rem;">Pacing & Conciseness</div>
                        <div style="font-size: 0.8125rem; color: #CBD5E1; line-height: 1.5;">{comm_coaching.get('pacing_and_conciseness', '')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c_st:
                st.markdown(
                    f"""
                    <div style="background: #0E1626; border: 1px solid #1E293B; border-radius: 10px; padding: 1rem; height: 100%;">
                        <div style="font-weight: 700; font-size: 0.875rem; color: #38BDF8; margin-bottom: 0.35rem;">STAR Framework Adherence</div>
                        <div style="font-size: 0.8125rem; color: #CBD5E1; line-height: 1.5;">{comm_coaching.get('star_framework_usage', '')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c_ex:
                st.markdown(
                    f"""
                    <div style="background: #0E1626; border: 1px solid #1E293B; border-radius: 10px; padding: 1rem; height: 100%;">
                        <div style="font-weight: 700; font-size: 0.875rem; color: #38BDF8; margin-bottom: 0.35rem;">Executive Presence</div>
                        <div style="font-size: 0.8125rem; color: #CBD5E1; line-height: 1.5;">{comm_coaching.get('executive_presence', '')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tab_questions:
        st.markdown("### 📝 Detailed Question Breakdown")
        st.caption("Review how you answered each question along with specific interviewer feedback.")

        if question_breakdown:
            for idx, q_data in enumerate(question_breakdown, 1):
                q_text = q_data.get("question", f"Question {idx}")
                ans_summary = q_data.get("answer_summary", "Candidate answered.")
                q_score = q_data.get("score", 7)
                feedback = q_data.get("feedback", "No feedback provided.")

                with st.expander(f"Question {idx:02d}: {q_text[:70]}... · Score: {q_score}/10", expanded=(idx == 1)):
                    st.markdown(f"**Interviewer Question:**\n{q_text}")
                    st.markdown(f"**Candidate Response Summary:**\n*{ans_summary}*")
                    st.markdown(f"**Score for this question:** `{q_score} / 10`")
                    st.markdown(f"**Specific Suggestion & Feedback:**\n{feedback}")
        else:
            st.info("No individual question breakdown available.")

    with tab_strengths:
        st.markdown("### ✅ Confirmed Strengths")
        st.caption("Areas where you met or exceeded the hiring bar:")
        if strengths:
            for s in strengths:
                st.markdown(
                    f"""
                    <div style="background: #0E1626; border-left: 4px solid #10B981; border-radius: 8px; padding: 0.875rem 1.15rem; margin-bottom: 0.75rem; font-size: 0.9375rem; color: #F1F5F9; line-height: 1.55;">
                        {s}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.write("No specific strengths captured.")

    with tab_export:
        st.markdown("### 📄 Full Interview Session Transcript & Export")
        
        full_session_json = json.dumps(
            {
                "role": role,
                "resume": resume,
                "overall_score": overall_score,
                "grade": grade,
                "hiring_recommendation": rec_label,
                "category_scores": category_scores,
                "overall_summary": overall_summary,
                "strengths": strengths,
                "actionable_suggestions": actionable_suggestions,
                "model_answer_transformation": model_transformation,
                "study_topics": study_topics,
                "communication_coaching": comm_coaching,
                "question_breakdown": question_breakdown,
                "conversation_history": history,
            },
            indent=2,
            ensure_ascii=False,
        )
        safe_name = "".join(c for c in role if c.isalnum() or c in ("-", "_")).lower()

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button(
                label="📥 Download Full Report (JSON)",
                data=full_session_json,
                file_name=f"apex_interview_evaluation_{safe_name}.json",
                mime="application/json",
                use_container_width=True,
            )

        with col_d2:
            # Markdown export summary
            md_summary = f"""# APEX INTERVIEW REPORT: {role}
**Overall Score:** {overall_score}/100 (Grade {grade})
**Recommendation:** {rec_label}

## Executive Summary
{overall_summary}

## Rubric Breakdown
- Technical Depth: {category_scores.get('technical_depth', overall_score)}/100
- Problem Solving: {category_scores.get('problem_solving', overall_score)}/100
- Communication: {category_scores.get('communication_clarity', overall_score)}/100
- Role Alignment: {category_scores.get('role_alignment', overall_score)}/100

## Priority Suggestions to Improve
"""
            for it in actionable_suggestions:
                md_summary += f"\n### {it.get('title')}\n- **Priority:** {it.get('priority')}\n- **Advice:** {it.get('advice')}\n- **Action Drill:** {it.get('action_item')}\n"

            st.download_button(
                label="📥 Download Summary (Markdown)",
                data=md_summary,
                file_name=f"apex_interview_summary_{safe_name}.md",
                mime="text/markdown",
                use_container_width=True,
            )

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        st.markdown("**Transcript:**")
        with st.container():
            for m in history:
                speaker = "Interviewer" if m.get("role") in ("assistant", "model") else "Candidate"
                st.markdown(f"**{speaker}:** {m.get('content')}")

    st.markdown("<hr style='border: none; border-top: 1px solid #1E293B; margin: 2rem 0 1.5rem 0;'>", unsafe_allow_html=True)

    # 5. Bottom Navigation Controls
    col_retake, col_new = st.columns([1, 1], gap="medium")
    with col_retake:
        if st.button("🔄 Retake Interview for Same Role", use_container_width=True):
            st.session_state.conversation_history = []
            st.session_state.generated_questions = []
            st.session_state.question_number = 1
            st.session_state.evaluation_report = None
            st.session_state.evaluation_error = None
            st.session_state.last_error = None
            st.session_state.generating_questions = False
            st.session_state.last_voice_ts = None
            st.session_state.screen = "chat"
            st.rerun()

    with col_new:
        if st.button("🚀 Start New Interview Session", type="primary", use_container_width=True):
            st.session_state.evaluation_error = None
            reset_interview()
            st.rerun()
