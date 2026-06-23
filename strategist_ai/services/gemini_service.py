"""
services/gemini_service.py  (Groq-powered)
───────────────────────────────────────────
All LLM API interactions isolated here.
Powered by Groq — OpenAI-compatible interface, ultra-fast inference.

Models:
    Text  → llama-3.3-70b-versatile
    Vision → meta-llama/llama-4-scout-17b-16e-instruct

Public API (unchanged — consumers don't need to know the backend):
    is_configured()                                  → bool
    generate_report(system_prompt, user_prompt)      → str
    generate_vision_report(system, user, img_bytes)  → str
    stream_report(system, user, img_bytes=None)      → Generator[str]
"""

import os
import base64
from typing import Generator

from groq import Groq

from config.settings import (
    GROQ_TEXT_MODEL,
    GROQ_VISION_MODEL,
    GROQ_TEMPERATURE,
    GROQ_MAX_TOKENS,
)


# ── Client factory ────────────────────────────────────────────────────────────

def _get_client() -> Groq:
    """
    Return an authenticated Groq client.
    Raises EnvironmentError if the key is missing or is still the placeholder.
    """
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key or api_key == "your_groq_api_key_here":
        raise EnvironmentError(
            "GROQ_API_KEY is not set. "
            "Add your key to the .env file: GROQ_API_KEY=gsk_..."
        )
    return Groq(api_key=api_key)


def _detect_mime(image_bytes: bytes) -> str:
    """Detect image MIME type from magic bytes."""
    if image_bytes[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"   # safe default


# ── Public API ────────────────────────────────────────────────────────────────

def is_configured() -> bool:
    """Return True if a valid GROQ_API_KEY is present in the environment."""
    key = os.getenv("GROQ_API_KEY", "").strip()
    return bool(key) and key != "your_groq_api_key_here"


def generate_report(system_prompt: str, user_prompt: str) -> str:
    """
    Generate a text-only strategic report (blocking call).

    Args:
        system_prompt: Master system instruction with injected JSON context.
        user_prompt:   The user's query.

    Returns:
        Full response as a string.
    """
    try:
        client   = _get_client()
        response = client.chat.completions.create(
            model=GROQ_TEXT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=GROQ_TEMPERATURE,
            max_tokens=GROQ_MAX_TOKENS,
        )
        return response.choices[0].message.content

    except EnvironmentError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Groq API error: {exc}") from exc


def generate_vision_report(
    system_prompt: str,
    user_prompt: str,
    image_bytes: bytes,
) -> str:
    """
    Generate a strategic report from a CCTV image + text (blocking call).

    Args:
        system_prompt: Master system instruction.
        user_prompt:   Analysis request.
        image_bytes:   Raw bytes of the uploaded image.

    Returns:
        Full response as a string.
    """
    try:
        client    = _get_client()
        mime_type = _detect_mime(image_bytes)
        b64_image = base64.b64encode(image_bytes).decode("utf-8")
        data_url  = f"data:{mime_type};base64,{b64_image}"

        response = client.chat.completions.create(
            model=GROQ_VISION_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": data_url},
                        },
                    ],
                },
            ],
            temperature=GROQ_TEMPERATURE,
            max_tokens=GROQ_MAX_TOKENS,
        )
        return response.choices[0].message.content

    except EnvironmentError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Groq Vision API error: {exc}") from exc


def stream_report(
    system_prompt: str,
    user_prompt: str,
    image_bytes: bytes | None = None,
) -> Generator[str, None, None]:
    """
    Stream a strategic report token-by-token via Groq.

    Automatically selects vision model when image_bytes is provided.
    Yields text chunks as they arrive — compatible with Streamlit streaming.

    Args:
        system_prompt: Master system instruction with injected JSON.
        user_prompt:   The user's question.
        image_bytes:   Optional raw image bytes for vision analysis.

    Yields:
        str: Text chunk from the streaming response.
    """
    try:
        client = _get_client()

        if image_bytes:
            # ── Vision mode (LLaMA 4 Scout) ───────────────────────────────────
            mime_type = _detect_mime(image_bytes)
            b64_image = base64.b64encode(image_bytes).decode("utf-8")
            data_url  = f"data:{mime_type};base64,{b64_image}"

            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text",      "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ]
            model = GROQ_VISION_MODEL

        else:
            # ── Text mode (LLaMA 3.3 70B) ─────────────────────────────────────
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ]
            model = GROQ_TEXT_MODEL

        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=GROQ_TEMPERATURE,
            max_tokens=GROQ_MAX_TOKENS,
            stream=True,
        )

        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content

    except EnvironmentError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Groq streaming error: {exc}") from exc
