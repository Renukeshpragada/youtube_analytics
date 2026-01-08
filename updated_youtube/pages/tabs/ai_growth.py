import streamlit as st
import requests
import pandas as pd
import json

# ==============================
# GROQ AI CONFIGURATION
# ==============================

def ask_groq(prompt, system_prompt="You are a helpful YouTube growth strategist assistant."):
    """
    Local Ollama AI call
    No API keys. No internet. No auth.
    """

    OLLAMA_URL = "http://localhost:11434/api/chat"
    MODEL_NAME = "tinyllama"  # change ONLY if needed

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        if response.status_code != 200:
            return f"❌ Ollama Error {response.status_code}: {response.text}"

        data = response.json()

        if "message" in data and "content" in data["message"]:
            return data["message"]["content"]

        return f"❌ Unexpected Ollama response format:\n{data}"

    except requests.exceptions.ConnectionError:
        return "❌ **Ollama is not running**"


def build_channel_context(df, channel_name):
    """Build context about the channel for AI"""
    top = df.sort_values("views", ascending=False).head(5)
    avg_views = int(df["views"].mean())
    avg_likes = int(df["likes"].mean())
    avg_engagement = round(df["engagement_rate"].mean(), 4)
    
    ctx = f"""
Channel Name: {channel_name}
Total Videos: {len(df)}
Average Views: {avg_views:,}
Average Likes: {avg_likes:,}
Average Engagement Rate: {avg_engagement}

Top 5 Performing Videos:
"""
    for idx, (_, r) in enumerate(top.iterrows(), 1):
        ctx += f"{idx}. {r['title']} - {r['views']:,} views, {r['likes']:,} likes\n"
    
    return ctx

def generate_title(df, channel_name, topic=""):
    """Generate YouTube video title suggestions"""
    context = build_channel_context(df, channel_name)
    prompt = f"""
{context}

Based on this channel's performance data, generate 5 compelling YouTube video title suggestions.
{"Focus on the topic: " + topic if topic else "Create titles that match the channel's successful content style."}

Requirements:
- Titles should be 50-60 characters
- Include power words that increase CTR
- Match the style of top-performing videos
- Be specific and curiosity-driven

Format as a numbered list.
"""
    return ask_groq(prompt, "You are an expert YouTube title optimizer.")

def generate_description(df, channel_name, title=""):
    """Generate YouTube video description"""
    context = build_channel_context(df, channel_name)
    prompt = f"""
{context}

{"Generate a YouTube video description for this title: " + title if title else "Generate a YouTube video description template"}

Requirements:
- First 125 characters should hook viewers and include keywords
- Include timestamps if applicable
- Add relevant hashtags
- Include call-to-action
- Match the channel's style

Provide a complete description.
"""
    return ask_groq(prompt, "You are an expert YouTube description writer.")

def generate_content(df, channel_name, topic=""):
    """Generate video content outline"""
    context = build_channel_context(df, channel_name)
    prompt = f"""
{context}

{"Create a detailed content outline for a video about: " + topic if topic else "Create a content outline based on the channel's successful videos"}

Requirements:
- Hook (first 15 seconds)
- Main points with timestamps
- Key takeaways
- Call-to-action
- Match the channel's successful content structure

Provide a structured outline.
"""
    return ask_groq(prompt, "You are an expert YouTube content strategist.")

def get_suggestions(df, channel_name):
    """Get growth suggestions based on channel data"""
    context = build_channel_context(df, channel_name)
    prompt = f"""
{context}

Analyze this channel's data and provide specific, actionable growth suggestions.

Focus on:
1. Content strategy improvements
2. Upload timing optimization
3. Engagement enhancement
4. Title and thumbnail improvements
5. Audience growth tactics

Provide 5-7 specific recommendations based on the actual data.
"""
    return ask_groq(prompt, "You are a YouTube growth expert who provides data-driven advice.")

def render(df, channel_input):
    st.markdown("""
    <div class="ai-growth-header">
        <h1 class="ai-main-title">🤖 AI Growth Assistant</h1>
        <p class="ai-subtitle">Powered by Groq AI - Get intelligent insights and content suggestions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ==============================
    # GENERATOR OPTIONS
    # ==============================
    st.markdown("### 🛠️ Content Generators")
    
    gen_col1, gen_col2, gen_col3, gen_col4 = st.columns(4)
    
    with gen_col1:
        title_btn = st.button("📝 Title Generator", use_container_width=True, key="title_gen")
    with gen_col2:
        desc_btn = st.button("📄 Description Generator", use_container_width=True, key="desc_gen")
    with gen_col3:
        content_btn = st.button("📋 Content Generator", use_container_width=True, key="content_gen")
    with gen_col4:
        suggest_btn = st.button("💡 Get Suggestions", use_container_width=True, key="suggest_gen")
    
    # ==============================
    # GENERATOR OUTPUTS
    # ==============================
    if title_btn:
        with st.spinner("Generating title suggestions..."):
            topic = st.text_input("Enter topic (optional)", key="title_topic", placeholder="e.g., Python tutorial")
            if st.button("Generate", key="title_generate"):
                result = generate_title(df, channel_input, topic)
                st.markdown(f"<div class='ai-result-box'><h4>📝 Title Suggestions:</h4><pre class='ai-result-text'>{result}</pre></div>", unsafe_allow_html=True)
    
    if desc_btn:
        with st.spinner("Generating description..."):
            title = st.text_input("Enter video title (optional)", key="desc_title", placeholder="e.g., Learn Python in 10 Minutes")
            if st.button("Generate", key="desc_generate"):
                result = generate_description(df, channel_input, title)
                st.markdown(f"<div class='ai-result-box'><h4>📄 Video Description:</h4><pre class='ai-result-text'>{result}</pre></div>", unsafe_allow_html=True)
    
    if content_btn:
        with st.spinner("Generating content outline..."):
            topic = st.text_input("Enter video topic (optional)", key="content_topic", placeholder="e.g., Machine Learning Basics")
            if st.button("Generate", key="content_generate"):
                result = generate_content(df, channel_input, topic)
                st.markdown(f"<div class='ai-result-box'><h4>📋 Content Outline:</h4><pre class='ai-result-text'>{result}</pre></div>", unsafe_allow_html=True)
    
    if suggest_btn:
        with st.spinner("Analyzing your channel and generating suggestions..."):
            result = get_suggestions(df, channel_input)
            st.markdown(f"<div class='ai-result-box'><h4>💡 Growth Suggestions:</h4><pre class='ai-result-text'>{result}</pre></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==============================
    # CHATBOT SECTION
    # ==============================
    st.markdown("### 💬 AI Chatbot")
    st.markdown("Ask me anything about growing your YouTube channel!")
    
    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = []
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.ai_messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-ai-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    with st.form("ai_chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_query = st.text_input(
                "",
                placeholder="Ask: How can I improve my video titles? What's the best upload time?",
                label_visibility="collapsed",
                key="chat_input"
            )
        with col2:
            submitted = st.form_submit_button("Send ➤", use_container_width=True)
    
    if submitted and user_query:
        st.session_state.ai_messages.append({"role": "user", "content": user_query})
        
        with st.spinner("AI is thinking..."):
            context = build_channel_context(df, channel_input)
            system_prompt = f"""You are an expert YouTube growth strategist. Use this channel data to provide specific, actionable advice:

{context}

Always reference the actual data when giving advice. Be specific and practical."""
            
            ai_response = ask_groq(user_query, system_prompt)
            st.session_state.ai_messages.append({"role": "ai", "content": ai_response})
        
        st.rerun()