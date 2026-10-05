from __future__ import annotations

import os
from collections.abc import Iterator
from typing import Any

from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-3.8-flash"
DEFAULT_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
]

SYSTEM_INSTRUCTION = """You are CONSOLE AI, a highly capable general-purpose AI assistant.

Answer the user's questions accurately, clearly and helpfully.

For educational questions, explain concepts step by step.

For programming questions:
- Understand the user's code.
- Identify errors.
- Explain why the error occurs.
- Provide corrected code.
- Explain the corrected code.

For mathematical questions:
- Show the required formulas.
- Solve step by step.
- Clearly state the final answer.

For science questions:
- Explain concepts accurately.
- Include equations where useful.

For ambiguous questions, ask for clarification only when necessary.

Do not invent facts. If you are uncertain, clearly state the uncertainty.
Use Markdown formatting. Use fenced code blocks for programming code.
Use LaTeX for mathematical equations when appropriate.
Give concise answers for simple questions and detailed answers for complex questions.

Current-information rule: do not pretend to have live web access. If current information is required and no search/tool result is supplied, clearly say that the answer may need verification.

Your goal is to be a reliable AI assistant for students, programmers and general users."""


class GeminiError(RuntimeError):
    """User-facing Gemini integration error."""


def get_api_key() -> str | None:
    """Read the API key from Streamlit secrets first, then environment variables."""
    try:
        secret = st_secrets_get("GEMINI_API_KEY")
        if secret:
            return secret
    except Exception:
        pass
    value = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if value and value.strip() and value.strip() != "YOUR_API_KEY":
        return value.strip()
    return None


def st_secrets_get(key: str) -> str | None:
    # Import lazily so this module remains importable outside Streamlit tests.
    import streamlit as st

    value = st.secrets.get(key)
    return str(value).strip() if value else None


def is_api_key_configured() -> bool:
    return bool(get_api_key())


def _to_contents(messages: list[dict[str, Any]]) -> list[types.Content]:
    contents: list[types.Content] = []
    for message in messages:
        role = message.get("role")
        text = str(message.get("content", ""))
        if not text:
            continue
        api_role = "user" if role == "user" else "model"
        contents.append(types.Content(role=api_role, parts=[types.Part.from_text(text=text)]))
    return contents


def stream_response(
    api_key: str | None,
    model: str,
    messages: list[dict[str, Any]],
    system_instruction: str = SYSTEM_INSTRUCTION,
) -> Iterator[str]:
    """Stream Gemini output as text chunks."""
    if not api_key:
        raise GeminiError("Gemini API key is not configured.")
    if not messages:
        raise GeminiError("There is no user message to send.")

    try:
        client = genai.Client(api_key=api_key)
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
            max_output_tokens=8192,
        )
        response_stream = client.models.generate_content_stream(
            model=model,
            contents=_to_contents(messages),
            config=config,
        )
        for chunk in response_stream:
            text = getattr(chunk, "text", None)
            if text:
                yield text
    except Exception as exc:
        message = str(exc)
        lowered = message.lower()
        if "api key" in lowered or "unauthenticated" in lowered or "permission" in lowered:
            raise GeminiError("The Gemini API key appears invalid or does not have access to this model.") from exc
        if "quota" in lowered or "resource exhausted" in lowered or "429" in lowered:
            raise GeminiError("Gemini API quota or rate limit was reached. Please try again later or use another model.") from exc
        if "not found" in lowered or "404" in lowered:
            raise GeminiError(f"The model `{model}` is unavailable. Choose another model from the sidebar.") from exc
        if "deadline" in lowered or "timeout" in lowered or "connection" in lowered:
            raise GeminiError("The connection to Gemini timed out or failed. Check your network and try again.") from exc
        raise GeminiError("Gemini returned an error while generating the response.") from exc
