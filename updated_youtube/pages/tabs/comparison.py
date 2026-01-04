import streamlit as st
import analytics.analytics as analytics
import pandas as pd

def render(channel_input, channels_df, conn):
    st.subheader("Channel Comparison")

    # Get the full list of channel names from the database
    channel_names = channels_df["channel_name"].tolist()

    # Logic to find the index of the currently searched channel for Dropdown 1
    try:
        default_ch1_index = channel_names.index(channel_input)
    except ValueError:
        default_ch1_index = 0

    col1, col2 = st.columns(2)

    with col1:
        ch1_name = st.selectbox(
            "Select Channel 1",
            channel_names,
            index=default_ch1_index, # Automatically matches your main search
            key="compare_ch1"
        )

    with col2:
        # Use index=None to create a blank placeholder
        ch2_name = st.selectbox(
            "Select Channel 2",
            channel_names,
            index=None,
            placeholder="Select a channel to compare...",
            key="compare_ch2"
        )

    # CHECK: Only show comparison if a second channel is selected
    if ch2_name is None:
        st.markdown("---")
        st.info("💡 **Select a second channel** from the dropdown above to view side-by-side metrics and engagement trends.")
    else:
        # Convert names → IDs
        ch1_id = channels_df.loc[
            channels_df["channel_name"] == ch1_name, "channel_id"
        ].values[0]

        ch2_id = channels_df.loc[
            channels_df["channel_name"] == ch2_name, "channel_id"
        ].values[0]

        # Load data for both channels
        df1 = analytics.load_video_data_by_channel(ch1_id)
        df2 = analytics.load_video_data_by_channel(ch2_id)

        st.markdown("---")
        st.subheader("Key Metrics Comparison")

        c1, c2 = st.columns(2)

        with c1:
            st.markdown(f"### {ch1_name}")
            st.metric("Avg Views", f"{int(df1['views'].mean()):,}")
            st.metric("Avg Engagement", round(df1["engagement_rate"].mean(), 4))
            st.metric("Total Videos", len(df1))

        with c2:
            st.markdown(f"### {ch2_name}")
            st.metric("Avg Views", f"{int(df2['views'].mean()):,}")
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

        # Create period for X-axis
        merged["period"] = merged["year"].astype(str) + "-" + merged["month"].astype(str).str.zfill(2)
        merged = merged.sort_values("period")

        st.line_chart(
            merged.set_index("period")[[ch1_name, ch2_name]]
        )

        st.markdown("---")

        # Determine winner
        avg1 = df1["engagement_rate"].mean()
        avg2 = df2["engagement_rate"].mean()
        winner = ch1_name if avg1 > avg2 else ch2_name

        st.success(
            f"🏆 Overall Insight: **{winner}** shows stronger average engagement between these two channels."
        )
