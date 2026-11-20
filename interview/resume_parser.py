"""PDF resume text extraction helper using pypdf."""

import io
import re
from typing import Tuple
from pypdf import PdfReader


def extract_text_from_pdf(pdf_bytes: bytes, max_pages: int = 5) -> Tuple[str, int]:
    """
    Extract readable plain text from an uploaded PDF resume.
    Returns (cleaned_text, total_page_count).
    Raises ValueError with an actionable user-facing message on failure or empty text.
    """
    if not pdf_bytes:
        raise ValueError("Uploaded PDF file is empty.")

    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
    except Exception as e:
        raise ValueError(
            "Unable to read this PDF file. Please ensure it is a valid, uncorrupted PDF."
        ) from e

    if getattr(reader, "is_encrypted", False):
        try:
            decrypt_result = reader.decrypt("")
            if not decrypt_result:
                raise ValueError(
                    "This PDF is password-protected. Please upload an unlocked PDF or paste your resume text below."
                )
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(
                "This PDF is password-protected. Please upload an unlocked PDF or paste your resume text below."
            ) from e

    total_pages = len(reader.pages)
    if total_pages == 0:
        raise ValueError("The uploaded PDF contains no pages.")

    page_texts = []
    for page in reader.pages[:max_pages]:
        raw = page.extract_text() or ""
        if raw.strip():
            page_texts.append(raw)

    combined = "\n\n".join(page_texts)
    # Normalize horizontal whitespace while keeping clean line structure
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in combined.splitlines()]
    cleaned = "\n".join(line for line in lines if line)

    if not cleaned.strip():
        raise ValueError(
            "No selectable text was found in this PDF (it may be a scanned image). "
            "Please upload a text-based PDF or paste your resume text below."
        )

    return cleaned.strip(), total_pages
