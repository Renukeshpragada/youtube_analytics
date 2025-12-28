import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="YouTube Channel Analytics",
    layout="centered"
)

# -----------------------------
# CLEAN WHITE THEME
# -----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #ffffff;
    }

    h1, h2, h3 {
        color: #111111;
        text-align: center;
    }

    .metric-box {
        background-color: #f5f5f5;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0px 0px 8px rgba(0,0,0,0.1);
    }

    .stButton>button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# TITLE
# -----------------------------
st.markdown("<h1>YouTube Channel Analytics Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<h3>Search channel statistics and performance insights</h3>", unsafe_allow_html=True)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(".\data\sql_exports\master_data.csv")

    # normalize column names (IMPORTANT)
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df

df = load_data()

# -----------------------------
# INPUT
# -----------------------------
st.markdown("### 🔍 Enter Channel Name")
channel_input = st.text_input("", placeholder="Example: Google Developers")
search_btn = st.button("Search")

# -----------------------------
# SEARCH LOGIC
# -----------------------------
if search_btn:
    if channel_input.strip() == "":
        st.warning("Please enter a channel name.")
    else:
        result = df[df["channel_name"].str.lower() == channel_input.lower()]

        if result.empty:
            st.error("Channel not found in the database.")
        else:
            channel = result.iloc[0]

            # -----------------------------
            # METRICS (4 STATISTICS)
            # -----------------------------
            col1, col2 = st.columns(2)
            col3, col4 = st.columns(2)

            with col1:
                st.markdown(
                    f"""
                    <div class="metric-box">
                        <h3>Subscribers</h3>
                        <h2>{int(channel['subscribers']):,}</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:
                st.markdown(
                    f"""
                    <div class="metric-box">
                        <h3>Total Videos</h3>
                        <h2>{int(channel['total_videos'])}</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col3:
                st.markdown(
                    f"""
                    <div class="metric-box">
                        <h3>Total Views</h3>
                        <h2>{int(channel['total_views']):,}</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col4:
                st.markdown(
                    f"""
                    <div class="metric-box">
                        <h3>Stored Videos</h3>
                        <h2>{int(channel['stored_video_count'])}</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # -----------------------------
            # CHART 1: BAR CHART (Subscribers vs Views)
            # -----------------------------
            st.markdown("### 📊 Subscribers vs Total Views")

            fig1, ax1 = plt.subplots()
            ax1.bar(
                ["Subscribers", "Total Views"],
                [channel["subscribers"], channel["total_views"]],
            )
            st.pyplot(fig1)

            # -----------------------------
            # CHART 2: PIE CHART (Video Contribution)
            # -----------------------------
            st.markdown("### 📊 Video Contribution")

            fig2, ax2 = plt.subplots()
            ax2.pie(
                [channel["stored_video_count"], channel["total_videos"] - channel["stored_video_count"]],
                labels=["Stored Videos", "Other Videos"],
                autopct="%1.1f%%",
                startangle=90
            )
            st.pyplot(fig2)

            # -----------------------------
            # CHART 3: LINE-LIKE COMPARISON (Simple)
            # -----------------------------
            st.markdown("### 📈 Growth Comparison")

            fig3, ax3 = plt.subplots()
            ax3.plot(
                ["Subscribers", "Total Views"],
                [channel["subscribers"], channel["total_views"]],
                marker="o"
            )
            st.pyplot(fig3)

# -----------------------------
# FOOTER
# -----------------------------
st.markdown(
    """
    <hr>
    <center>
    <p style="color:gray">
    Individual Project – YouTube Analytics Dashboard<br>
    Built using Streamlit and SQL-derived data
    </p>
    </center>
    """,
    unsafe_allow_html=True
)
