import streamlit as st
import altair as alt
import analytics.analytics as analytics
import pandas as pd

def render(channel_input, channels_df, conn):
    st.markdown("""
    <div class="section-header">
        <h2>⚖️ Channel Comparison</h2>
        <p>Compare your channel's performance with competitors</p>
    </div>
    """, unsafe_allow_html=True)

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
        st.markdown("### 📊 Monthly Engagement Trend Comparison")

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
        st.markdown("### 📈 Side-by-Side Metrics Comparison")
        
        metrics_data = pd.DataFrame({
            'Metric': ['Avg Views', 'Avg Engagement', 'Total Videos'],
            ch1_name: [
                int(df1['views'].mean()),
                round(df1['engagement_rate'].mean(), 4),
                len(df1)
            ],
            ch2_name: [
                int(df2['views'].mean()),
                round(df2['engagement_rate'].mean(), 4),
                len(df2)
            ]
        })
        
        # Normalize for comparison
        metrics_long = pd.melt(metrics_data, id_vars=['Metric'], value_vars=[ch1_name, ch2_name], 
                              var_name='Channel', value_name='Value')
        
        bar_comparison = alt.Chart(metrics_long).mark_bar(
            cornerRadiusTopLeft=6,
            cornerRadiusTopRight=6
        ).encode(
            x=alt.X('Metric:N', title='Metric', axis=alt.Axis(labelAngle=0, labelColor='#9bbcd6')),
            y=alt.Y('Value:Q', title='Value', axis=alt.Axis(labelColor='#9bbcd6', gridColor='#1c3d5a')),
            color=alt.Color('Channel:N',
                          scale=alt.Scale(domain=[ch1_name, ch2_name], range=['#FF0000', '#4cc3ff']),
                          legend=alt.Legend(title='Channel', labelColor='#9bbcd6', titleColor='#9bbcd6')),
            column=alt.Column('Metric:N', spacing=20),
            tooltip=['Channel', 'Metric', alt.Tooltip('Value:Q', format='.2f')]
        ).properties(width=150, height=300).configure_view(strokeOpacity=0).configure_axis(titleColor='#9bbcd6')
        
        st.altair_chart(bar_comparison, use_container_width=True)

        st.markdown("---")

        # Determine winner
        avg1 = df1["engagement_rate"].mean()
        avg2 = df2["engagement_rate"].mean()
        winner = ch1_name if avg1 > avg2 else ch2_name

        st.success(
            f"🏆 Overall Insight: **{winner}** shows stronger average engagement between these two channels."
        )
