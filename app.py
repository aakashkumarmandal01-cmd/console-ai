from __future__ import annotations

import streamlit as st

from modules.chat_manager import (
    add_message,
    create_conversation,
    delete_conversation,
    ensure_state,
    get_active_conversation,
    get_conversation_title,
    regenerate_last_response,
    set_active_conversation,
)
from modules.gemini import (
    DEFAULT_MODEL,
    DEFAULT_MODELS,
    SYSTEM_INSTRUCTION,
    GeminiError,
    get_api_key,
    is_api_key_configured,
    stream_response,
)
from modules.ui import inject_css, render_sidebar, render_message, render_welcome


st.set_page_config(
    page_title="CONSOLE AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
ensure_state()

# Keep the model list easy to extend from one place.
models = st.session_state.get("available_models", DEFAULT_MODELS)
if "selected_model" not in st.session_state:
    st.session_state.selected_model = DEFAULT_MODEL
if st.session_state.selected_model not in models:
    st.session_state.selected_model = models[0]

sidebar_action = render_sidebar(
    conversations=st.session_state.conversations,
    active_id=st.session_state.active_conversation_id,
    selected_model=st.session_state.selected_model,
    models=models,
    api_active=is_api_key_configured(),
)

if sidebar_action:
    action = sidebar_action.get("action")
    if action == "new_chat":
        new_id = create_conversation(st.session_state.conversations)
        st.session_state.active_conversation_id = new_id
        st.rerun()
    elif action == "select_chat":
        set_active_conversation(sidebar_action["conversation_id"])
        st.rerun()
    elif action == "delete_chat":
        delete_conversation(sidebar_action["conversation_id"])
        st.rerun()
    elif action == "set_model":
        st.session_state.selected_model = sidebar_action["model"]
        st.rerun()

conversation = get_active_conversation()
if conversation is None:
    new_id = create_conversation(st.session_state.conversations)
    st.session_state.active_conversation_id = new_id
    conversation = get_active_conversation()

# Main header.
st.markdown(
    f"""
    <div class="console-header">
        <div class="header-brand">
            <div class="brand-orb">🤖</div>
            <div>
                <div class="brand-title">CONSOLE AI</div>
                <div class="brand-subtitle">{get_conversation_title(conversation)}</div>
            </div>
        </div>
        <div class="header-status">
            <span class="status-dot"></span> {st.session_state.selected_model}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Chat history.
messages = conversation["messages"]
if not messages:
    render_welcome()
else:
    for index, message in enumerate(messages):
        render_message(message, index=index)

# Lightweight actions for the last completed AI response.
if messages and messages[-1]["role"] == "assistant":
    action_col1, action_col2, _ = st.columns([1, 1, 8])
    with action_col1:
        if st.button("↻ Regenerate", key=f"regen_{conversation['id']}"):
            regenerate_last_response(conversation)
            st.session_state.regenerate_pending = True
            st.rerun()
    with action_col2:
        if st.button("🗑 Clear", key=f"clear_{conversation['id']}"):
            conversation["messages"] = []
            conversation["title"] = "New Conversation"
            st.rerun()

example_prompt = st.session_state.pop("example_prompt", None)
regenerate_pending = st.session_state.pop("regenerate_pending", False)
prompt = example_prompt or st.chat_input("Ask a question, request code, or explore ideas…")

# A regeneration reuses the existing last user message without duplicating it.
if regenerate_pending and conversation["messages"] and conversation["messages"][-1]["role"] == "user":
    prompt = None

if prompt and prompt.strip():
    user_text = prompt.strip()
    add_message(conversation, "user", user_text)

    if conversation["title"] == "New Conversation":
        conversation["title"] = user_text.replace("\n", " ").strip()[:48]

    with st.chat_message("user", avatar="👤"):
        st.markdown(user_text)

if regenerate_pending or (prompt and prompt.strip()):
    if not is_api_key_configured():
        error = (
            "⚠️ **Gemini API key missing.** Add `GEMINI_API_KEY` to "
            "`.streamlit/secrets.toml` or your environment, then restart Streamlit."
        )
        add_message(conversation, "assistant", error)
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(error)
        st.stop()

    with st.chat_message("assistant", avatar="🤖"):
        status = st.empty()
        response_box = st.empty()
        status.markdown("<div class='thinking'>● ● ● <span>CONSOLE AI is thinking…</span></div>", unsafe_allow_html=True)
        full_response = ""
        try:
            for chunk in stream_response(
                api_key=get_api_key(),
                model=st.session_state.selected_model,
                messages=conversation["messages"],
                system_instruction=SYSTEM_INSTRUCTION,
            ):
                if chunk:
                    full_response += chunk
                    response_box.markdown(full_response)
            status.empty()
            if not full_response.strip():
                raise GeminiError("The model returned an empty response.")
            add_message(conversation, "assistant", full_response)
        except GeminiError as exc:
            status.empty()
            friendly = f"⚠️ **Unable to complete the request.**\n\n{exc}"
            response_box.markdown(friendly)
            add_message(conversation, "assistant", friendly)
        except Exception:
            status.empty()
            friendly = (
                "⚠️ **Unable to connect to the AI service.** "
                "Please check your API key, selected model, network connection, or quota and try again."
            )
            response_box.markdown(friendly)
            add_message(conversation, "assistant", friendly)

    st.rerun()
