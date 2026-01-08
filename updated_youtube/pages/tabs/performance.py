import streamlit as st
import altair as alt
import analytics.analytics as analytics

def render(df):
    st.subheader("📈 Performance Analysis")

    # ==============================
    # 1. MONTHLY VIEWS DISTRIBUTION (Professional Area Chart)
    # ==============================
    st.markdown("### Monthly Views Trend")
    mv = analytics.monthly_views_styled(df)
    
    view_chart = alt.Chart(mv).mark_area(
        line={'color': '#1E90FF', 'size': 2}, 
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color='rgba(20, 123, 255, 0.3)', offset=1),
                   alt.GradientStop(color='rgba(30, 144, 255, 0.7)', offset=0)],
            x1=1, x2=1, y1=1, y2=0
        )
    ).encode(
        x=alt.X('period:T', title='', axis=alt.Axis(format="%b '%y", labelAngle=-45, grid=False)),
        y=alt.Y('views:Q', title='Views', axis=alt.Axis(format='~s', grid=True, gridDash=[2,2], gridColor='#1c3d5a')),
        tooltip=['period', alt.Tooltip('views', format=',')]
    ).properties(height=350).configure_view(strokeOpacity=0).configure_axis(labelColor='#9bbcd6', titleColor='#9bbcd6')

    st.altair_chart(view_chart, use_container_width=True)

    st.markdown("---")

    # =============================
    # 2. UPLOAD FREQUENCY (Solid Bar Chart - No Overlapping Lines)
    # ==============================
    st.markdown("### Monthly Upload Frequency")
    
    # ==============================
# DATA (UNCHANGED)
# ==============================
    freq_df = df.groupby(
        ['year', 'month_name', 'month']
    ).size().reset_index(name='uploads')

    freq_df = freq_df.sort_values(['year', 'month'])

# Create a readable label to avoid overlap across years
    freq_df['month_label'] = freq_df['month_name'] + " " + freq_df['year'].astype(str)

# ==============================
# COLORFUL BAR CHART
# ==============================
    bar_chart = alt.Chart(freq_df).mark_bar(
        cornerRadiusTopLeft=8,
        cornerRadiusTopRight=8,
    ).encode(
        x=alt.X(
            'month_label:N',
            sort=alt.SortField(field='year', order='ascending'),
            title=None,
            axis=alt.Axis(
                labelAngle=-45,
                labelColor='#9bbcd6'
            )
        ),
        y=alt.Y(
            'uploads:Q',
            title='No. of Uploads',
            axis=alt.Axis(
                grid=True,
                gridColor='#1c3d5a',
                labelColor='#9bbcd6'
            )
        ),
        color=alt.Color(
            'uploads:Q',
            scale=alt.Scale(
                scheme='turbo'  # 🔥 colorful & expressive
            ),
            legend=alt.Legend(
                title='Upload Intensity',
                labelColor='#9bbcd6',
                titleColor='#9bbcd6'
            )
        ),
        tooltip=[
            alt.Tooltip('month_name:N', title='Month'),
            alt.Tooltip('year:O', title='Year'),
            alt.Tooltip('uploads:Q', title='Uploads')
        ]
    ).properties(
        height=380
    ).configure_view(
        strokeOpacity=0
    ).configure_axis(
        titleColor='#9bbcd6'
    )

    st.altair_chart(bar_chart, use_container_width=True)


    # =============================
    # 3. AVERAGE VIEWS PER MONTH (Matching Area Chart)
    # ==============================
    st.markdown("### Average Views per Video")

# ==============================
# DATA (UNCHANGED)
# ==============================
    avg_v_df = df.groupby(
        ['year', 'month_name', 'month']
    )['views'].mean().reset_index(name='avg_views')

    avg_v_df = avg_v_df.sort_values(['year', 'month'])

# Create label to avoid month overlap across years
    avg_v_df['month_label'] = avg_v_df['month_name'] + " " + avg_v_df['year'].astype(str)

# ==============================
# LINE (PRIMARY FOCUS)
# ==============================
    avg_line = alt.Chart(avg_v_df).mark_line(
        point=True,
        strokeWidth=4,
        color="#4cc3ff",
        interpolate="monotone"
    ).encode(
        x=alt.X(
            'month_label:N',
            title=None,
            axis=alt.Axis(
                labelAngle=-45,
                labelColor='#9bbcd6'
            )
        ),
        y=alt.Y(
            'avg_views:Q',
            title='Avg. Views',
            axis=alt.Axis(
                format='~s',
                grid=True,
                gridColor='#1c3d5a',
                gridDash=[3, 3],
                labelColor='#9bbcd6'
            )
        ),
        tooltip=[
            alt.Tooltip('month_name:N', title='Month'),
            alt.Tooltip('year:O', title='Year'),
            alt.Tooltip('avg_views:Q', title='Avg Views', format=',')
        ]
    )

# ==============================
# AREA (SUBTLE DEPTH)
# ==============================
    avg_area = alt.Chart(avg_v_df).mark_area(
    interpolate='monotone',
    color=alt.Gradient(
        gradient='linear',
        stops=[
            alt.GradientStop(color='rgba(76, 195, 255, 0.45)', offset=0),
            alt.GradientStop(color='rgba(76, 195, 255, 0.05)', offset=1),
        ],
        x1=0, x2=0, y1=0, y2=1
    )
    ).encode(
        x='month_label:N',
        y='avg_views:Q'
    )

# ==============================
# COMBINED CHART
# ==============================
    avg_chart = (
        avg_area + avg_line
    ).properties(
        height=420
    ).configure_view(
        strokeOpacity=0
    ).configure_axis(
        titleColor='#9bbcd6'
    )

    st.altair_chart(avg_chart, use_container_width=True)
