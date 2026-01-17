import streamlit as st
import mysql.connector
import pandas as pd
import time

from analytics.analytics import load_video_data_by_channel
from extraction.youtube_api import get_channel_id_by_name, sync_channel_to_db

from pages.tabs import (
    overview, performance, engagement, strategy,
    comparison, pricing, ai_growth, blogs
)

# ==============================
# 1. PAGE CONFIG & GLOBAL CSS
# ==============================
st.set_page_config(page_title="YTAI Analytics Dashboard", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    .stApp {
        background:radial-gradient(circle at bottom right, #0a2a43 50%, #04111d 75%, #000000 85%) !important ;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }

    /* Animation */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .main-content { animation: fadeInUp 0.6s ease-out forwards; }

    /* Header Styling */
    [data-testid="stHeader"] {
        background: rgba(13, 22, 31, 0.9) !important;
        backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(255,255,255,0.08);
    }

    .logo-text {
        font-weight: 900;
        font-size: 1.5rem;
        background: linear-gradient(90deg, #00e5ff, #007bff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
    }
    .logo-icon {
        width: 45px; height: 45px; border-radius: 18px; 
        background: linear-gradient(135deg,#00e5ff 0%, #007bff 100%);
        display: flex; align-items: center; justify-content: center;
        flex-direction: row; font-size: 2.5rem; color: white; font-weight: 800;
        box-shadow: 0 10px 30px rgba(0, 229, 255, 0.3);
            }
        .logo-container { display: flex; align-items: center; gap: 10px; }

    /* Fixed Navigation Buttons - Prevention of Wrapping */
    div.stButton > button {
        background: transparent !important;
        color: #94a3b8 !important;
        margin-top: 19px !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        transition: all 0.3s ease !important;
        height: 48px !important;
        white-space: nowrap !important; /* CRITICAL: Prevents text splitting */
    }
    
    div.stButton > button:hover {
        border-color: #00e5ff !important;
        color: white !important;
        background: rgba(0, 229, 255, 0.05) !important;
    }
            

    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #00e5ff, #007bff) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0, 229, 255, 0.3) !important;
    }
            div.stButton > button[kind="secondary"]{
            background:linear-gradient(180deg, #5d779c, #1e293b)!important;
            color: white !important;
            border: none !important;
            box-shadow: 0 4px 15px rgba(0, 229, 255, 0.3) !important;
            }

    /* Search Bar Input Styling */
    div[data-testid="stTextInput"] > div {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 50px !important;
    }
    
    /* Hide Default Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ==============================
# 2. STATE & DATA LOGIC
# ==============================
if "active_tab" not in st.session_state: st.session_state.active_tab = "overview"
if "df" not in st.session_state: st.session_state.df = None
if "channel_id" not in st.session_state: st.session_state.channel_id = None
if "search_value" not in st.session_state: st.session_state.search_value = ""

# Redirect sync from login page
if "pending_channel" in st.session_state and st.session_state.pending_channel:
    st.session_state.search_value = st.session_state.pending_channel
    st.session_state.pending_channel = None

@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host="localhost", user=st.secrets["database"]["user"], password=st.secrets["database"]["password"], database=st.secrets["database"]["name"]
    )

@st.cache_data
def load_channels():
    conn = get_connection()
    return pd.read_sql("SELECT * FROM channels_detailed", conn)

def auto_search(channel_name: str):
    channels_df = load_channels()
    st.session_state.df = None
    with st.spinner(f"Fetching '{channel_name}'..."):
        row = channels_df[channels_df["channel_name"].str.lower().str.strip() == channel_name.lower().strip()]
        if not row.empty:
            cid = row.iloc[0]["channel_id"]
            st.session_state.channel_id = cid
            st.session_state.df = load_video_data_by_channel(cid)
            return
        
        api_key = st.secrets["google"]["api_key"]
        yt_id = get_channel_id_by_name(api_key, channel_name)
        if yt_id:
            if sync_channel_to_db(get_connection(), api_key, yt_id):
                st.cache_data.clear()
                st.session_state.channel_id = yt_id
                st.session_state.df = load_video_data_by_channel(yt_id)
                return
        st.error("Channel not found.")

# ==============================
# 3. HEADER & NAV
# ==============================
header_row = st.container()
with header_row:
    l_col, s_col, u_col = st.columns([1.5, 3, 1.2], vertical_alignment="center")
    with l_col:
        st.markdown('<div class="logo-container"> <div class="logo-icon">▶</div><div class="logo-text"> YOUTUBE ANALYTICS</div></div> ', unsafe_allow_html=True)
    with s_col:
        search_query = st.text_input("", placeholder="🔍 Search any YouTube Channel...", value=st.session_state.search_value, label_visibility="collapsed")
    with u_col:
        u_name = st.session_state.user.get('name', 'User') if st.session_state.get('user') else 'Guest'
        if u_name == 'Guest':
            st.markdown(
                f'<div style="display:flex;justify-content:flex-end;gap:20px;"><div style="max-width:180px;word-break:break-word;text-align:right;color:white;"><b>{u_name}</b></div><a href="updated_youtube\authentication.py" style="color:black;text-decoration:none;background:linear-gradient(135deg,rgb(230 86 18) 10%,rgb(222,24,24) 90%);padding:7px 15px;border-radius:5px;white-space:nowrap;">Login</a></div>',
                unsafe_allow_html=True
            )
        else:   
            st.markdown(
                f'<div style="display:flex;justify-content:flex-end;gap:20px;"><div style="max-width:180px;word-break:break-word;text-align:right;color:white;"><b>{u_name}</b></div><a href="/?logout=true" style="color:black;text-decoration:none;background:linear-gradient(135deg,rgb(230 86 18) 10%,rgb(222,24,24) 90%);padding:7px 15px;border-radius:5px;white-space:nowrap;">Logout</a></div>',
                    unsafe_allow_html=True
                        )


if search_query and search_query != st.session_state.search_value:
    st.session_state.search_value = search_query
    auto_search(search_query)
    st.rerun()

if st.session_state.search_value and st.session_state.df is None:
    auto_search(st.session_state.search_value)

# Tab Bar
tabs_list = [
    ("overview", "📊 Overview"), ("performance", "📈 Performance"), ("engagement", "💬 Engagement"),
    ("strategy", "🎯 Strategy"), ("comparison", "⚖️ Compare"), ("pricing", "💰 Earnings"),
    ("ai_growth", "🤖 AI Growth"), ("blogs", "📰 Blogs")
]

st.markdown('<div style="margin-top:15px;"></div>', unsafe_allow_html=True)
t_cols = st.columns(len(tabs_list))
for i, (key, label) in enumerate(tabs_list):
    is_active = st.session_state.active_tab == key
    if t_cols[i].button(label, key=f"nav_{key}", type="primary" if is_active else "secondary", use_container_width=True):
        st.session_state.active_tab = key
        st.rerun()

# ==============================
# 4. CONTENT RENDER
# ==============================
st.markdown('<div class="main-content">', unsafe_allow_html=True)
df = st.session_state.df
channel_id = st.session_state.channel_id
channels_df = load_channels()

if df is not None:
    tab = st.session_state.active_tab
    if tab == "overview": overview.render(df, channel_id, channels_df)
    elif tab == "performance": performance.render(df)
    elif tab == "engagement": engagement.render(df)
    elif tab == "strategy": strategy.render(df)
    elif tab == "comparison": comparison.render(st.session_state.search_value, channels_df, get_connection())
    elif tab == "pricing": pricing.render(df)
    elif tab == "ai_growth": ai_growth.render(df, st.session_state.search_value)
    elif tab == "blogs": blogs.render(df)
else:
    st.markdown('<div style="text-align:center; padding:100px; color:#64748b;"><h2>Search a channel to begin analysis</h2></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)