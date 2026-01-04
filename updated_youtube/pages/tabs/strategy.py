import streamlit as st
import altair as alt
import pandas as pd

def render(df):
    st.subheader("🎯 Upload Strategy Analysis")

    # ==============================
    # 1. BEST DAY TO UPLOAD (Solid Bars - No Lines)
    # ==============================
    st.markdown("### Best Day to Upload")
    
    # Pre-sort days chronologically
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Aggregate data to avoid segmented/lined bars
    day_df = df.groupby("day_name")["views"].mean().reset_index(name="avg_views")

    day_chart = alt.Chart(day_df).mark_bar(
        color='#4cc3ff',
        cornerRadiusTopLeft=8,
        cornerRadiusTopRight=8,
        opacity=0.9
    ).encode(
        x=alt.X('day_name:N', sort=day_order, title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y('avg_views:Q', title='Average Views', axis=alt.Axis(format='~s', grid=True, gridColor='#1c3d5a')),
        tooltip=['day_name', alt.Tooltip('avg_views', format=',')]
    ).properties(height=350).configure_view(strokeOpacity=0).configure_axis(labelColor='#9bbcd6', titleColor='#9bbcd6')

    st.altair_chart(day_chart, use_container_width=True)

    # ==============================
    # 2. BEST HOUR TO UPLOAD (Area Chart)
    # ==============================
    st.markdown("---")
    st.markdown("### Best Hour to Upload (24h Format)")

    hour_df = df.groupby("hour")["views"].mean().reset_index(name="avg_views")

    hour_chart = alt.Chart(hour_df).mark_area(
        line={'color': '#1E90FF', 'size': 3},
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color='#1E90FF', offset=1),
                   alt.GradientStop(color='rgba(30, 144, 255, 0.1)', offset=0)],
            x1=1, x2=1, y1=1, y2=0
        )
    ).encode(
        x=alt.X('hour:O', title='Hour of Day (24h)', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('avg_views:Q', title='Average Views', axis=alt.Axis(format='~s', grid=True, gridColor='#1c3d5a')),
        tooltip=['hour', alt.Tooltip('avg_views', format=',')]
    ).properties(height=300).configure_view(strokeOpacity=0)

    st.altair_chart(hour_chart, use_container_width=True)

    # ==============================
    # 3. SUCCESS INSIGHTS
    # ==============================
    st.markdown("---")
    
    best_day = day_df.sort_values("avg_views", ascending=False).iloc[0]["day_name"]
    best_hour = hour_df.sort_values("avg_views", ascending=False).iloc[0]["hour"]

    st.success(
        f"📊 **Winning Strategy:** Uploading on **{best_day}** around **{best_hour}:00** "
        f"generally results in higher initial peak views for this channel."
    )