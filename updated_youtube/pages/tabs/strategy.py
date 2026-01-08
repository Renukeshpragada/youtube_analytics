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

# Aggregate data (UNCHANGED)
    day_df = df.groupby("day_name")["views"].mean().reset_index(name="avg_views")

    day_chart = alt.Chart(day_df).mark_bar(
        cornerRadiusTopLeft=8,
        cornerRadiusTopRight=8
    ).encode(
        x=alt.X(
            'day_name:N',
            sort=day_order,
            title=None,
            axis=alt.Axis(
                labelAngle=0,
                labelColor='#9bbcd6'
            )
        ),
        y=alt.Y(
            'avg_views:Q',
            title='Average Views',
            axis=alt.Axis(
                format='~s',
                grid=True,
                gridColor='#1c3d5a',
                labelColor='#9bbcd6'
            )
        ),
        color=alt.Color(
            'avg_views:Q',
            scale=alt.Scale(
                scheme='plasma'  # 🔥 colorful & perceptually ordered
            ),
            legend=alt.Legend(
                title='Avg Views Intensity',
                labelColor='#9bbcd6',
                titleColor='#9bbcd6'
            )
        ),
        tooltip=[
            alt.Tooltip('day_name:N', title='Day'),
            alt.Tooltip('avg_views:Q', title='Avg Views', format=',')
        ]
    ).properties(
        height=360
    ).configure_view(
        strokeOpacity=0
    ).configure_axis(
        titleColor='#9bbcd6'
    )

    st.altair_chart(day_chart, use_container_width=True)

    st.markdown("---")

    st.markdown("### Best Hour to Upload (24h Format)")

# ==============================
# DATA (UNCHANGED)
# ==============================
    hour_df = df.groupby("hour")["views"].mean().reset_index(name="avg_views")

# ==============================
# LINE (MATCHES EARNINGS STYLE)
# ==============================
    hour_line = alt.Chart(hour_df).mark_line(
        point=True,
        strokeWidth=4,
        color="#1E90FF",
        interpolate="monotone"
    ).encode(
        x=alt.X(
            "hour:O",
            title="Hour of Day (24h)",
            axis=alt.Axis(
                labelAngle=0,
                labelColor="#9bbcd6",
                grid=False
            )
        ),
        y=alt.Y(
            "avg_views:Q",
            title="Average Views",
            axis=alt.Axis(
                format="~s",
                labelColor="#9bbcd6",
                grid=True,
                gridColor="#1c3d5a",
                gridDash=[3, 3],
            )
        ),
        tooltip=[
            alt.Tooltip("hour:O", title="Hour"),
            alt.Tooltip("avg_views:Q", title="Avg Views", format=",")
        ]
    )

# ==============================
# AREA (MATCHES EARNINGS STYLE)
# ==============================
    hour_area = alt.Chart(hour_df).mark_area(
        interpolate="monotone",
        color=alt.Gradient(
            gradient="linear",
            stops=[
                alt.GradientStop(color="rgba(30, 144, 255, 0.7)", offset=0),
                alt.GradientStop(color="rgba(30, 144, 255, 0.1)", offset=1),
            ],
            x1=0, x2=0, y1=0, y2=1,
        )
    ).encode(
        x="hour:O",
        y="avg_views:Q"
        )

# ==============================
# COMBINED CHART
# ==============================
    hour_chart = (
        hour_area + hour_line
    ).properties(
        height=350
    ).configure_view(
        strokeOpacity=0
    ).configure_axis(
        titleColor="#9bbcd6"
    )

    st.altair_chart(hour_chart, use_container_width=True)

    st.markdown("---")

    

    st.markdown("### 🎯 Strategy: Upload Frequency vs Performance")

# ==============================
# DATA (NEW STRATEGY)
# ==============================
    freq_perf_df = (
        df.groupby(['year', 'month'])
        .agg(
            uploads=('video_id', 'count'),
            avg_views=('views', 'mean')
        )
        .reset_index()
    )

# ==============================
# SCATTER + TREND LINE
# ==============================
    scatter = alt.Chart(freq_perf_df).mark_circle(
        size=140,
        opacity=0.8
    ).encode(
        x=alt.X(
            'uploads:Q',
            title='Uploads per Month',
            axis=alt.Axis(labelColor='#9bbcd6')
        ),
        y=alt.Y(
            'avg_views:Q',
            title='Average Views per Video',
            axis=alt.Axis(
                format='~s',
                labelColor='#9bbcd6',
                grid=True,
                gridColor='#1c3d5a'
            )
        ),
        color=alt.Color(
            'avg_views:Q',
            scale=alt.Scale(scheme='turbo'),
            legend=alt.Legend(
                title='Avg Views',
                labelColor='#9bbcd6',
                titleColor='#9bbcd6'
            )
        ),
        tooltip=[
            alt.Tooltip('year:O', title='Year'),
            alt.Tooltip('uploads:Q', title='Uploads'),
            alt.Tooltip('avg_views:Q', title='Avg Views', format=',')
        ]
    )

    trend = alt.Chart(freq_perf_df).mark_line(
        color='#ffffff',
        strokeWidth=3
    ).encode(
        x='uploads:Q',
        y='avg_views:Q'
    )

    strategy_chart = (
        scatter + trend
    ).properties(
        height=420
    ).configure_view(
        strokeOpacity=0
    ).configure_axis(
        titleColor='#9bbcd6'
    )

    st.altair_chart(strategy_chart, use_container_width=True)

    st.caption(
    "📌 Insight: If views drop as uploads increase, focus on quality. "
    "If views rise with frequency, consistency is working."
    )
    best_day = day_df.sort_values("avg_views", ascending=False).iloc[0]["day_name"]
    best_hour = hour_df.sort_values("avg_views", ascending=False).iloc[0]["hour"]

    st.success(
        f"📊 **Winning Strategy:** Uploading on **{best_day}** around **{int(best_hour)}:00**"
        f"generally results in higher initial peak views for this channel."
    )
    