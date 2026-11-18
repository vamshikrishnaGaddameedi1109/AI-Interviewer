import os
import time
from typing import List, Dict, Union, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# List of models to try in order of preference if high demand / 503 occurs
CANDIDATE_MODELS = [
    os.environ.get("GEMINI_MODEL", "gemini-3.8-flash"),
    "gemini-flash-latest",
    "gemini-3.1-flash-lite",
]
# Remove duplicates while preserving order
CANDIDATE_MODELS = list(dict.fromkeys(CANDIDATE_MODELS))


def get_api_key() -> str:
    """Retrieve the Gemini API key from the environment."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    return api_key


def _is_transient_error(error_str: str) -> bool:
    """Check if the error is a temporary capacity/rate limit issue suitable for retry/fallback."""
    indicators = [
        "503",
        "UNAVAILABLE",
        "high demand",
        "temporarily unavailable",
        "429",
        "RESOURCE_EXHAUSTED",
        "rate limit",
        "overloaded",
    ]
    return any(ind.lower() in error_str.lower() for ind in indicators)


def call_llm(messages: Union[str, List[Dict[str, str]]], temperature: float = 0.7) -> str:
    """
    Single wrapper function around the LLM SDK with automatic retry and model failover.
    
    Args:
        messages: Either a single prompt string or a list of message dicts
                  e.g., [{"role": "system"|"user"|"assistant", "content": "..."}]
        temperature: Sampling temperature (e.g. 0.7 for creative questions, 0.2 for evaluation)
        
    Returns:
        Generated text response from the model.
        
    Raises:
        RuntimeError: If the API key is missing or all models and retries fail.
    """
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Please create a .env file with your GEMINI_API_KEY "
            "or set it in your environment variables."
        )

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    # Handle string vs list input
    if isinstance(messages, str):
        system_instruction = None
        contents = messages
    elif isinstance(messages, list):
        system_instruction = None
        genai_contents = []

        for msg in messages:
            role = msg.get("role", "user").lower()
            content_text = msg.get("content", "")

            if role == "system":
                if system_instruction:
                    system_instruction += "\n\n" + content_text
                else:
                    system_instruction = content_text
            elif role in ("assistant", "model"):
                genai_contents.append(
                    types.Content(
                        role="model",
                        parts=[types.Part.from_text(text=content_text)]
                    )
                )
            else:  # default to user
                genai_contents.append(
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=content_text)]
                    )
                )

        contents = genai_contents if genai_contents else ""
    else:
        contents = str(messages)
        system_instruction = None

    config_kwargs: Dict[str, Any] = {
        "temperature": temperature,
    }
    if system_instruction:
        config_kwargs["system_instruction"] = system_instruction

    config = types.GenerateContentConfig(**config_kwargs)

    last_error: Optional[Exception] = None

    # Try each candidate model in priority order
    for model_name in CANDIDATE_MODELS:
        # Up to 2 attempts per model for transient errors
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config,
                )

                if response and response.text:
                    return response.text.strip()
                raise RuntimeError("Empty response received from the model.")

            except Exception as e:
                last_error = e
                err_text = str(e)

                # If it's a transient 503 / 429 error, sleep briefly and try next attempt or fallback
                if _is_transient_error(err_text):
                    time.sleep(1.2 * (attempt + 1))
                    continue
                else:
                    # Non-transient error (e.g. invalid parameter), don't retry same model
                    break

    # If all models and retries failed
    raise RuntimeError(
        f"LLM API Error (all candidate models exhausted): {str(last_error)}"
    ) from last_error
