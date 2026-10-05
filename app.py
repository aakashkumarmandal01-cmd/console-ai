import os

import streamlit as st
from google import genai
from groq import Groq
from openai import OpenAI


def get_key(name):
    try:
        value = st.secrets.get(name)
        if value:
            return value
    except Exception:
        pass

    return os.getenv(name)


def call_groq(messages):
    key = get_key("GROQ_API_KEY")

    if not key:
        raise RuntimeError("Groq API key is not configured.")

    client = Groq(api_key=key)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7,
    )

    return response.choices[0].message.content


def call_gemini(messages):
    key = get_key("GEMINI_API_KEY")

    if not key:
        raise RuntimeError("Gemini API key is not configured.")

    client = genai.Client(api_key=key)

    prompt = "\n\n".join(
        f"{message['role']}: {message['content']}"
        for message in messages
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text


def call_openrouter(messages):
    key = get_key("OPENROUTER_API_KEY")

    if not key:
        raise RuntimeError("OpenRouter API key is not configured.")

    client = OpenAI(
        api_key=key,
        base_url="https://openrouter.ai/api/v1",
    )

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        temperature=0.7,
    )

    return response.choices[0].message.content


def generate_response(messages):

    providers = [
        ("Groq", call_groq),
        ("Gemini", call_gemini),
        ("OpenRouter", call_openrouter),
    ]

    errors = []

    for name, function in providers:

        try:
            answer = function(messages)

            if answer and answer.strip():
                return answer, name

        except Exception as error:
            errors.append(f"{name}: {error}")
            continue

    raise RuntimeError(
        "All configured AI providers failed.\n\n"
        + "\n".join(errors)
    )
