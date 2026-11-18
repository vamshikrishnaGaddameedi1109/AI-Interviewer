"""Compact, high-signal prompt templates and JSON parsers for fresher/entry-to-mid interviews."""

import json
import re
from typing import List, Optional

MAX_QUESTIONS_PER_REQUEST: int = 5
MAX_RESUME_CHARS: int = 1200
MAX_TRANSCRIPT_CHARS: int = 4500

BATCH_QUESTIONS_SYSTEM_PROMPT = (
    "You are an encouraging technical interviewer for entry-to-mid level (fresher/junior, 0-3 yrs) candidates. "
    "Return ONLY valid JSON: {\"questions\": [\"...\", ...]}. "
    "Cover core programming/OOP, basic DSA & Big-O, candidate projects, REST/SQL basics, and 1 behavioral question. "
    "No senior/staff architecture questions. Keep each question concise (1-2 sentences)."
)

BATCH_QUESTIONS_USER_TEMPLATE = (
    "Generate exactly {count} interview questions (maximum 5) for role: {role}.\n"
    "Candidate background: {resume_text}\n"
    "{existing_context}"
    "Return strictly JSON: {{\"questions\": [\"q1\", ...]}}"
)

EVALUATION_SYSTEM_PROMPT = (
    "You are an engineering mentor evaluating a fresher/entry-to-mid technical interview. "
    "Return ONLY strictly valid JSON matching the requested schema. Keep all fields concise (1-2 sentences max)."
)

EVALUATION_PROMPT_TEMPLATE = """Evaluate this entry-to-mid interview for: {role}.
Background: {resume_text}

Transcript:
{transcript}

Return ONLY valid JSON with this exact schema:
{{
  "overall_score": <int 0-100>,
  "hiring_recommendation": "<Strong Hire | Hire | Leaning Hire | Needs Preparation>",
  "category_scores": {{
    "technical_depth": <int 0-100>,
    "problem_solving": <int 0-100>,
    "communication_clarity": <int 0-100>,
    "role_alignment": <int 0-100>
  }},
  "overall_summary": "<2 concise sentences>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "actionable_suggestions": [
    {{
      "priority": "<High | Medium>",
      "category": "<Core Fundamentals | Problem Solving & DSA | Project Articulation | Communication & STAR>",
      "title": "<Short title>",
      "advice": "<1-2 crisp sentences>",
      "action_item": "<1 concrete drill>"
    }},
    {{
      "priority": "<High | Medium>",
      "category": "<Core Fundamentals | Problem Solving & DSA | Project Articulation | Communication & STAR>",
      "title": "<Short title 2>",
      "advice": "<1-2 crisp sentences>",
      "action_item": "<1 concrete drill>"
    }},
    {{
      "priority": "<High | Medium>",
      "category": "<Core Fundamentals | Problem Solving & DSA | Project Articulation | Communication & STAR>",
      "title": "<Short title 3>",
      "advice": "<1-2 crisp sentences>",
      "action_item": "<1 concrete drill>"
    }}
  ],
  "model_answer_transformation": {{
    "question": "<Weakest question>",
    "candidate_flaw": "<1 sentence gap>",
    "ideal_model_answer": "<2-3 sentence model fresher answer>",
    "key_takeaway": "<1 golden rule>"
  }},
  "study_topics": ["<topic 1>", "<topic 2>", "<topic 3>", "<topic 4>"],
  "communication_coaching": {{
    "pacing_and_conciseness": "<1 sentence>",
    "star_framework_usage": "<1 sentence>",
    "executive_presence": "<1 sentence>"
  }},
  "question_breakdown": [
    {{
      "question": "<concise question>",
      "answer_summary": "<1 sentence summary>",
      "score": <int 0-10>,
      "feedback": "<1-2 sentences feedback>"
    }}
  ]
}}"""


def _truncate_text(text: str, max_chars: int) -> str:
    clean = " ".join((text or "").split())
    if not clean:
        return ""
    if len(clean) <= max_chars:
        return clean
    return clean[: max_chars - 3].rstrip() + "..."


