from __future__ import annotations

from html import escape

import streamlit as st


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --console-bg: #08090b;
            --console-panel: #0e1014;
            --console-panel-2: #12151a;
            --console-border: #22262d;
            --console-text: #f2f4f7;
            --console-muted: #8b929d;
            --console-accent: #8b5cf6;
            --console-accent-2: #6366f1;
        }
        .stApp { background: var(--console-bg); color: var(--console-text); }
        [data-testid="stSidebar"] {
            background: #0a0b0e;
            border-right: 1px solid var(--console-border);
        }
        [data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }
        .block-container { max-width: 1180px; padding: 1rem 1.25rem 6.5rem; }
        .console-header {
            display:flex; align-items:center; justify-content:space-between;
            padding: .65rem .2rem 1rem; border-bottom: 1px solid var(--console-border); margin-bottom: 1.5rem;
        }
        .header-brand { display:flex; align-items:center; gap:.8rem; }
        .brand-orb { width:42px; height:42px; display:grid; place-items:center; border-radius:14px; background:linear-gradient(135deg,#171a22,#272038); border:1px solid #302943; }
        .brand-title { font-weight:750; letter-spacing:.02em; font-size:1.05rem; }
        .brand-subtitle { color:var(--console-muted); font-size:.78rem; margin-top:.1rem; }
        .header-status { color:var(--console-muted); font-size:.78rem; border:1px solid var(--console-border); padding:.42rem .65rem; border-radius:999px; }
        .status-dot { display:inline-block; width:7px; height:7px; border-radius:50%; background:#34d399; margin-right:5px; }
        .welcome { text-align:center; padding: 11vh 1rem 4vh; }
        .welcome-logo { font-size:3rem; }
        .welcome h1 { font-size:2.2rem; margin:.5rem 0 .25rem; }
        .welcome p { color:var(--console-muted); margin-bottom:1.5rem; }
        .thinking { color:var(--console-muted); font-size:.8rem; display:flex; gap:5px; align-items:center; margin-bottom:.5rem; }
        .thinking span { margin-left:6px; }
        .sidebar-title { font-size:1.05rem; font-weight:750; }
        .sidebar-subtitle { color:var(--console-muted); font-size:.72rem; margin-bottom:1rem; }
        .sidebar-section { color:#737b87; font-size:.68rem; text-transform:uppercase; letter-spacing:.1em; margin:1.25rem 0 .5rem; }
        .conversation-card { padding:.5rem .65rem; border:1px solid transparent; border-radius:10px; margin:.18rem 0; }
        .conversation-card.active { background:#151820; border-color:#252a33; }
        .conversation-name { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; font-size:.8rem; }
        .conversation-meta { color:#666e7a; font-size:.64rem; }
        .api-status { padding:.55rem .7rem; border:1px solid var(--console-border); border-radius:10px; font-size:.75rem; margin-top:.75rem; }
        .api-ok { color:#86efac; }
        .api-missing { color:#fca5a5; }
        .example { border:1px solid var(--console-border); background:var(--console-panel); padding:.75rem .9rem; border-radius:12px; margin:.45rem 0; }
        div[data-testid="stChatMessage"] { background:transparent; padding-top:.5rem; padding-bottom:.5rem; }
        div[data-testid="stChatMessageContent"] { max-width: 850px; }
        .stButton > button, .stDownloadButton > button { border-radius:10px; border:1px solid var(--console-border); background:#11141a; }
        .stButton > button:hover { border-color:#414754; }
        textarea, input { border-radius:14px !important; }
        [data-testid="stChatInput"] { background:rgba(8,9,11,.92); }
        @media (max-width: 700px) {
            .block-container { padding-left:.7rem; padding-right:.7rem; }
            .header-status { display:none; }
            .welcome { padding-top:7vh; }
            .welcome h1 { font-size:1.75rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(
    conversations: list[dict],
    active_id: str,
    selected_model: str,
    models: list[str],
    api_active: bool,
) -> dict | None:
    with st.sidebar:
        st.markdown('<div class="sidebar-title">🤖 CONSOLE AI Chatbot</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-subtitle">Powered by Google Gemini & AI Architecture</div>', unsafe_allow_html=True)

        if st.button("＋  New Chat", use_container_width=True, type="primary"):
            return {"action": "new_chat"}

        st.markdown('<div class="sidebar-section">Conversations</div>', unsafe_allow_html=True)
        for conversation in conversations:
            cid = conversation["id"]
            title = escape(conversation.get("title", "New Conversation"))
            active_class = " active" if cid == active_id else ""
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(
                    f'<div class="conversation-card{active_class}"><div class="conversation-name">💬 {title}</div></div>',
                    unsafe_allow_html=True,
                )
                if st.button("Open", key=f"open_{cid}", use_container_width=True):
                    return {"action": "select_chat", "conversation_id": cid}
            with col2:
                if st.button("×", key=f"delete_{cid}", help="Delete conversation"):
                    return {"action": "delete_chat", "conversation_id": cid}

        st.markdown('<div class="sidebar-section">Model</div>', unsafe_allow_html=True)
        model = st.selectbox("Gemini model", models, index=models.index(selected_model), label_visibility="collapsed")
        if model != selected_model:
            return {"action": "set_model", "model": model}

        status_class = "api-ok" if api_active else "api-missing"
        status_text = "🟢 API Key Active" if api_active else "🔴 API Key Missing"
        st.markdown(f'<div class="api-status {status_class}">{status_text}</div>', unsafe_allow_html=True)
        st.caption("Your key is never shown in the interface.")
    return None


def render_message(message: dict, index: int) -> None:
    role = message.get("role", "assistant")
    avatar = "👤" if role == "user" else "🤖"
    with st.chat_message(role, avatar=avatar):
        st.markdown(message.get("content", ""))


def render_welcome() -> None:
    st.markdown(
        """
        <div class="welcome">
            <div class="welcome-logo">🤖</div>
            <h1>How can I help you today?</h1>
            <p>Ask CONSOLE AI anything—from coding and mathematics to science, writing, and study help.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    examples = [
        "Explain recursion in C",
        "Solve this mathematics problem step by step",
        "Write a Python program to sort an array",
        "Explain quantum mechanics simply",
        "Debug my code and explain the error",
        "Help me prepare for my semester exam",
    ]
    cols = st.columns(2)
    for i, example in enumerate(examples):
        with cols[i % 2]:
            if st.button(example, key=f"example_{i}", use_container_width=True):
                st.session_state.example_prompt = example
                st.rerun()
