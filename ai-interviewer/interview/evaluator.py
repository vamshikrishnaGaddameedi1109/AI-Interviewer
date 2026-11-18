"""Evaluation module: builds evaluation prompt, invokes LLM with temperature 0.2, and parses JSON output."""

import json
import re
from typing import Dict, Any, List
from interview.llm import call_llm
from interview.prompts import build_evaluation_prompt, EVALUATION_SYSTEM_PROMPT
from interview.flow import format_conversation_for_prompt


def clean_and_parse_json(raw_text: str) -> Dict[str, Any]:
    """
    Strip any markdown code fences and extraneous text before parsing JSON.
    Throws ValueError with clear message if parsing fails.
    """
    text = raw_text.strip()

    # Strip markdown code blocks like ```json ... ``` or ``` ... ```
    pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(pattern, text)
    if match:
        text = match.group(1).strip()

    # If there's still preamble or postamble, locate outermost curly braces
    if not (text.startswith("{") and text.endswith("}")):
        start_idx = text.find("{")
        end_idx = text.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            text = text[start_idx : end_idx + 1]

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse LLM evaluation response into JSON: {str(e)}.\n"
            f"Raw text received:\n{raw_text[:300]}..."
        ) from e

    if not isinstance(data, dict):
        raise ValueError("Parsed JSON is not an object/dictionary.")

    # Validate essential keys and fallback if partially missing
    data.setdefault("overall_score", 0)
    data.setdefault("overall_summary", "No summary provided.")
    data.setdefault("strengths", ["Demonstrated interview readiness"])
    data.setdefault("areas_to_improve", ["Continue practicing technical details"])
    data.setdefault("question_breakdown", [])

    return data


def evaluate_interview(
    role: str,
    resume_text: str,
    conversation_history: List[Dict[str, str]],
) -> Dict[str, Any]:
    """
    Builds the evaluation prompt, calls the LLM at temperature 0.2,
    and returns parsed evaluation data.
    """
    transcript = format_conversation_for_prompt(conversation_history)
    user_prompt = build_evaluation_prompt(
        role=role,
        resume_text=resume_text,
        transcript=transcript,
    )

    messages = [
        {"role": "system", "content": EVALUATION_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    raw_response = call_llm(messages, temperature=0.2)
    parsed_report = clean_and_parse_json(raw_response)
    return parsed_report
