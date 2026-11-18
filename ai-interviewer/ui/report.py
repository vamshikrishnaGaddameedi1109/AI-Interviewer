"""Report screen: displays scored evaluation, category rubrics, strengths, and per-question breakdown."""

import json
import streamlit as st
from interview.evaluator import evaluate_interview
from interview.flow import reset_interview, save_session_to_json
from ui.theme import render_top_bar


def render_report_screen() -> None:
    role = st.session_state.get("role", "Technical Role")
    resume = st.session_state.get("resume", "")
    history = st.session_state.get("conversation_history", [])

    # 1. Top Bar Contract
    render_top_bar(
        brand_title="APEX INTERVIEWER",
        stage_label="Evaluation Report · Rubric Scored · Session Complete",
    )

    # Guard: if no conversation history exists
    if not history:
        st.warning("No interview conversation found to evaluate.")
        if st.button("⬅️ Return to Setup"):
            reset_interview()
            st.rerun()
        return

    # Call evaluator on first load
    if st.session_state.get("evaluation_report") is None:
        with st.spinner("Senior hiring manager is evaluating your complete interview transcript..."):
            try:
                report_data = evaluate_interview(
                    role=role,
                    resume_text=resume,
                    conversation_history=history,
                )
                st.session_state.evaluation_report = report_data

                saved_path = save_session_to_json(
                    role=role,
                    resume=resume,
                    conversation_history=history,
                    evaluation_report=report_data,
                )
                st.session_state.saved_session_file = saved_path
            except Exception as e:
                st.error(f"⚠️ Evaluation Error: {str(e)}")
                col_retry, col_reset = st.columns(2)
                with col_retry:
                    if st.button("🔄 Retry Evaluation", type="primary", use_container_width=True):
                        st.session_state.evaluation_report = None
                        st.rerun()
                with col_reset:
                    if st.button("⬅️ Start New Session", use_container_width=True):
                        reset_interview()
                        st.rerun()
                return

    report = st.session_state.evaluation_report

    overall_score = int(report.get("overall_score", 0))
    overall_summary = report.get("overall_summary", "")
    category_scores = report.get("category_scores", {})
    strengths = report.get("strengths", [])
    areas_to_improve = report.get("areas_to_improve", [])
    question_breakdown = report.get("question_breakdown", [])

    # Recommendation status logic
    if overall_score >= 80:
        rec_label = "● STRONG HIRE RECOMMENDATION"
        rec_color = "#10B981"
        rec_bg = "rgba(16, 185, 129, 0.1)"
        rec_border = "rgba(16, 185, 129, 0.3)"
    elif overall_score >= 65:
        rec_label = "● QUALIFIED / HIRE WITH RESERVATION"
        rec_color = "#38BDF8"
        rec_bg = "rgba(56, 189, 248, 0.1)"
        rec_border = "rgba(56, 189, 248, 0.3)"
    else:
        rec_label = "▲ NEEDS FOCUSED PREPARATION"
        rec_color = "#F59E0B"
        rec_bg = "rgba(245, 158, 11, 0.1)"
        rec_border = "rgba(245, 158, 11, 0.3)"

    # 2. Executive Scorecard Hero Card
    st.markdown(
        f"""
        <div style="background: #111827; border: 1px solid #1E293B; border-radius: 14px; padding: 1.75rem 2rem; margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; gap: 1.5rem;">
                <div style="flex: 1; min-width: 280px;">
                    <div style="font-size: 0.8125rem; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.35rem;">
                        Target Position: {role}
                    </div>
                    <div style="display: inline-block; padding: 4px 10px; border-radius: 6px; background: {rec_bg}; border: 1px solid {rec_border}; color: {rec_color}; font-size: 0.8125rem; font-weight: 700; letter-spacing: 0.03em; margin-bottom: 1rem;">
                        {rec_label}
                    </div>
                    <p style="font-size: 0.9375rem; line-height: 1.6; color: #E2E8F0; margin: 0;">
                        {overall_summary}
                    </p>
                </div>
                <div style="text-align: right; min-width: 140px; border-left: 1px solid #1E293B; padding-left: 2rem;">
                    <div style="font-size: 0.75rem; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em;">
                        Overall Score
                    </div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 2.75rem; font-weight: 700; color: #F8FAFC; line-height: 1.1; margin: 0.25rem 0;">
                        {overall_score}<span style="font-size: 1.25rem; color: #64748B;">/100</span>
                    </div>
                    <div style="font-size: 0.75rem; color: #64748B;">
                        Calibrated Benchmark
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Four-Metric Rubric Breakdown
    st.markdown("### Evaluation Rubric Breakdown")
    c1, c2, c3, c4 = st.columns(4)

    metrics = [
        ("Technical Depth", category_scores.get("technical_depth", overall_score), "Core knowledge & architecture"),
        ("Problem Solving", category_scores.get("problem_solving", overall_score), "Approach, scaling, tradeoffs"),
        ("Communication", category_scores.get("communication_clarity", overall_score), "Clarity, conciseness, structure"),
        ("Role Alignment", category_scores.get("role_alignment", overall_score), "Experience & situational fit"),
    ]

    for col, (label, val, desc) in zip([c1, c2, c3, c4], metrics):
        with col:
            val_int = int(val)
            pct = min(max(val_int / 100.0, 0.0), 1.0)
            st.markdown(
                f"""
                <div style="background: #111827; border: 1px solid #1E293B; border-radius: 10px; padding: 1rem 1.125rem;">
                    <div style="font-size: 0.8125rem; font-weight: 600; color: #CBD5E1; margin-bottom: 0.25rem;">
                        {label}
                    </div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.5rem; font-weight: 700; color: #38BDF8;">
                        {val_int}<span style="font-size: 0.875rem; color: #64748B;"> / 100</span>
                    </div>
                    <div style="font-size: 0.6875rem; color: #64748B; margin-top: 0.25rem;">
                        {desc}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(pct)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 4. Two-Column Strengths vs Improvements
    col_str, col_imp = st.columns(2, gap="large")

    with col_str:
        st.markdown("### ✅ Key Strengths")
        if strengths:
            for s in strengths:
                st.markdown(
                    f"""
                    <div style="background: #111827; border-left: 3px solid #10B981; border-radius: 6px; padding: 0.75rem 1rem; margin-bottom: 0.625rem; font-size: 0.875rem; color: #F1F5F9; line-height: 1.5;">
                        {s}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.write("No specific strengths captured.")

    with col_imp:
        st.markdown("### 🎯 Priority Improvement Areas")
        if areas_to_improve:
            for item in areas_to_improve:
                st.markdown(
                    f"""
                    <div style="background: #111827; border-left: 3px solid #F59E0B; border-radius: 6px; padding: 0.75rem 1rem; margin-bottom: 0.625rem; font-size: 0.875rem; color: #F1F5F9; line-height: 1.5;">
                        {item}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.write("No specific improvement areas captured.")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 5. Question-by-Question Detailed Review
    st.markdown("### 📝 Per-Question Review & Feedback")
    if question_breakdown:
        for idx, q_data in enumerate(question_breakdown, 1):
            q_text = q_data.get("question", f"Question {idx}")
            ans_summary = q_data.get("answer_summary", "Candidate answered.")
            q_score = q_data.get("score", 7)
            feedback = q_data.get("feedback", "No feedback provided.")

            with st.expander(f"Question {idx:02d}: {q_text[:70]}... · Score: {q_score}/10", expanded=(idx == 1)):
                st.markdown(f"**Interviewer Question:**\n{q_text}")
                st.markdown(f"**Candidate Response Summary:**\n*{ans_summary}*")
                st.markdown(f"**Question Score:** `{q_score} / 10`")
                st.markdown(f"**Specific Evaluation & Feedback:**\n{feedback}")
    else:
        st.info("No detailed breakdown available for this session.")

    st.markdown("<hr style='border: none; border-top: 1px solid #1E293B; margin: 1.5rem 0 1rem 0;'>", unsafe_allow_html=True)

    # 6. Action Controls: Download Report, Start New
    col_dl, col_new = st.columns([1, 1], gap="medium")

    with col_dl:
        full_session_json = json.dumps(
            {
                "role": role,
                "resume": resume,
                "overall_score": overall_score,
                "category_scores": category_scores,
                "overall_summary": overall_summary,
                "strengths": strengths,
                "areas_to_improve": areas_to_improve,
                "question_breakdown": question_breakdown,
                "conversation_history": history,
            },
            indent=2,
            ensure_ascii=False,
        )
        safe_name = "".join(c for c in role if c.isalnum() or c in ("-", "_")).lower()
        st.download_button(
            label="📥 Download Complete Report (JSON)",
            data=full_session_json,
            file_name=f"apex_interview_report_{safe_name}.json",
            mime="application/json",
            use_container_width=True,
        )

    with col_new:
        if st.button("🔄 Start Another Practice Interview", type="primary", use_container_width=True):
            reset_interview()
            st.rerun()
