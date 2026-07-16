import traceback
import uuid

import streamlit as st

from agent.react_agent import ReactAgent


# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="OpsPilot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ----------------------------
# Styles: minimal chat UI
# ----------------------------
st.markdown(
    """
<style>
    .stApp {
        background: #f7f7f8;
    }

    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stHeader"] {
        display: none !important;
    }

    #MainMenu,
    footer,
    header {
        visibility: hidden !important;
    }

    .block-container {
        max-width: 980px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    html, body, [class*="css"] {
        color: #111827;
    }

    section[data-testid="stSidebar"] {
        background: #ececf1;
        border-right: 1px solid #d9d9e3;
        min-width: 290px !important;
        max-width: 290px !important;
    }

    .sidebar-title {
        font-size: 1.08rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.9rem;
    }

    .main-title {
        font-size: 1.95rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
    }

    .sub-title {
        font-size: 0.98rem;
        color: #4b5563;
        line-height: 1.7;
        margin-bottom: 1.2rem;
    }

    .empty-wrap {
        text-align: center;
        padding-top: 9vh;
        color: #6b7280;
    }

    .empty-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.6rem;
    }

    .empty-desc {
        font-size: 1rem;
        color: #6b7280;
        line-height: 1.7;
    }

    div[data-testid="stChatMessage"] {
        background: transparent;
        border: none;
        padding-top: 0.3rem;
        padding-bottom: 0.3rem;
        margin-bottom: 0.35rem;
    }

    .history-tip {
        font-size: 0.85rem;
        color: #6b7280;
        line-height: 1.6;
        margin-top: 0.8rem;
    }

    .quick-label {
        font-size: 0.92rem;
        font-weight: 600;
        color: #4b5563;
        margin-bottom: 0.75rem;
    }

    .quick-question-note {
        font-size: 0.88rem;
        color: #6b7280;
        margin-bottom: 0.8rem;
    }

    hr {
        border-color: #e5e7eb;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 14px;
        border: 1px solid #d1d5db;
        background: #ffffff;
        color: #111827;
        font-weight: 500;
        padding: 0.62rem 0.85rem;
        box-shadow: none;
    }

    div.stButton > button:hover {
        background: #f3f4f6;
        border-color: #c7cdd4;
        color: #111827;
    }

    section[data-testid="stSidebar"] div.stButton > button {
        text-align: left !important;
        justify-content: flex-start !important;
        border-radius: 12px;
        border: 1px solid #d7d9df;
        background: #f8f8fb;
        color: #111827;
        padding: 0.72rem 0.85rem;
        margin-bottom: 0.35rem;
        font-size: 0.92rem;
        min-height: 48px;
    }

    section[data-testid="stSidebar"] div.stButton > button:hover {
        background: #ffffff;
        border-color: #bfc5cf;
    }

    .active-history {
        background: #ffffff;
        border: 1px solid #bfc5cf;
        border-radius: 12px;
        padding: 0.72rem 0.85rem;
        margin-bottom: 0.35rem;
        color: #111827;
        font-size: 0.92rem;
        font-weight: 600;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ----------------------------
# Session init
# ----------------------------
if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

if "conversations" not in st.session_state:
    first_id = str(uuid.uuid4())
    st.session_state["conversations"] = {
        first_id: {
            "title": "New chat",
            "messages": [],
        }
    }
    st.session_state["current_conversation_id"] = first_id

if "current_conversation_id" not in st.session_state:
    st.session_state["current_conversation_id"] = next(
        iter(st.session_state["conversations"])
    )

if "pending_prompt" not in st.session_state:
    st.session_state["pending_prompt"] = None


def get_current_conversation():
    conv_id = st.session_state["current_conversation_id"]
    return st.session_state["conversations"][conv_id]


def build_title_from_messages(messages: list[dict]) -> str:
    for msg in messages:
        if msg["role"] == "user" and msg["content"].strip():
            title = msg["content"].strip().replace("\n", " ")
            return title[:22] + ("..." if len(title) > 22 else "")
    return "New chat"


def create_new_conversation():
    new_id = str(uuid.uuid4())
    st.session_state["conversations"][new_id] = {
        "title": "New chat",
        "messages": [],
    }
    st.session_state["current_conversation_id"] = new_id
    st.session_state["pending_prompt"] = None


# ----------------------------
# Sidebar: chat history
# ----------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-title">OpsPilot</div>', unsafe_allow_html=True)

    if st.button("+ New chat", key="new_chat_btn"):
        create_new_conversation()
        st.rerun()

    st.markdown("---")

    conversation_ids = list(st.session_state["conversations"].keys())

    for cid in reversed(conversation_ids):
        title = st.session_state["conversations"][cid]["title"]
        display_title = title if title.strip() else "New chat"

        if cid == st.session_state["current_conversation_id"]:
            st.markdown(
                f'<div class="active-history">{display_title}</div>',
                unsafe_allow_html=True,
            )
        else:
            if st.button(display_title, key=f"history_{cid}"):
                st.session_state["current_conversation_id"] = cid
                st.session_state["pending_prompt"] = None
                st.rerun()

    st.markdown(
        '<div class="history-tip">Switch chats on the left. Ask questions on the right.</div>',
        unsafe_allow_html=True,
    )


# ----------------------------
# Main chat area
# ----------------------------
current_conv = get_current_conversation()
messages = current_conv["messages"]

st.markdown(
    """
    <div class="main-title">OpsPilot — Enterprise AIOps Agent</div>
    <div class="sub-title">
        Ops knowledge Q&amp;A, alert analysis, log/metric diagnosis, and operations reports.
    </div>
    """,
    unsafe_allow_html=True,
)

if len(messages) == 0:
    st.markdown(
        """
    <div class="empty-wrap">
        <div class="empty-title">What do you want to analyze today?</div>
        <div class="empty-desc">
            You can ask directly, for example:<br>
            Analyze anomalies for order-service in the last 1 hour
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="quick-label">Suggested prompts</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="quick-question-note">Click a question to start chatting.</div>',
        unsafe_allow_html=True,
    )

    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)

    with row1_col1:
        if st.button(
            "Analyze anomalies for order-service in the last 1 hour",
            key="quick_q_1",
        ):
            st.session_state["pending_prompt"] = (
                "Analyze anomalies for order-service in the last 1 hour"
            )
            st.rerun()

    with row1_col2:
        if st.button(
            "What are the main alerts for payment-service today?",
            key="quick_q_2",
        ):
            st.session_state["pending_prompt"] = (
                "What are the main alerts for payment-service today?"
            )
            st.rerun()

    with row2_col1:
        if st.button(
            "Generate an operations report for inventory-service this month",
            key="quick_q_3",
        ):
            st.session_state["pending_prompt"] = (
                "Generate an operations report for inventory-service this month"
            )
            st.rerun()

    with row2_col2:
        if st.button(
            "How should I troubleshoot high CPU usage?",
            key="quick_q_4",
        ):
            st.session_state["pending_prompt"] = (
                "How should I troubleshoot high CPU usage?"
            )
            st.rerun()

    st.markdown("---")


# ----------------------------
# Render current conversation
# ----------------------------
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ----------------------------
# Input handling
# ----------------------------
user_input = st.chat_input("Ask an ops question...")

if st.session_state["pending_prompt"]:
    prompt = st.session_state["pending_prompt"]
    st.session_state["pending_prompt"] = None
elif user_input:
    prompt = user_input
else:
    prompt = None


# ----------------------------
# Run agent (non-streaming via ReactAgent.run)
# ----------------------------
if prompt:
    current_conv = get_current_conversation()
    current_conv["messages"].append({"role": "user", "content": prompt})
    current_conv["title"] = build_title_from_messages(current_conv["messages"])

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        try:
            with st.spinner("Analyzing..."):
                full_response = st.session_state["agent"].run(prompt)
            placeholder.markdown(full_response)
        except Exception as e:
            traceback.print_exc()
            full_response = f"Runtime error: {type(e).__name__}: {e}"
            placeholder.error(full_response)

    current_conv["messages"].append({"role": "assistant", "content": full_response})
    current_conv["title"] = build_title_from_messages(current_conv["messages"])
