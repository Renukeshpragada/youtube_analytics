import streamlit as st
import mysql.connector
import pandas as pd

from analytics.analytics import *
import analytics.analytics as analytics


# ==============================
# AUTH GUARD
# ==============================
if "authenticated" not in st.session_state:
    st.switch_page("pages/authentication.py")


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
# HEADER + CHANNEL INPUT
# ==============================
st.title("YouTube Analytics & Insights Dashboard")

st.markdown("## 🔍 Channel Lookup")

channel_input = st.text_input(
    "Enter YouTube Channel Name",
    placeholder="e.g. Madan Gowri, Think School, Veritasium"
)

# ---- STOP HERE IF EMPTY ----
if not channel_input.strip():
    st.info("👆 Enter a YouTube channel name to view analytics.")
    st.stop()

# ---- FIND CHANNEL ----
channel_row = channels_df[
    channels_df["channel_name"].str.lower() == channel_input.lower()
]

if channel_row.empty:
    st.warning("Channel not found in database.")
    st.stop()

channel_id = channel_row.iloc[0]["channel_id"]

# ---- LOAD DATA ONCE ----
df = analytics.load_video_data_by_channel(conn, channel_id)

if df.empty:
    st.warning("No video data available for this channel.")
    st.stop()


# ==============================
# TABS
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
with tab4:
    st.subheader("Upload Strategy Analysis")
with tab4:
    st.subheader("Best Day to Upload")

    day_df = (
        df.groupby("day_name")["views"]
        .mean()
        .sort_values(ascending=False)
    )

    st.bar_chart(day_df)

with tab4:
    st.subheader("Best Hour to Upload")

    hour_df = (
        df.groupby("hour")["views"]
        .mean()
        .sort_values(ascending=False)
    )

    st.line_chart(hour_df)
with tab4:
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

with tab4:
    best_day = day_df.index[0]
    best_hour = hour_df.index[0]

    st.success(
        f"Recommended Posting Strategy: "
        f"Upload on **{best_day}** around **{best_hour}:00 hours** "
        f"for higher average views."
    )


# ==============================
# TAB 5: COMPARISON (UNCHANGED)
# ==============================
with tab5:
    st.subheader("Channel Comparison")

    # Use ALL channels from DB, not df
    channel_names = channels_df["channel_name"].tolist()

    col1, col2 = st.columns(2)

    with col1:
        ch1_name = st.selectbox(
            "Select Channel 1",
            channel_names,
            key="compare_ch1"
        )

    with col2:
        ch2_name = st.selectbox(
            "Select Channel 2",
            channel_names,
            index=1 if len(channel_names) > 1 else 0,
            key="compare_ch2"
        )

    # Convert names → IDs
    ch1_id = channels_df.loc[
        channels_df["channel_name"] == ch1_name, "channel_id"
    ].values[0]

    ch2_id = channels_df.loc[
        channels_df["channel_name"] == ch2_name, "channel_id"
    ].values[0]

    # Load data for both channels
    df1 = analytics.load_video_data_by_channel(conn, ch1_id)
    df2 = analytics.load_video_data_by_channel(conn, ch2_id)

    st.markdown("---")
    st.subheader("Key Metrics Comparison")

    c1, c2 = st.columns(2)

    with c1:
        st.metric("Avg Views", int(df1["views"].mean()))
        st.metric("Avg Engagement", round(df1["engagement_rate"].mean(), 4))
        st.metric("Total Videos", len(df1))

    with c2:
        st.metric("Avg Views", int(df2["views"].mean()))
        st.metric("Avg Engagement", round(df2["engagement_rate"].mean(), 4))
        st.metric("Total Videos", len(df2))

    st.markdown("---")
    st.subheader("Monthly Engagement Trend")

    m1 = (
        df1.groupby(["year", "month"])["engagement_rate"]
        .mean()
        .reset_index()
        .rename(columns={"engagement_rate": ch1_name})
    )

    m2 = (
        df2.groupby(["year", "month"])["engagement_rate"]
        .mean()
        .reset_index()
        .rename(columns={"engagement_rate": ch2_name})
    )

    merged = pd.merge(
        m1, m2,
        on=["year", "month"],
        how="outer"
    ).fillna(0)

    merged["period"] = merged["year"].astype(str) + "-" + merged["month"].astype(str)

    st.line_chart(
        merged.set_index("period")[[ch1_name, ch2_name]]
    )

    st.markdown("---")

    winner = (
        ch1_name
        if df1["engagement_rate"].mean() > df2["engagement_rate"].mean()
        else ch2_name
    )

    st.success(
        f"Overall Insight: **{winner}** shows stronger average engagement."
    )
