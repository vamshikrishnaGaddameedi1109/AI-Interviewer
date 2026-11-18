"""Gemini LLM client optimized for fast Flash responses with bounded exponential-backoff retries."""

import os
import time
import threading
from typing import List, Dict, Union, Any, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Active fast Gemini Flash models (avoid deprecated 1.5/2.0 and retired 2.5-flash-lite)
_DEPRECATED_MODELS = {
    "gemini-pro",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.0-pro",
    "gemini-2.0-flash-thinking",
    "gemini-2.5-flash-lite",
}
_ENV_MODEL = os.environ.get("GEMINI_MODEL", "").strip()
_FLASH_MODELS = [
    "gemini-4-hydrogen",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
]
CANDIDATE_MODELS: List[str] = list(
    dict.fromkeys(
        ([_ENV_MODEL] if (_ENV_MODEL and _ENV_MODEL.lower() not in _DEPRECATED_MODELS) else [])
        + _FLASH_MODELS
    )
)

# Maximum retry attempts after the initial call (1 initial + max 2 retries = 3 attempts max)
MAX_RETRIES: int = 2
BASE_BACKOFF_SECONDS: float = 1.0

_CLIENT_LOCK = threading.Lock()
_CLIENT_CACHE: Dict[Tuple[str, int], Any] = {}


class LLMServiceUnavailableError(RuntimeError):
    """Raised when Gemini API fails due to 503, 504 DEADLINE_EXCEEDED, 429, or network errors."""


def get_api_key() -> str:
    """Retrieve the Gemini API key from the environment."""
    return os.environ.get("GEMINI_API_KEY", "").strip()


def _get_client(api_key: str, timeout_ms: int) -> Any:
    """Reuse cached genai.Client configured with single-attempt HTTP (no hidden SDK retry storms)."""
    from google import genai
    from google.genai import types

    cache_key = (api_key, timeout_ms)
    with _CLIENT_LOCK:
        client = _CLIENT_CACHE.get(cache_key)
        if client is None:
            client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(
                    timeout=timeout_ms,
                    headers={"User-Agent": "aistudio-build"},
                    # Disable SDK's default 5x internal retry loop so our explicit
                    # max-2-retry exponential backoff controls total latency cleanly.
                    retry_options=types.HttpRetryOptions(attempts=1),
                ),
            )
            _CLIENT_CACHE[cache_key] = client
        return client


def is_transient_error(error_str: str) -> bool:
    """Check if the error is a temporary 503/504/429 or transient network failure."""
    indicators = [
        "503",
        "504",
        "DEADLINE_EXCEEDED",
        "UNAVAILABLE",
        "high demand",
        "temporarily unavailable",
        "429",
        "RESOURCE_EXHAUSTED",
        "rate limit",
        "overloaded",
        "timeout",
        "timed out",
        "connection",
        "network",
        "reset by peer",
        "eof",
    ]
    lower = error_str.lower()
    return any(ind.lower() in lower for ind in indicators)


def _is_model_not_found_error(error_str: str) -> bool:
    """Check if the model returned 404 NOT_FOUND or is unsupported."""
    lower = error_str.lower()
    return "404" in lower or "not_found" in lower or "is not found" in lower or "no longer available" in lower


def _is_thinking_unsupported_error(error_str: str) -> bool:
    """Check if a model rejected thinking_config."""
    lower = error_str.lower()
    return ("thinking" in lower or "budget" in lower or "level" in lower) and (
        "invalid" in lower or "unsupported" in lower or "only works" in lower or "400" in lower
    )


