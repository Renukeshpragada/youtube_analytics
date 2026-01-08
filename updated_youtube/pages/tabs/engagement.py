import streamlit as st
import altair as alt
import pandas as pd
import analytics.analytics as analytics

def render(df):
    st.markdown("""
    <div class="section-header">
        <h2>💬 Engagement Analysis</h2>
        <p>Understand how your audience interacts with your content</p>
    </div>
    """, unsafe_allow_html=True)

    # ==============================
    # KEY METRICS
    # ==============================
    avg_eng = round(df["engagement_rate"].mean(), 4)
    total_likes = int(df["likes"].sum())
    total_comments = int(df["comments"].sum())
    avg_likes = int(df["likes"].mean())
    avg_comments = int(df["comments"].mean())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="overview-card">
            <div class="overview-card-label">Avg Engagement Rate</div>
            <div class="overview-card-value">{avg_eng}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="overview-card">
            <div class="overview-card-label">Total Likes</div>
            <div class="overview-card-value">{total_likes:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="overview-card">
            <div class="overview-card-label">Total Comments</div>
            <div class="overview-card-value">{total_comments:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="overview-card">
            <div class="overview-card-label">Avg Likes/Video</div>
            <div class="overview-card-value">{avg_likes:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.caption("💡 Engagement Rate = (Likes + Comments) / Views")
    st.markdown("---")

    # ==============================
    # 1. LIKES VS COMMENTS SCATTER (Colorful)
    # ==============================
    st.markdown("### 📊 Likes vs Comments Correlation")
    
    scatter_chart = alt.Chart(df).mark_circle(
        size=100,
        opacity=0.7
    ).encode(
        x=alt.X('likes:Q', title='Likes', axis=alt.Axis(format='~s', labelColor='#9bbcd6', gridColor='#1c3d5a')),
        y=alt.Y('comments:Q', title='Comments', axis=alt.Axis(format='~s', labelColor='#9bbcd6', gridColor='#1c3d5a')),
        color=alt.Color('engagement_rate:Q',
                        scale=alt.Scale(scheme='redyellowgreen', domain=[df['engagement_rate'].min(), df['engagement_rate'].max()]),
                        legend=alt.Legend(title='Engagement Rate', labelColor='#9bbcd6', titleColor='#9bbcd6')),
        tooltip=['title', alt.Tooltip('likes:Q', format=','), alt.Tooltip('comments:Q', format=','), alt.Tooltip('engagement_rate:Q', format='.4f')]
    ).properties(height=400).configure_view(strokeOpacity=0).configure_axis(titleColor='#9bbcd6')
    
    st.altair_chart(scatter_chart, use_container_width=True)
    
    st.markdown("---")

    # ==============================
    # 2. VIEWS VS ENGAGEMENT RATE SCATTER
    # ==============================
    st.markdown("### 📈 Views vs Engagement Rate")
    
    views_eng_chart = alt.Chart(df).mark_circle(
        size=100,
        opacity=0.7
    ).encode(
        x=alt.X('views:Q', title='Views', axis=alt.Axis(format='~s', labelColor='#9bbcd6', gridColor='#1c3d5a')),
        y=alt.Y('engagement_rate:Q', title='Engagement Rate', axis=alt.Axis(format='.4f', labelColor='#9bbcd6', gridColor='#1c3d5a')),
        color=alt.Color('likes:Q',
                        scale=alt.Scale(scheme='blues', domain=[df['likes'].min(), df['likes'].max()]),
                        legend=alt.Legend(title='Likes', labelColor='#9bbcd6', titleColor='#9bbcd6')),
        tooltip=['title', alt.Tooltip('views:Q', format=','), alt.Tooltip('engagement_rate:Q', format='.4f'), alt.Tooltip('likes:Q', format=',')]
    ).properties(height=400).configure_view(strokeOpacity=0).configure_axis(titleColor='#9bbcd6')
    
    st.altair_chart(views_eng_chart, use_container_width=True)
    
    st.info("💡 **Insight:** High views + high engagement indicates viral content. Low engagement despite high views suggests passive audience.")
    
    st.markdown("---")

    # ==============================
    # 3. ENGAGEMENT DISTRIBUTION PIE CHART
    # ==============================
    st.markdown("### 🥧 Engagement Distribution")

# ==============================
# DATA (UNCHANGED)
# ==============================
    df_copy = df.copy()
    df_copy['engagement_category'] = pd.cut(
        df_copy['engagement_rate'],
        bins=[0, 0.01, 0.03, 0.05, float('inf')],
        labels=['Low (0-1%)', 'Medium (1-3%)', 'High (3-5%)', 'Very High (5%+)']
    )

    engagement_dist = df_copy['engagement_category'].value_counts().reset_index()
    engagement_dist.columns = ['category', 'count']

# ==============================
# LAYOUT: PIE | DISTRIBUTION
# ==============================
    col_pie, col_dist = st.columns([1.2, 1.8])

# ---------- PIE (SMALLER & CLEAN) ----------
    with col_pie:
        pie_chart = alt.Chart(engagement_dist).mark_arc(
            innerRadius=45,
            outerRadius=110
        ).encode(
            theta=alt.Theta('count:Q', stack=True),
            color=alt.Color(
                'category:N',
                scale=alt.Scale(
                    domain=[
                        'Low (0-1%)',
                        'Medium (1-3%)',
                        'High (3-5%)',
                        'Very High (5%+)'
                    ],
                    range=['#FF6B6B', '#FFD93D', '#4ECDC4', '#45B7D1']
                ),
                legend=None
            ),
            tooltip=[
                alt.Tooltip('category:N', title='Category'),
                alt.Tooltip('count:Q', title='Videos')
            ]
        ).properties(
            height=350,
            width=470
        ).configure_view(strokeOpacity=0)

        st.altair_chart(pie_chart, use_container_width=False)

# ---------- DISTRIBUTION (2 ITEMS PER ROW) ----------
    with col_dist:
        st.markdown("### 📊 Distribution")
        total = engagement_dist['count'].sum()

        grid = st.columns(2)
        for i, row in engagement_dist.iterrows():
            pct = (row['count'] / total) * 100
            with grid[i % 2]:
                st.markdown(
                    f"""
                    <div class="engagement-stat-card">
                        <div class="engagement-category">{row['category']}</div>
                        <div class="engagement-count">{int(row['count'])} videos</div>
                        <div class="engagement-pct">{pct:.1f}%</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.markdown("---")


    # ==============================
    # 4. MONTHLY ENGAGEMENT TREND
    # ==============================
    st.markdown("### 📅 Monthly Engagement Trend")

# ==============================
# DATA (UNCHANGED)
# ==============================
    monthly_eng = (
        df.groupby(['year', 'month_name', 'month'])['engagement_rate']
        .mean()
        .reset_index()
        .sort_values(['year', 'month'])
    )

# Create a clear label to avoid overlap across years
    monthly_eng['month_label'] = (
        monthly_eng['month_name'] + " " + monthly_eng['year'].astype(str)
    )

# ==============================
# LINE (PRIMARY FOCUS)
# ==============================
    trend_line = alt.Chart(monthly_eng).mark_line(
        point=True,
        strokeWidth=4,
        color='#FF4444',
        interpolate='monotone'
    ).encode(
        x=alt.X(
            'month_label:N',
            title=None,
            axis=alt.Axis(
                labelAngle=-45,
                labelColor='#9bbcd6',
                grid=False
            )
        ),
        y=alt.Y(
            'engagement_rate:Q',
            title='Avg Engagement Rate',
            axis=alt.Axis(
                format='.4f',
                labelColor='#9bbcd6',
                grid=True,
                gridColor='#1c3d5a',
                gridDash=[3, 3]
            )
        ),
        tooltip=[
            alt.Tooltip('month_name:N', title='Month'),
            alt.Tooltip('year:O', title='Year'),
            alt.Tooltip('engagement_rate:Q', title='Engagement Rate', format='.4f')
        ]
    )

# ==============================
# AREA (SUBTLE DEPTH)
# ==============================
    trend_area = alt.Chart(monthly_eng).mark_area(
        interpolate='monotone',
        color=alt.Gradient(
            gradient='linear',
            stops=[
                alt.GradientStop(color='rgba(255, 68, 68, 0.45)', offset=0),
                alt.GradientStop(color='rgba(255, 68, 68, 0.05)', offset=1)
            ],
            x1=0, x2=0, y1=0, y2=1
        )
    ).encode(
        x='month_label:N',
        y='engagement_rate:Q'
    )

# ==============================
# FINAL COMBINED CHART
# ==============================
    final_trend = (
        trend_area + trend_line
    ).properties(
        height=420
    ).configure_view(
        strokeOpacity=0
    ).configure_axis(
        titleColor='#9bbcd6'
    )

    st.altair_chart(final_trend, use_container_width=True)