def build_batch_questions_messages(
    role: str,
    resume_text: str,
    count: int = MAX_QUESTIONS_PER_REQUEST,
    existing_questions: Optional[List[str]] = None,
) -> List[dict]:
    """
    Build compact prompt messages to generate up to 5 interview questions per request.
    """
    capped_count = max(1, min(int(count), MAX_QUESTIONS_PER_REQUEST))
    compact_resume = _truncate_text(resume_text, MAX_RESUME_CHARS) or "Fresher candidate (no resume pasted)."

    if existing_questions:
        recent = existing_questions[-5:]
        compact_existing = "Already asked (do not repeat): " + " | ".join(
            _truncate_text(q, 100) for q in recent
        ) + "\n"
    else:
        compact_existing = ""

    user_prompt = BATCH_QUESTIONS_USER_TEMPLATE.format(
        count=capped_count,
        role=role.strip(),
        resume_text=compact_resume,
        existing_context=compact_existing,
    )
    return [
        {"role": "system", "content": BATCH_QUESTIONS_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def parse_questions_json(raw_text: str, max_count: int = MAX_QUESTIONS_PER_REQUEST) -> List[str]:
    """
    Robustly parse Gemini's JSON response into a validated list of up to 5 question strings.
    Raises ValueError if response cannot be parsed or contains no valid questions.
    """
    if not raw_text or not raw_text.strip():
        raise ValueError("Empty response received from Gemini while generating questions.")

    text = raw_text.strip()

    # Strip markdown code fences if present
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if fence_match:
        text = fence_match.group(1).strip()

    # Locate JSON object or array bounds if extraneous text surrounds it
    if not ((text.startswith("{") and text.endswith("}")) or (text.startswith("[") and text.endswith("]"))):
        obj_start, obj_end = text.find("{"), text.rfind("}")
        arr_start, arr_end = text.find("["), text.rfind("]")
        if obj_start != -1 and obj_end > obj_start and (arr_start == -1 or obj_start < arr_start):
            text = text[obj_start : obj_end + 1]
        elif arr_start != -1 and arr_end > arr_start:
            text = text[arr_start : arr_end + 1]

    # Remove trailing commas before closing brackets/braces
    text = re.sub(r",\s*([}\]])", r"\1", text)

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse generated interview questions JSON: {str(e)}. "
            f"Snippet: {raw_text[:200]}"
        ) from e

    if isinstance(parsed, dict):
        raw_list = parsed.get("questions")
        if raw_list is None:
            # Accept alternate common keys if returned
            for key in ("interview_questions", "items", "data"):
                if isinstance(parsed.get(key), list):
                    raw_list = parsed[key]
                    break
    elif isinstance(parsed, list):
        raw_list = parsed
    else:
        raise ValueError("Expected JSON object with 'questions' list or JSON array.")

    if not isinstance(raw_list, list):
        raise ValueError("Parsed JSON does not contain a valid 'questions' list.")

    questions: List[str] = []
    cap = max(1, min(int(max_count), MAX_QUESTIONS_PER_REQUEST))
    for item in raw_list:
        if isinstance(item, str):
            q_str = item.strip()
        elif isinstance(item, dict):
            q_str = str(item.get("question") or item.get("text") or "").strip()
        else:
            q_str = ""

        if q_str:
            questions.append(q_str)
        if len(questions) >= cap:
            break

    if not questions:
        raise ValueError("Gemini returned 0 valid interview questions in JSON response.")

    return questions


def build_evaluation_prompt(
    role: str,
    resume_text: str,
    transcript: str,
) -> str:
    """Build a compact evaluation prompt calibrated for freshers and entry-to-mid developers."""
    compact_resume = _truncate_text(resume_text, MAX_RESUME_CHARS) or "Fresher candidate."
    compact_transcript = transcript.strip()
    if len(compact_transcript) > MAX_TRANSCRIPT_CHARS:
        compact_transcript = compact_transcript[-MAX_TRANSCRIPT_CHARS:]
    return EVALUATION_PROMPT_TEMPLATE.format(
        role=role.strip(),
        resume_text=compact_resume,
        transcript=compact_transcript,
    )
