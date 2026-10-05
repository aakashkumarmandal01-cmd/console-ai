import os
from typing import List, Dict, Tuple

from google import genai
from groq import Groq
from openai import OpenAI


def _secret(name: str):
    try:
        import streamlit as st
        value = st.secrets.get(name)
        if value:
            return value
    except Exception:
        pass

    return os.getenv(name)


def _gemini(messages: List[Dict]) -> str:
    key = _secret("GEMINI_API_KEY")

    if not key:
        raise RuntimeError("Gemini API key not configured.")

    client = genai.Client(api_key=key)

    prompt = "\n\n".join(
        f"{m['role'].upper()}: {m['content']}"
        for m in messages
    )

    response = client.models.generate_content(
        model="gemini-3.7-flash",
        contents=prompt,
    )

    return response.text or ""


def _groq(messages: List[Dict]) -> str:
    key = _secret("GROQ_API_KEY")

    if not key:
        raise RuntimeError("Groq API key not configured.")

    client = Groq(api_key=key)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
    )

    return response.choices[0].message.content or ""


def _openrouter(messages: List[Dict]) -> str:
    key = _secret("OPENROUTER_API_KEY")

    if not key:
        raise RuntimeError("OpenRouter API key not configured.")

    client = OpenAI(
        api_key=key,
        base_url="https://openrouter.ai/api/v1",
    )

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
    )

    return response.choices[0].message.content or ""


PROVIDERS = [
    ("Groq", _groq),
    ("Gemini", _gemini),
    ("OpenRouter", _openrouter),
]


def generate_response(
    messages: List[Dict],
) -> Tuple[str, str]:

    errors = []

    for provider_name, provider in PROVIDERS:

        try:
            response = provider(messages)

            if response.strip():
                return response, provider_name

        except Exception as exc:

            errors.append(
                f"{provider_name}: {exc}"
            )

            # Immediately move to the next provider.
            continue

    raise RuntimeError(
        "All configured AI providers are unavailable."
    )
