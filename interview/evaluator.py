"""Evaluation module: builds evaluation prompt, invokes LLM, and parses JSON output with fresher/junior calibrated defaults."""

import json
import re
from typing import Dict, Any, List
from interview.llm import call_llm
from interview.prompts import build_evaluation_prompt, EVALUATION_SYSTEM_PROMPT
from interview.flow import format_conversation_for_prompt


def _clamp_int(val: Any, low: int, high: int, default: int) -> int:
    try:
        num = int(round(float(val)))
        return max(low, min(high, num))
    except (TypeError, ValueError):
        return default


def clean_and_parse_json(raw_text: str) -> Dict[str, Any]:
    """
    Strip any markdown code fences, extraneous text, and trailing commas before parsing JSON.
    Raises ValueError with clear message if parsing fails.
    """
    if not raw_text or not raw_text.strip():
        raise ValueError("Empty evaluation response received from Gemini.")

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

    # Remove trailing commas before closing braces/brackets
    text = re.sub(r",\s*([}\]])", r"\1", text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse LLM evaluation response into JSON: {str(e)}.\n"
            f"Raw text received:\n{raw_text[:300]}..."
        ) from e

    if not isinstance(data, dict):
        raise ValueError("Parsed JSON is not an object/dictionary.")

    # Validate essential keys and apply defaults calibrated for freshers
    overall_score = _clamp_int(data.get("overall_score", 74), 0, 100, 74)
    data["overall_score"] = overall_score

    # Hiring recommendation
    if not data.get("hiring_recommendation"):
        if overall_score >= 82:
            data["hiring_recommendation"] = "Strong Hire (Campus / Junior)"
        elif overall_score >= 68:
            data["hiring_recommendation"] = "Hire (Meets Fresher Bar)"
        elif overall_score >= 54:
            data["hiring_recommendation"] = "Leaning Hire (Needs Mentorship)"
        else:
            data["hiring_recommendation"] = "Needs Preparation"

    data.setdefault(
        "overall_summary",
        "Demonstrated good foundational understanding and enthusiasm. Will benefit from deeper explanation of data structures and structured project storytelling.",
    )

    # Strengths
    raw_strengths = data.get("strengths")
    if not isinstance(raw_strengths, list) or not raw_strengths:
        data["strengths"] = [
            "Clear understanding of core programming syntax and basic computer science fundamentals.",
            "Enthusiastic and eager attitude towards learning new technologies and tools.",
            "Able to explain academic project objectives and personal contributions clearly.",
        ]

    # Category scores (clamped 0-100)
    raw_cat = data.get("category_scores")
    if not isinstance(raw_cat, dict):
        raw_cat = {}

    data["category_scores"] = {
        "technical_depth": _clamp_int(raw_cat.get("technical_depth"), 0, 100, min(max(overall_score + 1, 20), 98)),
        "problem_solving": _clamp_int(raw_cat.get("problem_solving"), 0, 100, min(max(overall_score - 1, 20), 96)),
        "communication_clarity": _clamp_int(raw_cat.get("communication_clarity"), 0, 100, min(max(overall_score + 3, 20), 99)),
        "role_alignment": _clamp_int(raw_cat.get("role_alignment"), 0, 100, min(max(overall_score, 20), 95)),
    }

    # Actionable suggestions tailored for freshers and entry-to-mid candidates
    raw_suggestions = data.get("actionable_suggestions")
    if not isinstance(raw_suggestions, list) or not raw_suggestions:
        data["actionable_suggestions"] = [
            {
                "priority": "High",
                "category": "Problem Solving & DSA",
                "title": "Always State Time & Space Complexity (Big-O)",
                "advice": "In campus and entry-level coding interviews, interviewers always look for candidates who mention Big-O without being prompted. Whenever you propose a solution, immediately state: 'This approach takes O(N) time and O(1) space because...'",
                "action_item": "Review Big-O complexity for basic operations on Arrays, HashMaps, Binary Search Trees, and common sorting algorithms (QuickSort, MergeSort).",
            },
            {
                "priority": "High",
                "category": "Project Articulation",
                "title": "Explain Your Projects with Architecture, Not Just Features",
                "advice": "Instead of only stating what the project does ('It is a recipe app'), explain the technical architecture: frontend framework, backend API endpoints, database schema, and one difficult bug you debugged.",
                "action_item": "Prepare a 60-second pitch for your main college project covering: Problem -> Tech Stack -> Your specific code contributions -> Hardest bug solved.",
            },
            {
                "priority": "Medium",
                "category": "Core Fundamentals",
                "title": "Connect OOP Theory to Practical Code Examples",
                "advice": "When asked about Object-Oriented Programming (Polymorphism, Encapsulation, Inheritance), avoid reciting textbook definitions. Give a quick real-world code example (e.g., 'An Animal base class with a makeSound() method overridden by Dog').",
                "action_item": "Write a 5-line code snippet demonstrating method overriding vs overloading in your preferred programming language.",
            },
        ]

    # Model answer transformation for fresher interview question
    model_ans = data.get("model_answer_transformation")
    if not isinstance(model_ans, dict) or not model_ans.get("ideal_model_answer"):
        data["model_answer_transformation"] = {
            "question": "Can you explain the difference between an Array and a Linked List, and when you would use each?",
            "candidate_flaw": "Gave a brief theoretical answer ('Array has fixed size, Linked List has nodes') without explaining memory layout, access time complexity, or practical use cases.",
            "ideal_model_answer": "An array stores elements in contiguous memory locations, which gives us instant O(1) random access by index. However, resizing requires allocating a new memory block and copying, and inserting in the middle takes O(N) time. In contrast, a Linked List stores data in discrete nodes containing values and pointers. Inserting or deleting at the head is O(1) without shifting, but finding an element requires O(N) sequential traversal because memory is not contiguous. In practice, I'd use an Array when I need fast indexing or know the collection size upfront, and a Linked List when frequent insertions/deletions at the boundaries occur.",
            "key_takeaway": "Always compare time complexity, memory allocation (contiguous vs pointers), and give a real-world scenario where one beats the other.",
        }

    # Study topics for freshers / campus placement
    study_topics = data.get("study_topics")
    if not isinstance(study_topics, list) or not study_topics:
        data["study_topics"] = [
            "Data Structures: Hash Maps vs Binary Trees (Lookup time & collisions)",
            "SQL Basics: INNER vs LEFT JOIN, GROUP BY, and basic indexing",
            "OOP Pillars: Polymorphism vs Inheritance with code examples",
            "Web Fundamentals: REST API status codes (200, 201, 400, 404, 500)",
        ]

    # Communication coaching
    comm_coach = data.get("communication_coaching")
    if not isinstance(comm_coach, dict):
        data["communication_coaching"] = {
            "pacing_and_conciseness": "Speak clearly and take a 5-second pause to organize your thoughts before answering complex questions.",
            "star_framework_usage": "When talking about college projects or team conflicts, use STAR (Situation, Task, Action, Result) to stay structured.",
            "executive_presence": "Demonstrate curiosity and coachability. If you do not know a syntax rule, explain your logical thought process honestly.",
        }

    # Normalize question_breakdown scores (0-10)
    raw_breakdown = data.get("question_breakdown")
    if isinstance(raw_breakdown, list):
        normalized_breakdown = []
        for item in raw_breakdown:
            if isinstance(item, dict):
                normalized_breakdown.append({
                    "question": str(item.get("question", "Interview Question")),
                    "answer_summary": str(item.get("answer_summary", "Candidate answered.")),
                    "score": _clamp_int(item.get("score", 7), 0, 10, 7),
                    "feedback": str(item.get("feedback", "")),
                })
        data["question_breakdown"] = normalized_breakdown
    else:
        data["question_breakdown"] = []

    return data


def evaluate_interview(
    role: str,
    resume_text: str,
    conversation_history: List[Dict[str, str]],
) -> Dict[str, Any]:
    """
    Builds a compact evaluation prompt, calls the fast Gemini Flash model at temperature 0.2,
    and returns parsed evaluation JSON data. Propagates API/parsing errors for explicit Retry handling.
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

    raw_response = call_llm(
        messages,
        temperature=0.2,
        json_mode=True,
        max_output_tokens=1600,
        disable_thinking=True,
        timeout_ms=15000,
    )
    parsed_report = clean_and_parse_json(raw_response)
    return parsed_report
