"""Image assets helper with base64 data-URI caching and resilient CSS fallbacks."""

import os
import base64
from typing import Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(BASE_DIR, "src", "assets", "images")

INTERVIEWER_AVATAR_FILE = "avatar_interviewer_1790948797230.jpg"
CANDIDATE_AVATAR_FILE = "avatar_candidate_1790948810999.jpg"
HERO_ROOM_FILE = "hero_interview_room_1790948825828.jpg"

_cache = {}


def _get_base64_image(filename: str) -> Optional[str]:
    if filename in _cache:
        return _cache[filename]

    filepath = os.path.join(IMAGES_DIR, filename)
    if os.path.isfile(filepath):
        try:
            with open(filepath, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                mime = "image/jpeg" if filename.endswith((".jpg", ".jpeg")) else "image/png"
                data_uri = f"data:{mime};base64,{encoded}"
                _cache[filename] = data_uri
                return data_uri
        except Exception:
            return None
    return None


def get_interviewer_avatar_uri() -> Optional[str]:
    return _get_base64_image(INTERVIEWER_AVATAR_FILE)


def get_candidate_avatar_uri() -> Optional[str]:
    return _get_base64_image(CANDIDATE_AVATAR_FILE)


def get_hero_room_uri() -> Optional[str]:
    return _get_base64_image(HERO_ROOM_FILE)
