"""Setup screen tailored for Freshers, College Graduates, and Entry-to-Mid level developers."""

import streamlit as st
from interview.flow import start_interview
from interview.llm import get_api_key
from interview.resume_parser import extract_text_from_pdf
from ui.theme import render_header
from ui.assets import get_hero_room_uri

ROLE_PRESETS = [
    "Entry-Level Software Engineer (Fresher)",
    "Junior Full-Stack Developer (React & Node.js)",
    "Junior Backend Engineer (Python / Java / SQL)",
    "Junior Data Analyst & Python Developer",
    "Graduate Cloud & DevOps Engineer",
    "Junior QA / Automation Engineer",
]

SAMPLE_RESUMES = {
    "Entry-Level Software Engineer (Fresher)": (
        "B.S. in Computer Science (2024 Graduate). GPA: 3.8/4.0.\n"
        "Coursework: Data Structures & Algorithms, Database Management Systems (DBMS), Operating Systems, Computer Networks.\n"
        "Skills: Python, Java, C++, SQL, Git, Linux.\n"
        "Capstone Project: Built an online bookstore web application using React and Flask with PostgreSQL. "
        "Implemented user authentication with JWT, RESTful API endpoints, and optimized SQL queries for catalog search. "
        "Solved 200+ LeetCode problems covering arrays, strings, hash maps, and binary trees."
    ),
    "Junior Full-Stack Developer (React & Node.js)": (
        "Junior Web Developer with 1 year of project experience in modern JavaScript/TypeScript, React, and Node.js/Express.\n"
        "Projects: Created a collaborative task-tracking board (similar to Trello) featuring drag-and-drop, WebSocket real-time updates, and MongoDB storage.\n"
        "Internship: 6-month software development intern at a startup. Built responsive UI components, integrated Stripe checkout API, and fixed 40+ frontend bugs.\n"
        "Key Skills: HTML5, CSS3/Tailwind, JavaScript (ES6+), React, Node.js, Express, MongoDB, Git."
    ),
    "Junior Backend Engineer (Python / Java / SQL)": (
        "Recent Computer Science Graduate with strong passion for backend systems and database design.\n"
        "Skills: Python (FastAPI/Django), Java (Spring Boot basics), PostgreSQL, MySQL, Docker, Postman.\n"
        "Projects: Built a micro-URL shortening service in FastAPI with Redis caching and PostgreSQL persistence. "
        "Analyzed database indexing and achieved sub-15ms response times. Wrote unit tests using PyTest achieving 85% code coverage.\n"
        "Familiar with OOP design principles, REST architectural patterns, and basic Docker containerization."
    ),
    "Junior Data Analyst & Python Developer": (
        "B.S. in Information Systems / Data Science. Proficient in Python, SQL, Pandas, NumPy, and Tableau.\n"
        "Projects: Conducted customer churn analysis on a telecom dataset (50,000+ records) using Pandas and Scikit-learn. "
        "Built interactive Tableau dashboard tracking monthly KPIs and conversion rates.\n"
        "Strong understanding of relational database normalization, SQL aggregate queries (GROUP BY, HAVING, WINDOW functions), and data visualization."
    ),
    "Graduate Cloud & DevOps Engineer": (
        "Recent Engineering graduate with AWS Certified Cloud Practitioner.\n"
        "Skills: Linux/Bash scripting, Docker, Git, AWS (EC2, S3, RDS, IAM), CI/CD fundamentals with GitHub Actions.\n"
        "Projects: Containerized a multi-tier web application using Docker Compose and deployed it to AWS EC2 behind an NGINX reverse proxy. "
        "Automated deployment pipeline with GitHub Actions to run automated linting and tests on pull requests."
    ),
    "Junior QA / Automation Engineer": (
        "Entry-level Software Quality Engineer with knowledge of manual testing methodologies and test automation.\n"
        "Skills: Python, Selenium WebDriver, Postman for API testing, JIRA, SQL for test data verification.\n"
        "Projects: Designed automated regression test suite using Selenium in Python covering 30+ end-to-end user workflows. "
        "Created comprehensive bug reports with reproduction steps and logs."
    )
}


