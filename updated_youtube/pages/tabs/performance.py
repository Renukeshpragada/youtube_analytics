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
        line={'color': '#1E90FF', 'size': 3}, 
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color='#1E90FF', offset=1),
                   alt.GradientStop(color='rgba(30, 144, 255, 0.1)', offset=0)],
            x1=1, x2=1, y1=1, y2=0
        )
    ).encode(
        x=alt.X('period:T', title='', axis=alt.Axis(format="%b '%y", labelAngle=-45, grid=False)),
        y=alt.Y('views:Q', title='Views', axis=alt.Axis(format='~s', grid=True, gridDash=[2,2], gridColor='#1c3d5a')),
        tooltip=['period', alt.Tooltip('views', format=',')]
    ).properties(height=350).configure_view(strokeOpacity=0).configure_axis(labelColor='#9bbcd6', titleColor='#9bbcd6')

    st.altair_chart(view_chart, use_container_width=True)

    st.markdown("---")

    # ==============================
    # 2. UPLOAD FREQUENCY (Solid Bar Chart - No Overlapping Lines)
    # ==============================
    st.markdown("### Monthly Upload Frequency")
    
    # We group by month_name and count video IDs
    freq_df = df.groupby(['year', 'month_name', 'month']).size().reset_index(name='uploads')
    freq_df = freq_df.sort_values(['year', 'month'])

    bar_chart = alt.Chart(freq_df).mark_bar(
        color='#4cc3ff',
        cornerRadiusTopLeft=8,  # Smooth corners like Image 2
        cornerRadiusTopRight=8,
        opacity=0.9
    ).encode(
        x=alt.X('month_name:N', sort=alt.SortField('month'), title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y('uploads:Q', title='No. of Uploads', axis=alt.Axis(grid=True, gridColor='#1c3d5a')),
        tooltip=['month_name', 'uploads']
    ).properties(height=300).configure_view(strokeOpacity=0)

    st.altair_chart(bar_chart, use_container_width=True)

    st.markdown("---")

    # ==============================
    # 3. AVERAGE VIEWS PER MONTH (Matching Area Chart)
    # ==============================
    st.markdown("### Average Views per Video")
    
    # Aggregate to get average views per month
    avg_v_df = df.groupby(['year', 'month_name', 'month'])['views'].mean().reset_index(name='avg_views')
    avg_v_df = avg_v_df.sort_values(['year', 'month'])

    avg_chart = alt.Chart(avg_v_df).mark_area(
        line={'color': '#4cc3ff', 'size': 3},
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color='rgba(76, 195, 255, 0.4)', offset=1),
                   alt.GradientStop(color='rgba(76, 195, 255, 0)', offset=0)],
            x1=1, x2=1, y1=1, y2=0
        )
    ).encode(
        x=alt.X('month_name:N', sort=alt.SortField('month'), title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y('avg_views:Q', title='Avg. Views', axis=alt.Axis(grid=True, gridColor='#1c3d5a')),
        tooltip=['month_name', alt.Tooltip('avg_views', format=',')]
    ).properties(height=300).configure_view(strokeOpacity=0)

    st.altair_chart(avg_chart, use_container_width=True)