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

# ==================================================
# PAGE CONFIG + CSS
# ==================================================
st.set_page_config(page_title="YouTube Analytics", layout="wide")

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

# ==================================================
# SESSION STATE INIT
# ==================================================

# ==================================================
# SESSION STATE INITIALIZATION (CRITICAL)
# ==================================================
# ==============================
# SESSION STATE INITIALIZATION
# ==============================

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "overview"

if "df" not in st.session_state:
    st.session_state.df = None

if "channel_id" not in st.session_state:
    st.session_state.channel_id = None

if "search_value" not in st.session_state:
    st.session_state.search_value = ""

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = None



# ==================================================
# DATABASE
# ==================================================
@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="yt_user",
        password="StrongPass@123",
        database="youtube_analytics"
    )

conn = get_connection()

@st.cache_data
def load_channels():
    return pd.read_sql("SELECT * FROM channels_detailed", conn)

channels_df = load_channels()

# ==================================================
# HANDLE LOGIN / LOGOUT
# ==================================================
qp = st.query_params

if qp.get("login") == "true":
    st.switch_page("authenticator.py")

if qp.get("logout") == "true":
    st.session_state.clear()
    st.rerun()

# ==================================================
# HEADER (LOGO + TITLE + LOGIN/LOGOUT ONLY)
# ==================================================
user_name = (
    st.session_state.user.get("name")
    if st.session_state.authenticated and st.session_state.user
    else ""
)

st.markdown("""
<div class="app-header">
    <div class="header-left">
        <div class="header-logo">▶</div>
        <div class="header-title">YouTube Analytics</div>
    </div>
    <div class="header-right">
""", unsafe_allow_html=True)


# ==================================================
# SEARCH INPUT (NOT IN HEADER)
# ==================================================
search = st.text_input(
    "",
    placeholder="Enter YouTube Channel Name or ID...",
    label_visibility="collapsed",
    value=st.session_state.search_value
)


# ==================================================
# AUTO SEARCH LOGIC
# ==================================================
def auto_search(channel_name: str):
    global channels_df   # 🔴 IMPORTANT

    st.session_state.df = None
    st.session_state.channel_id = None

    with st.spinner("Fetching data, please wait..."):
        time.sleep(0.4)

        # ==========================
        # 1️⃣ SEARCH IN LOCAL DB
        # ==========================
        row = channels_df[
            channels_df["channel_name"].str.lower().str.strip()
            == channel_name.lower().strip()
        ]

        if not row.empty:
            cid = row.iloc[0]["channel_id"]
            st.session_state.channel_id = cid
            st.session_state.df = load_video_data_by_channel(cid)
            return

        # ==========================
        # 2️⃣ SEARCH VIA YOUTUBE API
        # ==========================
        api_key = st.secrets["google"]["api_key"]
        yt_id = get_channel_id_by_name(api_key, channel_name)

        if not yt_id:
            st.error("❌ Channel not found on YouTube.")
            return

        if sync_channel_to_db(conn, api_key, yt_id):
            # Clear cache and reload channels globally
            st.cache_data.clear()
            channels_df = load_channels()

            row = channels_df[
                channels_df["channel_name"].str.lower().str.strip()
                == channel_name.lower().strip()
            ]

            if not row.empty:
                cid = row.iloc[0]["channel_id"]
                st.session_state.channel_id = cid
                st.session_state.df = load_video_data_by_channel(cid)
                return

        st.error("❌ Channel sync failed. Please try again.")

# Trigger auto search only when value changes
if search and search != st.session_state.search_value:
    st.session_state.search_value = search
    auto_search(search)
if (
    st.session_state.search_value
    and st.session_state.df is None
    ):
    auto_search(st.session_state.search_value)


# ==================================================
# TABS (SAME PAGE)
# ==================================================
tabs = [
    ("overview", "📊 Overview"),
    ("performance", "📈 Performance"),
    ("engagement", "💬 Engagement"),
    ("strategy", "🎯 Strategy"),
    ("comparison", "⚖️ Comparison"),
    ("pricing", "💰 Earnings"),
    ("ai_growth", "🤖 AI Growth"),
    ("blogs", "📰 Blogs"),
]

cols = st.columns(len(tabs))
for i, (key, label) in enumerate(tabs):
    if cols[i].button(label, key=f"tab_{key}"):
        st.session_state.active_tab = key

st.markdown("<div class='tabs-underline'></div>", unsafe_allow_html=True)

# ==================================================
# TAB CONTENT
# ==================================================
def need_channel():
    st.warning("Enter a YouTube channel name to view analytics.")

df = st.session_state.df
channel_id = st.session_state.channel_id
tab = st.session_state.active_tab

if tab == "overview":
    overview.render(df, channel_id, channels_df) 

elif tab == "performance":
    performance.render(df) 

elif tab == "engagement":
    engagement.render(df) 

elif tab == "strategy":
    strategy.render(df) 
elif tab == "comparison":
    comparison.render(
        st.session_state.search_value,
        channels_df,
        conn
    ) 

elif tab == "pricing":
    pricing.render(df)

elif tab == "ai_growth":
    ai_growth.render(df, st.session_state.search_value) 

elif tab == "blogs":
    blogs.render(df) 