def call_llm(
    messages: Union[str, List[Dict[str, str]]],
    temperature: float = 0.7,
    json_mode: bool = False,
    max_output_tokens: Optional[int] = None,
    disable_thinking: bool = True,
    timeout_ms: int = 12000,
    model_candidates: Optional[List[str]] = None,
    max_retries: int = MAX_RETRIES,
) -> str:
    """
    Invoke an active fast Gemini Flash model with:
    - Single-attempt HTTP timeout per call (prevents hidden SDK retry storms causing 504s)
    - Low/Minimal thinking configured appropriately per model family
    - Maximum of 2 retry attempts with exponential backoff (1.0s, 2.0s) for 503/504/network errors
    """
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Please create a .env file with your GEMINI_API_KEY "
            "or set it in your environment variables."
        )

    from google.genai import types

    client = _get_client(api_key, timeout_ms)
    models = list(model_candidates or CANDIDATE_MODELS)

    # Normalize string vs list messages
    if isinstance(messages, str):
        system_instruction = None
        contents: Any = messages
    elif isinstance(messages, list):
        system_instruction = None
        genai_contents = []

        for msg in messages:
            role = msg.get("role", "user").lower()
            content_text = msg.get("content", "")

            if role == "system":
                system_instruction = (
                    f"{system_instruction}\n\n{content_text}"
                    if system_instruction
                    else content_text
                )
            elif role in ("assistant", "model"):
                genai_contents.append(
                    types.Content(
                        role="model",
                        parts=[types.Part.from_text(text=content_text)],
                    )
                )
            else:
                genai_contents.append(
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=content_text)],
                    )
                )

        contents = genai_contents if genai_contents else ""
    else:
        contents = str(messages)
        system_instruction = None

    def _build_config(model_name: str, use_thinking_disable: bool) -> types.GenerateContentConfig:
        lower_name = model_name.lower()
        is_gemini4 = lower_name.startswith("gemini-4")
        is_gemini3 = lower_name.startswith("gemini-3")

        config_kwargs: Dict[str, Any] = {}
        # Gemini 4 models reject temperature/topP/topK and thinkingBudget; use ThinkingLevel instead.
        if not is_gemini4:
            config_kwargs["temperature"] = temperature
            if max_output_tokens is not None:
                config_kwargs["max_output_tokens"] = max_output_tokens

        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction
        if json_mode:
            config_kwargs["response_mime_type"] = "application/json"

        if use_thinking_disable:
            if is_gemini4:
                config_kwargs["thinking_config"] = types.ThinkingConfig(
                    thinking_level=types.ThinkingLevel.LOW
                )
            elif is_gemini3:
                config_kwargs["thinking_config"] = types.ThinkingConfig(
                    thinking_level=types.ThinkingLevel.MINIMAL
                )
            else:
                config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=0)

        return types.GenerateContentConfig(**config_kwargs)

    # Cap transient retries strictly to max_retries (default: 2 retries = 3 attempts max)
    capped_retries = max(0, min(max_retries, MAX_RETRIES))
    transient_retries_used = 0
    tried_not_found = set()
    model_idx = 0
    last_error: Optional[Exception] = None
    saw_transient = False

    while True:
        # Select next candidate model that hasn't returned 404 NOT_FOUND
        available_indices = [i for i, m in enumerate(models) if m not in tried_not_found]
        if not available_indices:
            break
        if models[model_idx] in tried_not_found:
            model_idx = available_indices[0]

        model_name = models[model_idx]
        use_thinking_disable = disable_thinking

        while True:
            try:
                config = _build_config(model_name, use_thinking_disable)
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config,
                )
                if response and response.text:
                    return response.text.strip()
                raise RuntimeError("Empty response received from Gemini model.")

            except Exception as e:
                last_error = e
                err_text = str(e)

                # If this specific model rejects thinking_config, retry immediately without it
                if use_thinking_disable and _is_thinking_unsupported_error(err_text):
                    use_thinking_disable = False
                    continue

                # If model is unavailable/retired (404), skip it immediately and try next active model
                if _is_model_not_found_error(err_text):
                    tried_not_found.add(model_name)
                    model_idx = (model_idx + 1) % len(models)
                    break

                if is_transient_error(err_text):
                    saw_transient = True
                    if transient_retries_used < capped_retries:
                        backoff = BASE_BACKOFF_SECONDS * (2 ** transient_retries_used)
                        transient_retries_used += 1
                        model_idx = (model_idx + 1) % len(models)
                        time.sleep(backoff)
                        break

                    raise LLMServiceUnavailableError(
                        f"Gemini API temporarily unavailable after {capped_retries} retries: {err_text}"
                    ) from e

                raise RuntimeError(f"Gemini API Error ({model_name}): {err_text}") from e

    if saw_transient and last_error is not None:
        raise LLMServiceUnavailableError(
            f"Gemini API temporarily unavailable: {str(last_error)}"
        ) from last_error
    raise RuntimeError(f"Gemini API Error: {str(last_error)}") from last_error
