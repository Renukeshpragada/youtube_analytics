import streamlit as st
import mysql.connector
import pandas as pd

from analytics.analytics import *
import analytics.analytics as analytics

from googleapiclient.discovery import build

# ==============================
# AUTH GUARD
# ==============================
if "authenticated" not in st.session_state:
    st.switch_page("authentication.py")

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="YouTube Analytics & Insights Dashboard",
    layout="wide"
)

# ==============================
# UI / CSS (UNCHANGED)
# ==============================
st.markdown("""
<!-- YOUR EXISTING CSS EXACTLY AS PROVIDED -->
""", unsafe_allow_html=True)

# ==============================
# DB CONNECTION
# ==============================
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
def load_channels(_conn):
    return pd.read_sql(
        "SELECT channel_id, channel_name FROM channels_detailed",
        _conn
    )

channels_df = load_channels(conn)

# ==============================
# YOUTUBE API SEARCH (NEW)
# ==============================
def search_channel_id_youtube_api(channel_name):
    youtube = build(
        "youtube",
        "v3",
        developerKey=st.secrets["youtube"]["api_key"]
    )

    response = youtube.search().list(
        part="snippet",
        q=channel_name,
        type="channel",
        maxResults=1
    ).execute()

    items = response.get("items", [])
    if not items:
        return None

    return items[0]["snippet"]["channelId"]

# ==============================
# DEFAULT USER CHANNEL AFTER LOGIN
# ==============================
if "active_channel_id" not in st.session_state:
    if "my_channel_id" in st.session_state:
        st.session_state["active_channel_id"] = st.session_state["my_channel_id"]

# ==============================
# HEADER + CHANNEL SEARCH
# ==============================
st.title("YouTube Analytics & Insights Dashboard")
st.markdown("## 🔍 Channel Lookup")

channel_input = st.text_input(
    "Enter YouTube Channel Name",
    placeholder="e.g. Think School, Veritasium"
)

# ==============================
# CHANNEL RESOLUTION LOGIC
# ==============================

# CASE 1: User searched something
if channel_input.strip():

    channel_row = channels_df[
        channels_df["channel_name"].str.lower() == channel_input.lower()
    ]

    # Found in DB
    if not channel_row.empty:
        st.session_state["active_channel_id"] = channel_row.iloc[0]["channel_id"]

    # Not in DB → API fallback
    else:
        st.info("Channel not found in database. Searching YouTube API...")

        api_channel_id = search_channel_id_youtube_api(channel_input)

        if not api_channel_id:
            st.error("Channel not found on YouTube.")
            st.stop()

        st.info("Fetching channel data from YouTube API...")
        fetch_channel_and_videos_from_api(api_channel_id)

        # Reload DB cache
        channels_df = load_channels(conn)
        st.session_state["active_channel_id"] = api_channel_id

# CASE 2: No search, no default
elif "active_channel_id" not in st.session_state:
    st.info("👆 Enter a YouTube channel name to view analytics.")
    st.stop()

channel_id = st.session_state["active_channel_id"]

# ==============================
# LOAD VIDEO DATA
# ==============================
df = analytics.load_video_data_by_channel(conn, channel_id)

if df.empty:
    st.error("Unable to load channel data.")
    st.stop()

# ==============================
# TABS (UNCHANGED)
# ==============================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Overview", "Performance", "Engagement", "Strategy", "Comparison"]
)

# ==============================
# TAB 1: OVERVIEW
# ==============================
with tab1:
    st.subheader("Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Videos", len(df))
    col2.metric("Total Views", int(df["views"].sum()))
    col3.metric("Avg Engagement", round(df["engagement_rate"].mean(), 4))
    col4.metric("Avg Duration (sec)", int(df["duration_seconds"].mean()))

    st.markdown("---")

    st.subheader("Top 10 Videos by Views")
    tv = analytics.top_videos_by_views(df)
    tv["title"] = tv["title"].apply(analytics.truncate_title)
    st.dataframe(tv, use_container_width=True)

    st.markdown("---")

    st.subheader("Top 10 Videos by Likes")
    tl = analytics.top_videos_by_likes(df)
    tl["title"] = tl["title"].apply(analytics.truncate_title)
    st.dataframe(tl, use_container_width=True)

    st.markdown("---")

    st.subheader("Top 10 Videos by Engagement Rate")
    te = analytics.top_videos_by_engagement(df)
    te["title"] = te["title"].apply(analytics.truncate_title)
    st.dataframe(te, use_container_width=True)

# ==============================
# TAB 2: PERFORMANCE
# ==============================
with tab2:
    st.subheader("Performance Analysis")

with tab2:
    st.subheader("Monthly Views Distribution")
    mv = monthly_views(df)
    st.line_chart(mv, x="month_name", y="views")

with tab2:
    st.subheader("Upload Frequency vs Average Views")
    freq_df = upload_frequency_vs_views(df)
    st.bar_chart(freq_df.set_index("month")["uploads"])
    st.line_chart(freq_df.set_index("month")["avg_views"])

# ==============================
# TAB 3: ENGAGEMENT
# ==============================
with tab3:
    st.subheader("Engagement Analysis")

with tab3:
    st.metric("Average Engagement Rate", round(df["engagement_rate"].mean(), 4))

with tab3:
    st.subheader("Likes vs Comments Correlation")
    st.scatter_chart(df, x="likes", y="comments")

with tab3:
    st.subheader("Views vs Engagement Rate")
    st.scatter_chart(df, x="views", y="engagement_rate")

# ==============================
# TAB 4: STRATEGY
# ==============================
with tab4:
    st.subheader("Upload Strategy Analysis")

with tab4:
    st.subheader("Best Day to Upload")
    day_df = df.groupby("day_name")["views"].mean().sort_values(ascending=False)
    st.bar_chart(day_df)

with tab4:
    st.subheader("Best Hour to Upload")
    hour_df = df.groupby("hour")["views"].mean().sort_values(ascending=False)
    st.line_chart(hour_df)

with tab4:
    best_day = day_df.index[0]
    best_hour = hour_df.index[0]

    st.success(
        f"Recommended Posting Strategy: Upload on **{best_day}** around **{best_hour}:00 hours**"
    )

# ==============================
# TAB 5: COMPARISON (UNCHANGED)
# ==============================
with tab5:
    st.subheader("Channel Comparison")

    channel_names = channels_df["channel_name"].tolist()

    col1, col2 = st.columns(2)

    with col1:
        ch1_name = st.selectbox("Select Channel 1", channel_names, key="compare_ch1")

    with col2:
        ch2_name = st.selectbox(
            "Select Channel 2",
            channel_names,
            index=1 if len(channel_names) > 1 else 0,
            key="compare_ch2"
        )

    ch1_id = channels_df.loc[channels_df["channel_name"] == ch1_name, "channel_id"].values[0]
    ch2_id = channels_df.loc[channels_df["channel_name"] == ch2_name, "channel_id"].values[0]

    df1 = analytics.load_video_data_by_channel(conn, ch1_id)
    df2 = analytics.load_video_data_by_channel(conn, ch2_id)

    c1, c2 = st.columns(2)

    with c1:
        st.metric("Avg Views", int(df1["views"].mean()))
        st.metric("Avg Engagement", round(df1["engagement_rate"].mean(), 4))
        st.metric("Total Videos", len(df1))

    with c2:
        st.metric("Avg Views", int(df2["views"].mean()))
        st.metric("Avg Engagement", round(df2["engagement_rate"].mean(), 4))
        st.metric("Total Videos", len(df2))
