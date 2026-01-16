import streamlit as st
import altair as alt
import analytics.analytics as analytics
import pandas as pd

def render(channel_input, channels_df, conn):
    st.markdown("""
       <div style="margin-bottom:30px;">
        <h2 style="font-weight:800; color:white; font-size:2.2rem;margin-left:499px;">⚖️ Channel Comparison</h2>
        <p style="color:#94a3b8; font-size:1rem;margin-left:500px;">Compare your channel's performance with competitors</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    # Get the full list of cannel names from the database
    channel_names = channels_df["channel_name"].tolist()

    # Logic to find tindex of the currently searched channel for Dropdown 1
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
        # Use indx=Non to crate a blankplaceholder
        ch2_name = st.selectbox(
            "Select Channel 2",
            channel_names,
            index=None,
            placeholder="Select a channel to compare...",
            key="compare_ch2"
        )

    # CHECK: Only show comparison if a secon channel is selected
    

    if ch2_name is None or ch1_name is None:
        st.markdown("---")
        st.info("💡 **Select a second channel** from the dropdown above to view side-by-side metrics and engagement trends.")
        return
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
        
        st.markdown("---")
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
        st.markdown("### 📊 Monthly Engagement Trend Comparison")
        st.markdown("---")
        m1 = (
            df1.groupby(["year", "month"])["engagement_rate"]
            .mean()
            .reset_index()
        )
        m1['channel'] = ch1_name

        m2 = (
            df2.groupby(["year", "month"])["engagement_rate"]
            .mean()
            .reset_index()
        )
        m2['channel'] = ch2_name

        # Combine data
        comparison_data = pd.concat([
            m1[['year', 'month', 'engagement_rate', 'channel']],
            m2[['year', 'month', 'engagement_rate', 'channel']]
        ])
        comparison_data['period'] = comparison_data['year'].astype(str) + "-" + comparison_data['month'].astype(str).str.zfill(2)
        comparison_data = comparison_data.sort_values('period')

        # Create colorful comparison chart
        comparison_chart = alt.Chart(comparison_data).mark_line(
            point=True,
            strokeWidth=3
        ).encode(
            x=alt.X('period:N', title='Period', axis=alt.Axis(labelAngle=-45, labelColor='#9bbcd6')),
            y=alt.Y('engagement_rate:Q', title='Engagement Rate', axis=alt.Axis(format='.4f', labelColor='#9bbcd6', gridColor='#1c3d5a')),
            color=alt.Color('channel:N',
                          scale=alt.Scale(domain=[ch1_name, ch2_name], range=['#FF0000', '#4cc3ff']),
                          legend=alt.Legend(title='Channel', labelColor='#9bbcd6', titleColor='#9bbcd6')),
            tooltip=['channel', 'period', alt.Tooltip('engagement_rate:Q', format='.4f')]
        ).properties(height=400).configure_view(strokeOpacity=0).configure_axis(titleColor='#9bbcd6')

        st.altair_chart(comparison_chart, use_container_width=True)
        
        # Add bar chart comparison
        

        # Determine winner
        avg1 = df1["engagement_rate"].mean()
        avg2 = df2["engagement_rate"].mean()
        winner = ch1_name if avg1 > avg2 else ch2_name

        st.success(
            f"🏆 Overall Insight: **{winner}** shows stronger average engagement between these two channels."
        )

        st.markdown("---")

        st.markdown("### 📊 Average Views per Video")
        st.markdown("---")
    avg_views_df = pd.DataFrame({
        "Channel": [ch1_name, ch2_name],
        "Avg Views": [df1['views'].mean(), df2['views'].mean()]
    })

    avg_views_chart = alt.Chart(avg_views_df).mark_bar(
        cornerRadiusTopLeft=8,
        cornerRadiusTopRight=8
    ).encode(
        x=alt.X('Channel:N', title=None, axis=alt.Axis(labelColor='#9bbcd6')),
        y=alt.Y(
            'Avg Views:Q',
            title='Average Views',
            axis=alt.Axis(format='~s', grid=True, gridColor='#1c3d5a')
        ),
        color=alt.Color(
            'Channel:N',
            scale=alt.Scale(range=['#4cc3ff', '#ff6b6b']),
            legend=None
        ),
        tooltip=[
            alt.Tooltip('Channel:N'),
            alt.Tooltip('Avg Views:Q', format=',')
        ]
    ).properties(height=320).configure_view(strokeOpacity=0)

    st.altair_chart(avg_views_chart, use_container_width=True)
    st.markdown("---")
    st.markdown("### 📅 Upload Frequency Comparison")
    st.markdown("---")
    freq_a = df1.groupby(['year', 'month']).size().reset_index(name='uploads')
    freq_b = df2.groupby(['year', 'month']).size().reset_index(name='uploads')

    freq_a['Channel'] = ch1_name
    freq_b['Channel'] = ch2_name

    freq_df = pd.concat([freq_a, freq_b])

    freq_chart = alt.Chart(freq_df).mark_line(
        point=True,
        strokeWidth=3
    ).encode(
        x=alt.X('month:O', title='Month'),
        y=alt.Y(
            'uploads:Q',
            title='Uploads',
            axis=alt.Axis(grid=True, gridColor='#1c3d5a')
        ),
        color=alt.Color(
            'Channel:N',
            scale=alt.Scale(range=['#4cc3ff', '#ff6b6b']),
            legend=alt.Legend(labelColor='#9bbcd6')
        ),
        tooltip=['Channel', 'uploads']
    ).properties(height=350).configure_view(strokeOpacity=0)

    st.altair_chart(freq_chart, use_container_width=True)
    st.markdown("---")
    st.markdown("### 📈 Views Trend Comparison")
    st.markdown("---")
    trend_a = df1.groupby(['year', 'month'])['views'].mean().reset_index()
    trend_b = df2.groupby(['year', 'month'])['views'].mean().reset_index()

    trend_a['Channel'] = ch1_name
    trend_b['Channel'] = ch2_name

    trend_df = pd.concat([trend_a, trend_b])

    trend_chart = alt.Chart(trend_df).mark_line(
        strokeWidth=3,
        interpolate='monotone'
    ).encode(
        x=alt.X('month:O', title='Month'),
        y=alt.Y(
            'views:Q',
            title='Average Views',
            axis=alt.Axis(format='~s', grid=True, gridColor='#1c3d5a')
        ),
        color=alt.Color(
            'Channel:N',
            scale=alt.Scale(range=['#4cc3ff', '#ff6b6b']),
            legend=alt.Legend(labelColor='#9bbcd6')
        ),
        tooltip=['Channel', alt.Tooltip('views:Q', format=',')]
    ).properties(height=380).configure_view(strokeOpacity=0)

    st.altair_chart(trend_chart, use_container_width=True)
 