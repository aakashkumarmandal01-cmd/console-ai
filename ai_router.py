import os
import time
from typing import List, Dict, Tuple

from google import genai
from groq import Groq
from mistralai import Mistral
from cerebras.cloud.sdk import Cerebras
from openai import OpenAI


def _secret(name: str):
    try:
        import streamlit as st
        return st.secrets.get(name) or os.getenv(name)
    except Exception:
        return os.getenv(name)


def _gemini(messages: List[Dict]) -> str:
    key = _secret("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("Gemini API key is missing.")

    client = genai.Client(api_key=key)

    prompt = "\n\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in messages
    )

    response = client.models.generate_content(
        model="gemini-3.7-flash",
        contents=prompt,
    )

    return response.text or ""


def _groq(messages: List[Dict]) -> str:
    key = _secret("GROQ_API_KEY")
    if not key:
        raise RuntimeError("Groq API key is missing.")

    client = Groq(api_key=key)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
    )

    return response.choices[0].message.content or ""


def _mistral(messages: List[Dict]) -> str:
    key = _secret("MISTRAL_API_KEY")
    if not key:
        raise RuntimeError("Mistral API key is missing.")

    client = Mistral(api_key=key)

    response = client.chat.complete(
        model="mistral-small-latest",
        messages=messages,
    )

    return response.choices[0].message.content or ""


def _cerebras(messages: List[Dict]) -> str:
    key = _secret("CEREBRAS_API_KEY")
    if not key:
        raise RuntimeError("Cerebras API key is missing.")

    client = Cerebras(api_key=key)

    response = client.chat.completions.create(
        model="llama-3.3-70b",
        messages=messages,
    )

    return response.choices[0].message.content or ""


def _openrouter(messages: List[Dict]) -> str:
    key = _secret("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OpenRouter API key is missing.")

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
    ("Gemini", _gemini),
    ("Groq", _groq),
    ("Mistral", _mistral),
    ("Cerebras", _cerebras),
    ("OpenRouter", _openrouter),
]


def generate_response(messages: List[Dict]) -> Tuple[str, str]:
    errors = []

    for provider_name, provider_function in PROVIDERS:
        for attempt in range(2):
            try:
                result = provider_function(messages)

                if result.strip():
                    return result, provider_name

            except Exception as exc:
                error_text = str(exc)
                errors.append(f"{provider_name}: {error_text}")

                # Retry temporary/rate-limit errors once.
                temporary = any(
                    code in error_text
                    for code in ("429", "500", "502", "503", "504", "timeout")
                )

                if temporary and attempt == 0:
                    time.sleep(1)
                    continue

                break

    raise RuntimeError(
        "All configured AI providers failed.\n\n"
        + "\n".join(errors[-5:])
    )
