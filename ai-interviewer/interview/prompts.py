"""Prompt templates and helper functions for question generation and candidate evaluation."""

QUESTION_SYSTEM_PROMPT_TEMPLATE = (
    "You are an experienced technical interviewer conducting a structured interview for the role of {role}. "
    "Ask one question at a time. Base questions on the role and the candidate's resume if provided. "
    "After the candidate answers, decide whether to ask a natural follow-up to probe a vague or interesting answer, "
    "or move to a new topic — don't always follow up. Keep a professional, encouraging tone. "
    "Never reveal scores or hints during the interview. Never answer the question yourself. "
    "Cover a mix of background, technical knowledge, problem-solving, and one behavioral question across the interview. "
    "This is question {question_number} of {total_questions}. Resume: {resume_text}. "
    "Conversation so far: {conversation_history}. "
    "Respond with ONLY the next question or follow-up to say to the candidate — no labels, no preamble."
)

EVALUATION_SYSTEM_PROMPT = """You are an expert hiring manager and senior technical interviewer.
Evaluate the candidate's interview performance based on the full transcript provided.
Analyze their depth of knowledge, communication clarity, relevance of examples, problem-solving acumen, and demeanor.
Provide your evaluation strictly as a valid, well-formed JSON object conforming to the required schema.
Do NOT include any extra text, commentary, or markdown outside of the JSON."""

EVALUATION_PROMPT_TEMPLATE = """Evaluate this completed interview for the role of {role}.

Candidate Resume (if provided):
{resume_text}

Full Interview Transcript:
{transcript}

You must return a strictly valid JSON object matching this exact schema:
{{
  "overall_score": <int 0-100>,
  "overall_summary": "<string 2-3 sentences providing an executive summary of performance>",
  "strengths": [
    "<string key strength 1>",
    "<string key strength 2>",
    "<string key strength 3>"
  ],
  "areas_to_improve": [
    "<string key improvement area 1>",
    "<string key improvement area 2>",
    "<string key improvement area 3>"
  ],
  "question_breakdown": [
    {{
      "question": "<string verbatim or concise interview question>",
      "answer_summary": "<string 1-line summary of how candidate answered>",
      "score": <int 0-10>,
      "feedback": "<string specific, constructive feedback on this answer>"
    }}
  ]
}}

Return ONLY the raw JSON object. Do not wrap in backticks or markdown fences if possible, or use standard ```json ... ``` formatting."""


def build_question_prompt(
    role: str,
    resume_text: str,
    question_number: int,
    total_questions: int,
    conversation_history: str,
) -> str:
    """Build the prompt for generating the next interview question or follow-up."""
    clean_resume = resume_text.strip() if resume_text else "None provided."
    clean_history = conversation_history.strip() if conversation_history else "No conversation yet. Please start with an opening question about the candidate's background."
    
    return QUESTION_SYSTEM_PROMPT_TEMPLATE.format(
        role=role.strip(),
        resume_text=clean_resume,
        question_number=question_number,
        total_questions=total_questions,
        conversation_history=clean_history,
    )


def build_evaluation_prompt(
    role: str,
    resume_text: str,
    transcript: str,
) -> str:
    """Build the evaluation prompt with the interview transcript."""
    clean_resume = resume_text.strip() if resume_text else "None provided."
    return EVALUATION_PROMPT_TEMPLATE.format(
        role=role.strip(),
        resume_text=clean_resume,
        transcript=transcript.strip(),
    )
