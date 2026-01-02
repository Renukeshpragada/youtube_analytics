import streamlit as st
import mysql.connector
import pandas as pd
from analytics.analytics import *
import analytics.analytics as analytics

# ==============================
# AUTH GUARD & LOGOUT
# ==============================
if "authenticated" not in st.session_state:
    st.switch_page("authentication.py")

# LOGOUT BUTTON IN SIDEBAR
with st.sidebar:
    st.markdown("### User Profile")
    if "user" in st.session_state:
        st.write(f"Logged in as: **{st.session_state.user['name']}**")
    if st.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("authentication.py")

# ==============================
# PAGE CONFIG & UI (UNCHANGED CSS)
# ==============================
st.set_page_config(page_title="YouTube Analytics Dashboard", layout="wide")
# [KEEP YOUR CSS MARKDOWN HERE - REMOVED FOR BREVITY]
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    display: none !important;
}
/* ---- MAIN BACKGROUND ---- */
.stApp {
    background: radial-gradient(
        circle at bottom left,
        #0a2a43 35%,
        #04111d 70%,
        #000000 80%
    );
    color: #eaeaea;
    font-family: 'Segoe UI', sans-serif;
}

/* ---- HEADINGS ---- */
h1, h2, h3, h4 {
    color: #CCCCCC;
    font-weight: 600;
}

/* ---- TABS ---- */
.stTabs [data-baseweb="tab"] {
    color: #9bbcd6;
    font-size: 16px;
}

.stTabs [aria-selected="true"] {
    color: #4cc3ff !important;
    border-bottom: 3px solid #4cc3ff;
}

/* ---- METRIC CARDS ---- */
div[data-testid="metric-container"] {
    background: linear-gradient(
        145deg,
        #0b253a,
        #081a2a
    );
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 0 12px rgba(0, 140, 255, 0.15);
}

div[data-testid="metric-container"] label {
    color: #9bbcd6;
}

div[data-testid="metric-container"] div {
    color: #ffffff;
}

/* ---- TABLES ---- */
thead tr th {
    background-color: #0b253a !important;
    color: #9bdcff !important;
}

tbody tr td {
    background-color: #040e18 !important;
    color: #eaeaea !important;
}

tbody tr:hover td {
    background-color: #0b253a !important;
}
            p {
    color: #9bbcd6;        /* soft blue-gray for readability */
    font-size: 25px;
    line-height: 1.6;
    font-weight: 400;
    margin-bottom: 0.6rem;
}
.st-emotion-cache-1q82h82{
            color: #A9A9A9;
}
            input, textarea {
    background-color: #081a2a !important;
    color: #ffffff !important;
    border-radius: 8px;
}
            .st-emotion-cache-1jsf23j>p{
             font-size: 17px;
            
            color: #4DD0E1;
}
            
            
.stAlertContainer {
    background-color: #102437 !important;
    color: #ffffff !important;
    border-radius: 8px; 
            }
            .st-emotion-cache-pk3c77>p{
            color: #FFC857!important;
            font-size: 16px;    }
p>strong{
            color: #FF6F61!important;
            font-size: 24px;        }


        .st-emotion-cache-5wrjf1>p{
            color:#fcc909!important;   
            font-size: 23px;    }

/* ---- SELECT BOX ---- */
div[data-baseweb="select"] > div {
    background-color: #081a2a !important;
    color: white !important;
}
            input::placeholder {
    color: #A9A9A9 !important;   /* brighter blue */
    opacity: 1 !important;       /* full brightness */
}

/* For better browser compatibility */
input::-webkit-input-placeholder {
    color:  #A9A9A9 !important;
    opacity: 1 !important;
}

input:-ms-input-placeholder {
    color:  #A9A9A9 !important;
}

input::-ms-input-placeholder {
    color:  #A9A9A9 !important;
}

/* ---- SCROLLBAR ---- */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-thumb {
    background: #4cc3ff;
    border-radius: 6px;
}

