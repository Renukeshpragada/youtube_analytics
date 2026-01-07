import streamlit as st
import requests
import pandas as pd

OLLAMA_URL = "http://localhost:11434/api/generate"

def ask_ollama(prompt):
    r = requests.post(
        OLLAMA_URL,
        json={
            "model": "tinyllama",
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )
    return r.json()["response"]

def build_context(df, channel_name):
    top = df.sort_values("views", ascending=False).head(5)

    ctx = f"""
You are a YouTube growth strategist.

Channel name: {channel_name}
Total videos: {len(df)}
Average views: {int(df["views"].mean())}

Top videos:
"""
    for _, r in top.iterrows():
        ctx += f"- {r['title']} ({r['views']} views)\n"

    ctx += """
Give specific, data-backed advice.
No generic tips.
"""
    return ctx

def render(df, channel_input):

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # -----HERO --------
    if len(st.session_state.messages) == 0:
        st.markdown(
            f"""
            <div class="hero">
                <h1>AI Channel Growth Assistant</h1>
                <p>Welcome, <b>{channel_input}</b></p>
            </div>
            """,
            unsafe_allow_html=True
        )    #  CHAT WINDoW 
    chat_html = "<div class='chat-outer'><div class='chat-window'>"

    for msg in st.session_state.messages:
        role_class = "user" if msg["role"] == "user" else "ai"
        chat_html += f"<div class='bubble {role_class}'>{msg['content']}</div>"

    chat_html += "</div></div>"
    st.markdown(chat_html, unsafe_allow_html=True)
    st.markdown("""
    <script>
    const chat = document.querySelector('.chat-window');
    if (chat) {
        chat.scrollTop = chat.scrollHeight;
    }
    </script>
    """, unsafe_allow_html=True)

    # --INPUT (FORM = FIX) ----
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([8, 1])  # input-wier, button smaller
        with col1:
            user_input = st.text_input(
                "",
                placeholder="Ask how to grow your channel…",
                label_visibility="collapsed"
            )
        with col2:
            submitted = st.form_submit_button("Send",key="send_btn")
    if submitted and user_input:
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )
        with st.spinner("Thinking..."):
            prompt = build_context(df, channel_input) + f"\nUser: {user_input}"
            reply = ask_ollama(prompt)
        st.session_state.messages.append(
            {"role": "ai", "content": reply}
        )
        st.rerun()