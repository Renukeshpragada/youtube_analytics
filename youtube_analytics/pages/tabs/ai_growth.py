import streamlit as st
import requests
import pandas as pd
import time
import os

GROQ_API_KEY = st.secrets["groq"]["GROQ_API_KEY"]
GROQ_URL = st.secrets["groq"]["GROQ_URL"]
MODEL_NAME = st.secrets["groq"]["MODEL_NAME"]


def ask_ai(prompt, mode="chat", context_data=""):
    system_prompts = {
        "chat": (
            "You are a senior YouTube Growth Strategist.\n"
            "Respond with a structured, point-by-point analysis.\n"
            "No greetings. No filler. No explanations.\n"
            "Use Markdown. Bold key insights."
        ),

        "title": (
            "You are a viral YouTube title generator.\n"
            "Generate EXACTLY 5 titles.\n"
            "Each title must be on a new bullet point.\n"
            "No intro text. No numbering explanation.\n"
            "Only bullet points.\n"
            "Titles must be concise, high-CTR, curiosity-driven."
        ),

        "script": (
            "You are a YouTube script architect.\n"
            "Return a 3-act structure:\n"
            "- Act 1: Hook\n"
            "- Act 2: Core Value\n"
            "- Act 3: CTA\n"
            "Use bullet points only. No paragraphs."
        ),

        "analytics": (
            "You are a YouTube analytics expert.\n"
            "Convert metrics into insights.\n"
            "Each insight must be a bullet point.\n"
            "Bold important numbers or trends."
        ),

        "growth": (
            "You are a YouTube growth hacker.\n"
            "List actionable growth tactics.\n"
            "Each tactic must be one bullet point.\n"
            "No motivational language. Only actions."
        )
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": system_prompts.get(mode)
            },
            {
                "role": "user",
                "content": f"Context:\n{context_data}\n\nTask:\n{prompt}"
            }
        ],
        "temperature": 0.6,
        "max_tokens": 350
    }

    try:
        r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    except Exception as e:
        return "❌ AI service unavailable. Please try again."