</style>
""", unsafe_allow_html=True)


# ==============================
# DB CONNECTION
# ==============================
@st.cache_resource
def get_connection():
    return mysql.connector.connect(host="localhost", user="yt_user", password="StrongPass@123", database="youtube_analytics")
conn = get_connection()

@st.cache_data
def load_channels(_conn):
    return pd.read_sql("SELECT channel_id, channel_name FROM channels_detailed", _conn)
channels_df = load_channels(conn)

# ==============================
# HEADER + AUTO CHANNEL LOGIC
# ==============================
st.title("YouTube Analytics & Insights Dashboard")

# Determine default channel from Login
my_channel = st.session_state.get("user_yt_channel")
default_name = my_channel["channel_name"] if my_channel else ""

st.markdown("## 🔍 Channel Lookup")
channel_input = st.text_input(
    "Enter YouTube Channel Name", 
    value=default_name, # Defaults to the logged-in user's channel
    placeholder="Searching for your own channel by default..."
)

# FIND CHANNEL
# ---- FIND CHANNEL ----
channel_row = channels_df[channels_df["channel_name"].str.lower() == channel_input.lower()]

is_from_db = False
df = pd.DataFrame() # Initialize empty
api_stats = {}

if not channel_row.empty:
    # 1. CHANNEL FOUND IN LOCAL DB
    channel_id = channel_row.iloc[0]["channel_id"]
    df = analytics.load_video_data_by_channel(conn, channel_id)
    is_from_db = True
else:
    # 2. CHANNEL NOT IN DB -> FETCH FROM LIVE API
    st.info("🔍 Channel not in local database. Fetching live data from YouTube API...")
    try:
        api_key = st.secrets["google"]["api_key"]
        from extraction.youtube_api import get_channel_id_by_name, fetch_channel_stats_from_api
        
        target_id = get_channel_id_by_name(api_key, channel_input)
        if target_id:
            api_stats = fetch_channel_stats_from_api(api_key, target_id)
            # Create a fake single-row dataframe for the overview cards
            df = pd.DataFrame([{
                "views": api_stats['total_views'],
                "engagement_rate": 0.0, 
                "duration_seconds": 0
            }])
        else:
            st.error("Could not find that channel on YouTube either.")
            st.stop()
    except Exception as e:
        st.error(f"API Error: Make sure your YouTube API Key is correct. {e}")
        st.stop()

# ==============================
# UPDATED TABS & FEATURES
# ==============================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["Overview", "Pricing (Earnings)", "Daily Ideas", "AI Growth Chat", "Comparison", "Blogs"]
)

with tab1:
    if is_from_db:
        # Show your original overview code for DB channels
        st.subheader(f"Detailed Overview: {channel_input}")
        # ... (Your existing Overview code) ...
    else:
        # Show LIVE API STATS for channels like MrBeast
        st.subheader(f"Live Statistics: {api_stats['channel_name']}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Subscribers", f"{api_stats['subscribers']:,}")
        c2.metric("Total Views", f"{api_stats['total_views']:,}")
        c3.metric("Total Videos", f"{api_stats['video_count']:,}")
        st.warning("Note: Deep video-level analytics (Performance/Strategy) are only available for channels in your local database.")

with tab2:
    st.subheader("💰 Estimated Channel Earnings (Pricing)")
    # Calculate earnings based on total views (industry avg CPM $4)
    total_views = api_stats['total_views'] if not is_from_db else df["views"].sum()
    earnings = (total_views / 1000) * 4.0
    st.metric("Estimated Lifetime Revenue", f"${int(earnings):,}")
    st.caption("Based on standard $4.00 CPM.")

with tab3:
    st.subheader("💡 Daily Video Ideas (VidIQ Style)")
    st.success("Trend: 'Reaction to new AI Tools' is currently exploding in your niche.")
    st.success("Idea: 'How to master YouTube Analytics in 10 minutes'.")

with tab4:
    st.subheader("🤖 AI Growth Chatbot")
    prompt = st.chat_input("Ask how to grow this channel...")
    if prompt:
        st.info(f"AI: For a channel like '{channel_input}', focusing on high-retention thumbnails and keywords related to current trends will increase CTR by 15%.")

with tab6:
    st.subheader("📰 Latest Creator Blogs")
    st.markdown("- [How to get your first 1000 subs](https://example.com)")
    st.markdown("- [The ultimate guide to YouTube SEO](https://example.com)")

# [TAB 1, 2, 3 - UNCHANGED FROM YOUR CODE]
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
    
    st.caption(
        "Shows total views of videos published in each month "
        "(based on publish date)."
    )

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
    avg_eng = round(df["engagement_rate"].mean(), 4)

    st.metric(
        label="Average Engagement Rate",
        value=avg_eng
    )

    st.caption(
        "Engagement Rate = (Likes + Comments) / Views"
    )

with tab3:
    st.subheader("Likes vs Comments Correlation")

    st.scatter_chart(
        df,
        x="likes",
        y="comments"
    )
with tab3:
    st.subheader("Views vs Engagement Rate")

    st.scatter_chart(
        df,
        x="views",
        y="engagement_rate"
    )

    st.caption(
        "High views + high engagement indicates viral content. "
        "Low engagement despite high views suggests passive audience."
    )
# ==============================
# TAB 4: STRATEGY
# ==============================

# ==============================
# TAB 4: PRICING (EARNINGS)
# ==============================
with tab4:
    st.subheader("💰 Estimated Channel Earnings")
    total_views = df["views"].sum()
    
    col1, col2, col3 = st.columns(3)
    # Industry standard CPM ranges $2 - $7
    low_est = (total_views / 1000) * 2.0
    mid_est = (total_views / 1000) * 4.5
    high_est = (total_views / 1000) * 7.0

    col1.metric("Low Estimate ($2 CPM)", f"${int(low_est):,}")
    col2.metric("Average Estimate ($4.5 CPM)", f"${int(mid_est):,}")
    col3.metric("High Estimate ($7 CPM)", f"${int(high_est):,}")
    
    st.info("Note: These are estimates based on total views. Actual YouTube revenue depends on niche, location, and ad types.")

# ==============================
# TAB 5: AI IDEAS & CHATBOT
# ==============================
with tab5:
    st.subheader("🤖 AI Growth Assistant")
    
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.markdown("### 💡 Daily Video Ideas")
        # Logic: Suggest ideas based on their top performing titles
        top_titles = df.sort_values("views", ascending=False)["title"].head(3).tolist()
        st.write("Based on your top videos, try these:")
        for title in top_titles:
            st.success(f"Idea: 'The Secret behind {title} - Deep Dive'")
            
    with c2:
        st.markdown("### 💬 Ask the AI Chatbot")
        user_msg = st.text_input("Ask how to grow your channel:", placeholder="How do I get more subscribers?")
        if user_msg:
            # Simple Logic or call your AI API here
            st.info(f"AI Suggestion: For your channel, focusing on high-engagement topics like your top videos will help. Try uploading on {df.groupby('day_name')['views'].mean().idxmax()}.")

# ==============================
# TAB 7: BLOGS
# ==============================
with tab7:
    st.subheader("📰 Content Creator Blogs")
    st.markdown("""
    - **How to beat the Algorithm in 2024**
    - **10 Tips for Better Thumbnails**
    - **The Future of Short-form Content**
    """)
    st.button("Read more articles")
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
    
    st.caption(
        "Shows total views of videos published in each month "
        "(based on publish date)."
    )

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
    avg_eng = round(df["engagement_rate"].mean(), 4)

    st.metric(
        label="Average Engagement Rate",
        value=avg_eng
    )

    st.caption(
        "Engagement Rate = (Likes + Comments) / Views"
    )

with tab3:
    st.subheader("Likes vs Comments Correlation")

    st.scatter_chart(
        df,
        x="likes",
        y="comments"
    )
with tab3:
    st.subheader("Views vs Engagement Rate")

    st.scatter_chart(
        df,
        x="views",
        y="engagement_rate"
    )

    st.caption(
        "High views + high engagement indicates viral content. "
        "Low engagement despite high views suggests passive audience."
    )
# ==============================
# TAB 4: STRATEGY
# ==============================
with tab8:
    st.subheader("Upload Strategy Analysis")
with tab8:
    st.subheader("Best Day to Upload")

    day_df = (
        df.groupby("day_name")["views"]
        .mean()
        .sort_values(ascending=False)
    )

    st.bar_chart(day_df)

with tab8:
    st.subheader("Best Hour to Upload")

    hour_df = (
        df.groupby("hour")["views"]
        .mean()
        .sort_values(ascending=False)
    )

    st.line_chart(hour_df)
with tab8:
    st.subheader("Upload Frequency vs Average Views")

    freq_df = (
        df.groupby(["year", "month"])
        .agg(
            uploads=("video_id", "count"),
            avg_views=("views", "mean")
        )
        .reset_index()
    )

    st.line_chart(freq_df.set_index("month")[["uploads", "avg_views"]])

with tab8:
    best_day = day_df.index[0]
    best_hour = hour_df.index[0]

    st.success(
        f"Recommended Posting Strategy: "
        f"Upload on **{best_day}** around **{best_hour}:00 hours** "
        f"for higher average views."
    )