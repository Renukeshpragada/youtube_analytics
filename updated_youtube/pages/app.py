import streamlit as st
import mysql.connector
import pandas as pd
import altair as alt
from analytics.analytics import load_video_data_by_channel
from extraction.youtube_api import get_channel_id_by_name, sync_channel_to_db

# Import Tab Modules
from pages.tabs import (overview, performance, engagement, strategy, 
                        comparison, pricing, ai_growth, blogs)

# ==============================
# 1. SETUP & AUTH
# ==============================
if "authenticated" not in st.session_state:
    st.switch_page("authentication.py")

st.set_page_config(page_title="YouTube Analytics Dashboard", layout="wide")

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

# ==============================
# 2. DATABASE & DATA LOADING
# ==============================
@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host="localhost", user="yt_user", 
        password="StrongPass@123", database="youtube_analytics"
    )

conn = get_connection()

@st.cache_data
def load_channels(_conn):
    # ✅ Fetch all columns so metaata like subscribers is available
    return pd.read_sql("SELECT * FROM channels_detailed", _conn)

channels_df = load_channels(conn)
# ==============================
# 3. SIDEBAR & SEARCH
# ==============================
with st.sidebar:
    st.markdown("### User Profile")
    if "user" in st.session_state:
        st.write(f"Logged in as: **{st.session_state.user['name']}**")
    if st.button("Logout", width="stretch"):
        st.session_state.clear()
        st.switch_page("authentication.py")

st.title("YouTube Analytics & Insights Dashboard")

my_channel = st.session_state.get("user_yt_channel")
default_name = my_channel["channel_name"] if my_channel else ""

st.markdown("## 🔍 Channel Lookup")
channel_input = st.text_input("Enter YouTube Channel Name", value=default_name)

if not channel_input.strip():
    st.info("👆 Enter a YouTube channel name to view analytics.")
    st.stop()

# ==============================
# 4. AUTO-SYNC LOGIC
# ==============================
channel_row = channels_df[channels_df["channel_name"].str.lower() == channel_input.lower()]

if channel_row.empty:
    st.markdown(f'<div class="custom-alert">⚠️ "{channel_input}" not in local database. Syncing all videos...</div>', unsafe_allow_html=True)
    with st.spinner("Please wait, fetching metadata..."):
        api_key = st.secrets["google"]["api_key"]
        target_id = get_channel_id_by_name(api_key, channel_input)
        if target_id and sync_channel_to_db(conn, api_key, target_id):
            st.cache_data.clear()
            st.rerun()
        else:
            st.error("Channel not found or Sync failed.")
            st.stop()

# Load Data
channel_id = channel_row.iloc[0]["channel_id"]
df = load_video_data_by_channel(channel_id)

# ==============================
# 5. TABS DEFINITION
# ==============================
t1, t2, t3, t4, t5, t6, t7, t8 = st.tabs([
    "Overview", "Performance", "Engagement", "Strategy", "Comparison", "Earnings", "AI Growth", "Blogs"
])

# Pass df, channel_id, and channels_df to the overview tab
with t1: overview.render(df, channel_id, channels_df)
with t2: performance.render(df)
with t3: engagement.render(df)
with t4: strategy.render(df)
with t5: comparison.render(channel_input, channels_df, conn)
with t6: pricing.render(df)
with t7: ai_growth.render(df, channel_input)
with t8: blogs.render(df)