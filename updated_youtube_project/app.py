import streamlit as st
from analytics.analytics import * 
import analytics.analytics as analytics
import mysql.connector

st.set_page_config(page_title="YouTube Analytics Dashboard", layout="wide")

st.title("YouTube Analytics & Insights Dashboard")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Overview", "Performance", "Engagement", "Strategy", "Comparison"]
)

@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="yt_user",
        password="StrongPass@123",
        database="youtube_analytics"
    )

conn = get_connection()
df = load_video_data(conn)


@st.cache_data
@st.cache_data
def load_channels(_conn):
    query = "SELECT channel_id, channel_name FROM channels_detailed"
    return pd.read_sql(query, _conn)

channels_df = load_channels(conn)




with tab1:
    st.markdown("### Select YouTube Channel")

    selected_channel = st.selectbox(
        "Channel",
        channels_df["channel_name"],
        key="main_channel_select"
    )

    channel_id = channels_df.loc[
        channels_df["channel_name"] == selected_channel,
        "channel_id"
    ].values[0]
    df = analytics.load_video_data_by_channel(conn, channel_id)
    if df.empty:
        st.warning("No data available for this channel.")
        st.stop()
        
    st.subheader("Overview")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Videos", len(df))
    col2.metric("Total Views", int(df["views"].sum()))
    col3.metric("Avg Engagement", round(df["engagement_rate"].mean(), 4))
    col4.metric("Avg Duration (sec)", int(df["duration_seconds"].mean()))
    st.markdown("---")
    st.subheader("Top 10 Videos by Views")

    top_views_df = analytics.top_videos_by_views(df)
    top_views_df["title"] = top_views_df["title"].apply(analytics.truncate_title)

    st.dataframe(top_views_df,use_container_width=True)
    st.markdown("---")
    st.subheader("Top 10 Videos by Likes")

    top_likes_df = analytics.top_videos_by_likes(df)
    top_likes_df["title"] = top_likes_df["title"].apply(analytics.truncate_title)

    st.dataframe(top_likes_df,use_container_width=True)
    st.markdown("---")
    st.subheader("Top 10 Videos by Engagement Rate")

    top_engagement_df = analytics.top_videos_by_engagement(df)
    top_engagement_df["title"] = top_engagement_df["title"].apply(analytics.truncate_title)

    st.dataframe(top_engagement_df,use_container_width=True)

with tab2:
    st.subheader("Performance Analysis")

with tab2:
    st.subheader("Monthly Views Distribution")

    monthly_df = monthly_views(df)

    st.line_chart(
        monthly_df,
        x="month_name",
        y="views"
    )

    st.caption(
        "Shows total views of videos published in each month "
        "(based on publish date, not real-time growth)."
    )

with tab2:
    st.subheader("Upload Frequency vs Average Views")

    freq_df = upload_frequency_vs_views(df)

    st.bar_chart(freq_df.set_index("month")["uploads"])
    st.line_chart(freq_df.set_index("month")["avg_views"])

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
