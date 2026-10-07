"""Streamlit chat interface for the REST API & Webhook Troubleshooter.

Run from the project folder:   streamlit run app/app.py

This file only DISPLAYS things. All the matching logic lives in src/chatbot.py.
"""
import os
import sys
from pathlib import Path

import streamlit as st

# Streamlit runs this file from the app/ folder, so we add the project folder to
# Python's search path (so "from src..." works) and make it the working folder
# (so "data/faqs.csv" is found).
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))
os.chdir(ROOT)

from src.chatbot import FAQChatbot  # noqa: E402  (must come after the path lines above)

EXAMPLES = [
    "What does 502 Bad Gateway mean?",
    "Why is my webhook not firing?",
    "Why am I getting a CORS error in the browser?",
    "How do I send a Bearer token?",
    "429",
]
WELCOME = (
    "Hi! I can help with REST API and webhook problems: status codes, "
    "authentication, CORS, rate limits, webhooks, and debugging tools. "
    "Ask me a question, or pick an example from the sidebar."
)

st.set_page_config(page_title="API & Webhook Troubleshooter", page_icon="🛠️", layout="centered")


@st.cache_resource(show_spinner="Loading the chatbot...")
def load_bot() -> FAQChatbot:
    """Build the chatbot once (loading spaCy and the FAQs is slow) and reuse it."""
    return FAQChatbot()


bot = load_bot()

# ----- Session state: what Streamlit remembers between reruns -----
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": WELCOME}]
if "pending" not in st.session_state:
    st.session_state.pending = None


def queue_question(question: str) -> None:
    """Called when an example or suggestion button is clicked."""
    st.session_state.pending = question


def clear_chat() -> None:
    st.session_state.messages = [{"role": "assistant", "content": WELCOME}]
    st.session_state.pending = None


# ----- Sidebar -----
with st.sidebar:
    st.header("🛠️ API & Webhook Troubleshooter")
    st.write(
        "Ask about HTTP status codes, authentication, CORS, rate limits, "
        "webhooks, and debugging tools."
    )
    st.subheader("Try an example")
    for example in EXAMPLES:
        st.button(
            example,
            key=f"example_{example}",
            on_click=queue_question,
            args=(example,),
            use_container_width=True,
        )
    st.divider()
    show_details = st.checkbox("Show match details", value=False)
    st.button("Clear chat", on_click=clear_chat, use_container_width=True)
    with st.expander("How it works"):
        st.markdown(
            "1. **Preprocess** your question with spaCy (clean, tokenize, remove stopwords, lemmatize)\n"
            "2. **Match** it against the FAQ questions with TF-IDF and cosine similarity\n"
            "3. **Answer** with the best match, or say *not sure* and suggest similar questions"
        )
    st.caption(f"{bot.total_faqs} FAQs · {len(bot.matcher.df)} question wordings")

# ----- Main page -----
st.title("REST API & Webhook Troubleshooter")
st.caption("An FAQ chatbot built with spaCy, TF-IDF and cosine similarity.")

# A question comes from the chat box, or from a button click (stored in "pending").
prompt = st.chat_input("Ask about an API error, webhook, CORS...")
question = prompt or st.session_state.pending
st.session_state.pending = None

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    reply = bot.get_response(question)
    st.session_state.messages.append(
        {"role": "assistant", "content": reply["answer"], "reply": reply}
    )

# Draw the whole conversation.
last = len(st.session_state.messages) - 1
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        reply = msg.get("reply")
        if reply and reply["found"]:
            st.caption(f"Category: {reply['category']}")
            st.markdown(f"[📖 Read the source documentation]({reply['source_url']})")
        if reply and show_details:
            st.caption(f"match score {reply['score']:.2f} · FAQ: {reply['faq_id'] or 'none'}")
        # Only the newest answer shows clickable suggestions.
        if reply and reply["suggestions"] and i == last:
            st.write("Related questions:" if reply["found"] else "Did you mean:")
            for j, suggestion in enumerate(reply["suggestions"]):
                st.button(
                    suggestion,
                    key=f"suggestion_{i}_{j}",
                    on_click=queue_question,
                    args=(suggestion,),
                    use_container_width=True,
                )

st.divider()
st.caption(
    "Answers are short summaries of MDN and provider documentation. "
    "Always check the source link for full details."
)