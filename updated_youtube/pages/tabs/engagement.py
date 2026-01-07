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
    
    # Categorize videos by engagement rate
    df_copy = df.copy()
    df_copy['engagement_category'] = pd.cut(
        df_copy['engagement_rate'],
        bins=[0, 0.01, 0.03, 0.05, float('inf')],
        labels=['Low (0-1%)', 'Medium (1-3%)', 'High (3-5%)', 'Very High (5%+)']
    )
    
    engagement_dist = df_copy['engagement_category'].value_counts().reset_index()
    engagement_dist.columns = ['category', 'count']
    
    col_pie, col_info = st.columns([2, 1])
    
    with col_pie:
        pie_chart = alt.Chart(engagement_dist).mark_arc(
            innerRadius=60,
            outerRadius=150
        ).encode(
            theta=alt.Theta('count:Q', stack=True),
            color=alt.Color('category:N',
                          scale=alt.Scale(domain=['Low (0-1%)', 'Medium (1-3%)', 'High (3-5%)', 'Very High (5%+)'],
                                        range=['#FF6B6B', '#FFD93D', '#4ECDC4', '#45B7D1']),
                          legend=alt.Legend(title='Engagement Level', labelColor='#9bbcd6', titleColor='#9bbcd6')),
            tooltip=['category', alt.Tooltip('count:Q', title='Videos')]
        ).properties(height=400, width=400)
        
        st.altair_chart(pie_chart, use_container_width=True)
    
    with col_info:
        st.markdown("### 📊 Distribution")
        total = engagement_dist['count'].sum()
        for _, row in engagement_dist.iterrows():
            pct = (row['count'] / total) * 100
            st.markdown(f"""
            <div class="engagement-stat-card">
                <div class="engagement-category">{row['category']}</div>
                <div class="engagement-count">{int(row['count'])} videos</div>
                <div class="engagement-pct">{pct:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")

    # ==============================
    # 4. MONTHLY ENGAGEMENT TREND
    # ==============================
    st.markdown("### 📅 Monthly Engagement Trend")
    
    monthly_eng = df.groupby(['year', 'month_name', 'month'])['engagement_rate'].mean().reset_index()
    monthly_eng = monthly_eng.sort_values(['year', 'month'])
    
    trend_chart = alt.Chart(monthly_eng).mark_line(
        point=True,
        strokeWidth=3,
        color='#FF4444'
    ).encode(
        x=alt.X('month_name:N', sort=alt.SortField('month'), title='Month', axis=alt.Axis(labelAngle=0, labelColor='#9bbcd6')),
        y=alt.Y('engagement_rate:Q', title='Avg Engagement Rate', axis=alt.Axis(format='.4f', labelColor='#9bbcd6', gridColor='#1c3d5a')),
        tooltip=['month_name', alt.Tooltip('engagement_rate:Q', format='.4f')]
    ).properties(height=350)
    
    area_trend = alt.Chart(monthly_eng).mark_area(
        color=alt.Gradient(
            gradient='linear',
            stops=[
                alt.GradientStop(color='rgba(255, 68, 68, 0.6)', offset=0),
                alt.GradientStop(color='rgba(255, 68, 68, 0.1)', offset=1)
            ],
            x1=0, x2=0, y1=0, y2=1
        )
    ).encode(
        x=alt.X('month_name:N', sort=alt.SortField('month')),
        y=alt.Y('engagement_rate:Q')
    ).properties(height=350)
    
    final_trend = (area_trend + trend_chart).resolve_scale().configure_view(strokeOpacity=0).configure_axis(titleColor='#9bbcd6')
    
    st.altair_chart(final_trend, use_container_width=True)