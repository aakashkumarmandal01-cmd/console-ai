from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import streamlit as st


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_conversation() -> dict:
    return {
        "id": uuid4().hex,
        "title": "New Conversation",
        "created_at": _now_iso(),
        "messages": [],
    }


def ensure_state() -> None:
    if "conversations" not in st.session_state:
        first = _new_conversation()
        st.session_state.conversations = [first]
        st.session_state.active_conversation_id = first["id"]
    elif "active_conversation_id" not in st.session_state:
        st.session_state.active_conversation_id = st.session_state.conversations[0]["id"]


def create_conversation(conversations: list[dict]) -> str:
    conversation = _new_conversation()
    conversations.insert(0, conversation)
    return conversation["id"]


def get_active_conversation() -> dict | None:
    active_id = st.session_state.get("active_conversation_id")
    for conversation in st.session_state.get("conversations", []):
        if conversation["id"] == active_id:
            return conversation
    return None


def set_active_conversation(conversation_id: str) -> None:
    if any(c["id"] == conversation_id for c in st.session_state.conversations):
        st.session_state.active_conversation_id = conversation_id


def get_conversation_title(conversation: dict) -> str:
    return conversation.get("title") or "New Conversation"


def add_message(conversation: dict, role: str, content: str) -> None:
    conversation["messages"].append(
        {
            "role": role,
            "content": content,
            "created_at": _now_iso(),
        }
    )


def delete_conversation(conversation_id: str) -> None:
    conversations = st.session_state.conversations
    st.session_state.conversations = [c for c in conversations if c["id"] != conversation_id]
    if not st.session_state.conversations:
        new_id = create_conversation(st.session_state.conversations)
        st.session_state.active_conversation_id = new_id
        return
    if st.session_state.active_conversation_id == conversation_id:
        st.session_state.active_conversation_id = st.session_state.conversations[0]["id"]


def regenerate_last_response(conversation: dict) -> None:
    """Remove the last assistant response so app.py can generate it again."""
    if conversation["messages"] and conversation["messages"][-1]["role"] == "assistant":
        conversation["messages"].pop()
