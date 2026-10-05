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

from modules.ai_router import generate_response

from modules.ui import (
    inject_css,
    render_sidebar,
    render_message,
    render_welcome,
)


st.set_page_config(
    page_title="CONSOLE AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
ensure_state()


# ---------------------------------------------------------
# MODEL DISPLAY
# ---------------------------------------------------------

models = [
    "Auto / Best Available",
    "Gemini 3.8 Flash",
    "Gemini 3.7 Flash",
    "Groq",
    "OpenRouter",
]

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "Auto / Best Available"


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

sidebar_action = render_sidebar(
    conversations=st.session_state.conversations,
    active_id=st.session_state.active_conversation_id,
    selected_model=st.session_state.selected_model,
    models=models,
    api_active=True,
)


if sidebar_action:
    action = sidebar_action.get("action")

    if action == "new_chat":
        new_id = create_conversation(
            st.session_state.conversations
        )
        st.session_state.active_conversation_id = new_id
        st.rerun()

    elif action == "select_chat":
        set_active_conversation(
            sidebar_action["conversation_id"]
        )
        st.rerun()

    elif action == "delete_chat":
        delete_conversation(
            sidebar_action["conversation_id"]
        )
        st.rerun()

    elif action == "set_model":
        st.session_state.selected_model = sidebar_action["model"]
        st.rerun()


# ---------------------------------------------------------
# ACTIVE CONVERSATION
# ---------------------------------------------------------

conversation = get_active_conversation()

if conversation is None:
    new_id = create_conversation(
        st.session_state.conversations
    )

    st.session_state.active_conversation_id = new_id

    conversation = get_active_conversation()


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    f"""
    <div class="console-header">
        <div class="header-brand">

            <div class="brand-orb">
                🤖
            </div>

            <div>
                <div class="brand-title">
                    CONSOLE AI
                </div>

                <div class="brand-subtitle">
                    {get_conversation_title(conversation)}
                </div>
            </div>

        </div>

        <div class="header-status">
            <span class="status-dot"></span>
            Auto AI
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# CHAT HISTORY
# ---------------------------------------------------------

messages = conversation["messages"]

if not messages:
    render_welcome()

else:

    for index, message in enumerate(messages):

        render_message(
            message,
            index=index
        )


# ---------------------------------------------------------
# CHAT ACTIONS
# ---------------------------------------------------------

if messages and messages[-1]["role"] == "assistant":

    action_col1, action_col2, _ = st.columns(
        [1, 1, 8]
    )

    with action_col1:

        if st.button(
            "↻ Regenerate",
            key=f"regen_{conversation['id']}"
        ):

            regenerate_last_response(
                conversation
            )

            st.session_state.regenerate_pending = True

            st.rerun()


    with action_col2:

        if st.button(
            "🗑 Clear",
            key=f"clear_{conversation['id']}"
        ):

            conversation["messages"] = []

            conversation["title"] = "New Conversation"

            st.rerun()


# ---------------------------------------------------------
# USER INPUT
# ---------------------------------------------------------

example_prompt = st.session_state.pop(
    "example_prompt",
    None
)

regenerate_pending = st.session_state.pop(
    "regenerate_pending",
    False
)

prompt = (
    example_prompt
    or st.chat_input(
        "Ask a question, request code, or explore ideas…"
    )
)


# ---------------------------------------------------------
# NEW USER MESSAGE
# ---------------------------------------------------------

if prompt and prompt.strip():

    user_text = prompt.strip()

    add_message(
        conversation,
        "user",
        user_text
    )

    if conversation["title"] == "New Conversation":

        conversation["title"] = (
            user_text
            .replace("\n", " ")
            .strip()[:48]
        )

    with st.chat_message(
        "user",
        avatar="👤"
    ):

        st.markdown(user_text)


# ---------------------------------------------------------
# AI GENERATION
# ---------------------------------------------------------

if regenerate_pending or (
    prompt and prompt.strip()
):

    with st.chat_message(
        "assistant",
        avatar="🤖"
    ):

        status = st.empty()

        response_box = st.empty()

        status.markdown(
            """
            <div class="thinking">
                ● ● ●
                <span>
                    CONSOLE AI is thinking…
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

        try:

            # -------------------------------------------------
            # AUTOMATIC PROVIDER ROUTER
            # -------------------------------------------------

            response, provider = generate_response(
                conversation["messages"]
            )

            status.empty()

            response_box.markdown(
                response
            )

            add_message(
                conversation,
                "assistant",
                response
            )

        except Exception as exc:

            status.empty()

            error_message = str(exc)

            friendly = (
                "⚠️ **Unable to complete the request.**\n\n"
                f"{error_message}"
            )

            response_box.markdown(
                friendly
            )

            add_message(
                conversation,
                "assistant",
                friendly
            )

    st.rerun()