# ================================================
# 2. PERMANENT CSS (RADIAL & LOCKED LAYOUT)
# ================================================
def inject_stable_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
        
        /* 1. FORCE RADIAL BACKGROUND - CANNOT BE OVERRIDDEN */
        
        
        .stApp {
              background:radial-gradient(circle at bottom right, #0a2a43 50%, #04111d 75%, #000000 85%) !important ;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }

        /* 2. HEADERS */
        .ai-hero-header { text-align: center; margin: 20px 0 30px 80px; }
        .ai-hero-header h1 { font-size: 3rem !important; font-weight: 800 !important; color: white !important; letter-spacing: -2px !important; margin: 0; }
        .ai-hero-header p { color: #94a3b8 !important; font-size: 1.2rem !important; font-weight: 600; }

        /* 3. NAVIGATION */
        div.stButton > button {
            background: rgba(255, 255, 255, 0.03) !important;
            color: #94a3b8 !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            transition: 0.3s;
        }
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #00e5ff 0%, #007bff 100%) !important;
            color: white !important;
            box-shadow: 0 0 20px rgba(0, 229, 255, 0.3) !important;
            border: none !important;
            
            
        }

        /* 4. LOCKED CHAT RENDERING (NO FLICKER) */
        .yt-chat-viewport { display: flex; flex-direction: column; gap: 35px; width: 90%;  }

        /* User Message: Strictly Far Right */
        .yt-user-row { width: 90%; display: flex !important; justify-content: flex-end !important; margin-bottom: 10px; }
        .yt-user-bubble {
            background: #1e293b !important;
            color: white !important;
            padding: 15px 25px !important;
            border-radius: 24px 24px 4px 24px !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            max-width: 60% !important;
            font-weight: 600 !important;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3) !important;
        }

        /* AI Message: Strictly Far Left Document Style */
        .yt-ai-row { width: 70%; display: flex !important; justify-content: flex-start; margin-left:130px !important; }
        .yt-ai-report {
            background: rgba(13, 22, 31, 0.6) !important;
            backdrop-filter: blur(12px) !important;
            padding: 35px !important;
            border-radius: 20px !important;
            border-left: 5px solid #00e5ff !important;
            max-width: 80% !important;
            line-height: 1.8 !important;
            color: #d1d5db !important;
            font-size: 1.05rem !important;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5) !important;
            margin-left:60px;
        }
        .yt-ai-report b, .yt-ai-report strong { color: #00e5ff !important; font-weight: 800 !important; }

        /* 5. VISIBLE INPUT HUB */
        [data-testid="stChatInput"] {
            background-color: #0d161f !important;
            border: 1px solid #1e293b !important;
            border-radius: 16px !important;
            box-shadow: 0 -10px 50px rgba(0,0,0,0.6) !important;
        }
        [data-testid="stChatInput"] textarea { color: white !important; font-size: 1.1rem !important;
                }
                [data-testid="stChatInput"] {
                width:750px;
                display:flex;
                margin-left:170px;
                height:60px;
                align-items: center;
                justify-content:center;
               background: linear-gradient(135deg, #01050a59, #2b2d2d1f) !important;
                }

    </style>
    """, unsafe_allow_html=True)

# ================================================
# 3. RENDER LOGIC
# ================================================
def render(df, channel_input):
    inject_stable_css()

    if "ai_chat_history" not in st.session_state: st.session_state.ai_chat_history = []
    if "active_mode" not in st.session_state: st.session_state.active_mode = "chat"
    
    ctx = f"Channel: {channel_input}"

    # --- TOP HEADER ---
    st.markdown("""
    <div class="ai-hero-header">
        <h1>AI Growth Assistant</h1>
        <p>Analyze your channel and scale content faster</p>
    </div>
    """, unsafe_allow_html=True)

    # --- NAVIGATION TABS ---
    nav_tabs = [("chat", "💬 Chat"), ("title", "🚀 Titles"), ("script", "📄 Scripts"), ("analytics", "📊 Analytics"), ("growth", "📈 Growth")]
    cols = st.columns(len(nav_tabs))
    for i, (key, label) in enumerate(nav_tabs):
        with cols[i]:
            if st.button(label, key=f"btn_{key}", use_container_width=True, 
                         type="primary" if st.session_state.active_mode == key else "secondary"):
                st.session_state.active_mode = key
                st.rerun()

    # --- THE CHAT HUB (PERSISTENT SCROLL) ---
    st.markdown("<br>", unsafe_allow_html=True)
    chat_box = st.container(height=540, width=1200,border=False)

    with chat_box:
        if not st.session_state.ai_chat_history:
            # Landing Screen
            st.markdown("<div style='text-align:center;padding-top:200px; padding-left:250px;'><h2>How can I help you grow today?</h2><p style='color:#64748b;'>Choose a tool above or start typing below.</p></div>", unsafe_allow_html=True)
            
        else:
            # LOCKED HTML RENDERING (Prevents the 2-second state reset)
            for m in st.session_state.ai_chat_history:
                if m["role"] == "user":
                    st.markdown(f'<div class="yt-user-row"><div class="yt-user-bubble">{m["content"]}</div></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="yt-ai-row"><div class="yt-ai-report">{m["content"]}</div></div>', unsafe_allow_html=True)

    # --- INPUT HUB ---
    st.markdown("<br>", unsafe_allow_html=True)
    _, input_col, _ = st.columns([1, 6, 1])
    with input_col:
        user_query = st.chat_input("Ask a growth coach...")
    
    if user_query:
        trigger_chat(user_query, ctx)

def trigger_chat(query, ctx):
    st.session_state.ai_chat_history.append({"role": "user", "content": query})
    with st.spinner("AI Processing..."):
        response = ask_ai(query, mode=st.session_state.active_mode, context_data=ctx)
        st.session_state.ai_chat_history.append({"role": "assistant", "content": response})
    st.rerun()