def render_setup_screen() -> None:
    # 1. Top Header with Step indicator
    render_header(current_screen="setup")

    # 2. Hero Section with Generated Studio Visual
    hero_uri = get_hero_room_uri()
    if hero_uri:
        st.markdown(
            f"""
            <div style="
                position: relative;
                border-radius: 16px;
                overflow: hidden;
                margin-bottom: 2rem;
                border: 1px solid #1E293B;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.45);
                height: 220px;
                background: url('{hero_uri}') center center / cover no-repeat;
            ">
                <div style="
                    position: absolute;
                    inset: 0;
                    background: linear-gradient(180deg, rgba(7, 11, 20, 0.35) 0%, rgba(7, 11, 20, 0.94) 85%);
                    display: flex;
                    flex-direction: column;
                    justify-content: flex-end;
                    padding: 1.75rem 2.25rem;
                ">
                    <div style="font-size: 0.8125rem; font-weight: 700; color: #38BDF8; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.35rem;">
                        Fresher & Junior Tech Interview Practice Studio
                    </div>
                    <h1 style="font-size: 1.85rem; font-weight: 800; color: #FFFFFF; margin: 0 0 0.5rem 0; line-height: 1.2;">
                        Ace Your Campus Placements & Entry-Level Interviews
                    </h1>
                    <div style="font-size: 0.875rem; color: #94A3B8; display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
                        <span>CS Fundamentals & OOP</span>
                        <span aria-hidden="true" style="color: #475569;">·</span>
                        <span>Data Structures (DSA)</span>
                        <span aria-hidden="true" style="color: #475569;">·</span>
                        <span>College Project Deep-Dives</span>
                        <span aria-hidden="true" style="color: #475569;">·</span>
                        <span style="color: #38BDF8; font-weight: 600;">Calibrated Fresher Scoring & Improvement Tips</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    api_key = get_api_key()
    if not api_key:
        st.warning(
            "⚠️ **No GEMINI_API_KEY detected.** Please add your `GEMINI_API_KEY` to `.env` or system environment variables "
            "to power dynamic questions and scoring."
        )

    if "role_input_widget" not in st.session_state:
        st.session_state.role_input_widget = (
            st.session_state.get("role_input_val")
            or st.session_state.get("role")
            or "Entry-Level Software Engineer (Fresher)"
        )
    if "resume_input_widget" not in st.session_state:
        st.session_state.resume_input_widget = st.session_state.get(
            "resume_input_val", st.session_state.get("resume", "")
        )

    # 3. Two-Column Workspace Layout
    col_main, col_sidebar = st.columns([1.8, 1.2], gap="large")

    with col_main:
        st.markdown("### 🎓 Target Role & Track")

        # Quick preset buttons for freshers
        st.markdown("<div style='font-size: 0.8125rem; color: #94A3B8; margin-bottom: 6px;'>Quick Select Entry-Level Tracks:</div>", unsafe_allow_html=True)
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            if st.button("🚀 Fresher SDE", use_container_width=True):
                st.session_state.role_input_val = ROLE_PRESETS[0]
                st.session_state.role_input_widget = ROLE_PRESETS[0]
                st.session_state.resume_input_val = SAMPLE_RESUMES[ROLE_PRESETS[0]]
                st.session_state.resume_input_widget = SAMPLE_RESUMES[ROLE_PRESETS[0]]
                st.session_state.uploaded_pdf_meta = None
                st.session_state.pdf_parse_error = None
                st.rerun()
        with col_p2:
            if st.button("💻 Junior Full-Stack", use_container_width=True):
                st.session_state.role_input_val = ROLE_PRESETS[1]
                st.session_state.role_input_widget = ROLE_PRESETS[1]
                st.session_state.resume_input_val = SAMPLE_RESUMES[ROLE_PRESETS[1]]
                st.session_state.resume_input_widget = SAMPLE_RESUMES[ROLE_PRESETS[1]]
                st.session_state.uploaded_pdf_meta = None
                st.session_state.pdf_parse_error = None
                st.rerun()
        with col_p3:
            if st.button("⚙️ Junior Backend", use_container_width=True):
                st.session_state.role_input_val = ROLE_PRESETS[2]
                st.session_state.role_input_widget = ROLE_PRESETS[2]
                st.session_state.resume_input_val = SAMPLE_RESUMES[ROLE_PRESETS[2]]
                st.session_state.resume_input_widget = SAMPLE_RESUMES[ROLE_PRESETS[2]]
                st.session_state.uploaded_pdf_meta = None
                st.session_state.pdf_parse_error = None
                st.rerun()

        role_input = st.text_input(
            "Target Position / Internship Title *",
            key="role_input_widget",
            placeholder="e.g. Graduate Software Engineer, Junior Web Developer, Associate Python Dev...",
            help="Questions will be strictly calibrated to entry-level fundamentals for this role.",
        )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.markdown("### 📄 Candidate Background, Degree & Projects")

        uploaded_pdf = st.file_uploader(
            "📎 Upload Resume PDF (Optional)",
            type=["pdf"],
            key="resume_pdf_uploader",
            help="Upload your resume PDF so interview questions are tailored directly to your skills, projects, and experience.",
        )

        if uploaded_pdf is not None:
            pdf_sig = (uploaded_pdf.name, uploaded_pdf.size)
            if st.session_state.get("uploaded_pdf_sig") != pdf_sig:
                try:
                    extracted_text, page_count = extract_text_from_pdf(uploaded_pdf.getvalue())
                    st.session_state.uploaded_pdf_sig = pdf_sig
                    st.session_state.uploaded_pdf_extracted = extracted_text
                    st.session_state.uploaded_pdf_meta = {
                        "name": uploaded_pdf.name,
                        "pages": page_count,
                        "chars": len(extracted_text),
                    }
                    st.session_state.pdf_parse_error = None
                    st.session_state.resume_input_val = extracted_text
                    st.session_state.resume_input_widget = extracted_text
                except ValueError as e:
                    st.session_state.uploaded_pdf_sig = pdf_sig
                    st.session_state.uploaded_pdf_meta = None
                    st.session_state.pdf_parse_error = str(e)
        elif st.session_state.get("uploaded_pdf_sig") is not None:
            # User clicked remove (×) on the uploaded PDF
            prev_extracted = st.session_state.get("uploaded_pdf_extracted", "")
            st.session_state.uploaded_pdf_sig = None
            st.session_state.uploaded_pdf_meta = None
            st.session_state.uploaded_pdf_extracted = None
            st.session_state.pdf_parse_error = None
            if st.session_state.get("resume_input_widget") == prev_extracted:
                st.session_state.resume_input_widget = ""
                st.session_state.resume_input_val = ""

        if st.session_state.get("pdf_parse_error"):
            st.warning(f"⚠️ {st.session_state.pdf_parse_error}")
        elif st.session_state.get("uploaded_pdf_meta"):
            meta = st.session_state.uploaded_pdf_meta
            st.caption(
                f"📄 Extracted from **{meta['name']}** ({meta['pages']} page(s), {meta['chars']:,} chars) · "
                "Review or edit the extracted resume text below."
            )

        resume_input = st.text_area(
            "College Projects, Degree, Tech Stack, or Resume (Optional)",
            key="resume_input_widget",
            height=130,
            placeholder="Upload a PDF resume above, or paste your degree/college, coursework, favorite tech stack (Python, Java, React, SQL), or capstone project details here...\n\nThe interviewer will ask you to explain your projects and code choices.",
            help="Optional: Upload your PDF resume or share your projects/courses so the interviewer can ask tailored questions.",
        )
        if resume_input:
            st.caption(f"✓ {len(resume_input):,} characters loaded · Interviewer will tailor questions to your resume and projects.")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.markdown("### ⏱️ Experience Level & Session Length")
        col_diff, col_q = st.columns(2)
        with col_diff:
            experience_level = st.selectbox(
                "Experience Level (Calibrated for Freshers)",
                options=[
                    "Fresher / College Graduate (0 yrs)",
                    "Entry-Level Engineer (0-1 yrs)",
                    "Junior Developer (1-2 yrs)",
                    "Mid-Level Engineer (2-3 yrs)",
                ],
                index=0,
                help="Calibrates questions strictly to entry and mid-level concepts (DSA basics, OOP, college projects, debugging).",
            )
        with col_q:
            question_count = st.selectbox(
                "Interview Length",
                options=[3, 5, 7],
                index=1,
                format_func=lambda x: f"{x} Questions (Quick Mock Drill)" if x == 3 else (f"{x} Questions (Standard Placement Round)" if x == 5 else f"{x} Questions (Comprehensive Drill)"),
                help="Choose how many questions to practice before receiving your calibrated score and suggestions to improve.",
            )

        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
        start_btn = st.button("🚀 Start Fresher Interview Simulation", type="primary", use_container_width=True)

        if start_btn:
            clean_role = role_input.strip()
            if not clean_role:
                st.error("Please enter a target role or internship title before proceeding.")
                return

            full_role_title = f"{experience_level} - {clean_role}" if not any(clean_role.lower().startswith(p) for p in ["fresher", "entry", "junior", "graduate", "intern", "associate", "mid"]) else clean_role

            start_interview(
                role=full_role_title,
                resume=resume_input,
                enable_voice=st.session_state.get("enable_voice", True),
                enable_voice_input=st.session_state.get("enable_voice_input", True),
                total_questions=question_count,
            )
            st.rerun()

    with col_sidebar:
        st.markdown("### 🎙️ Audio & Voice Controls")
        st.markdown(
            """
            <div style="background: #0E1626; border: 1px solid #1E293B; border-radius: 12px; padding: 1.25rem; margin-bottom: 1.5rem;">
                <div style="font-size: 0.8125rem; color: #94A3B8; line-height: 1.5; margin-bottom: 1rem;">
                    Practice speaking your answers aloud with browser microphone recognition and realistic interviewer audio.
                </div>
            """,
            unsafe_allow_html=True,
        )
        voice_out = st.toggle(
            "🔊 Read Questions Aloud (TTS)",
            value=st.session_state.get("enable_voice", True),
            help="AI Interviewer speaks questions aloud using natural voice audio.",
        )
        auto_play = st.toggle(
            "▶️ Auto-play Audio",
            value=st.session_state.get("auto_play_voice", True),
            disabled=not voice_out,
            help="Automatically plays audio when new questions arrive.",
        )
        voice_in = st.toggle(
            "🎙️ Speech-to-Text Microphone Input",
            value=st.session_state.get("enable_voice_input", True),
            help="Speak your responses directly using your browser microphone.",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.session_state.enable_voice = voice_out
        st.session_state.auto_play_voice = auto_play
        st.session_state.enable_voice_input = voice_in

        # Fresher Interview Guide Card
        st.markdown(
            """
            <div style="background: #0A111F; border: 1px solid #1E293B; border-radius: 12px; padding: 1.25rem;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #38BDF8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                    Fresher Interview Focus Areas
                </div>
                <div style="font-weight: 700; font-size: 0.95rem; color: #F8FAFC; margin-bottom: 0.5rem;">
                    What the Interviewer Looks For:
                </div>
                <ul style="font-size: 0.8125rem; color: #94A3B8; padding-left: 1.2rem; margin: 0; line-height: 1.6;">
                    <li><strong>CS Fundamentals:</strong> OOP concepts, memory, basic algorithms</li>
                    <li><strong>Problem Solving:</strong> Explaining your thought process step-by-step</li>
                    <li><strong>Project Ownership:</strong> Clearly describing what YOU personally built</li>
                    <li><strong>Coachability & Eagerness:</strong> Honest communication when learning new concepts</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
