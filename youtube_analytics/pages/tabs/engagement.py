import streamlit as st
import altair as alt
import pandas as pd
import analytics.analytics as analytics

def render(df):
    # ==============================
    # 1. PREMIUM CSS & ANIMATIONS
    # ==============================
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

        /* Main Container Animation */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .eng-container {
            animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            font-family: 'Inter', sans-serif;
        }

        /* Top Metric Cards */
        .eng-metric-card {
            background: rgba(13, 22, 31, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 18px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(139, 144, 150, 0.4);
            transition: all 0.3s ease;
        }
        .eng-metric-card:hover {
            border-color: #00e5ff; 
            
            transform: translateY(-5px);
            
            background: rgba(20, 36, 51, 0.9);
        }
        .eng-metric-label {
            color: #94a3b8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 10px;
        }
        .eng-metric-value {
            color: white; font-size: 1.8rem; font-weight: 800;
            background: linear-gradient(90deg, #ffffff, #00e5ff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }

        /* THE 2x2 DISTRIBUTION GRID CARDS */
        .dist-square-item {
            background: rgba(13, 22, 31, 0.8);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: 0.3s;
            margin-bottom: 15px;
            height: 140px; /* Fixed height for neatness */
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 8px 24px rgba(22, 172 ,170,0.3);
        } 
        .dist-square-item:hover { 
            border-color: #00e5ff; 
            background: rgba(13, 22, 31, 1);
            transform: scale(1.02);
        }
        
        .dist-dot-row { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
        .dot { width: 10px; height: 10px; border-radius: 50%; }
        .dist-cat-name { color: #94a3b8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }
        .dist-main-pct { color: white; font-size: 1.8rem; font-weight: 800; }
        .dist-sub-count { color: #00e5ff; font-size: 0.85rem; font-weight: 600; opacity: 0.9; }

        hr { border: none; height: 1px; background: rgba(255,255,255,0.05); margin: 40px 0; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="eng-container">', unsafe_allow_html=True)

    # ==============================
    # HEADER
    # ==============================
    st.markdown("""
    <div style="margin-bottom:30px;">
        <h2 style="font-weight:800; color:white; font-size:2.2rem;margin-left:499px;">💬 Engagement Analysis</h2>
        <p style="color:#94a3b8; font-size:1rem;margin-left:497px;">Understand how your audience interacts with your content</p>
    </div>
    """, unsafe_allow_html=True)

    # ==============================
    # TOP KEY METRICS 
    # ==============================
    avg_eng = round(df["engagement_rate"].mean(), 4)
    total_likes = int(df["likes"].sum())
    total_comments = int(df["comments"].sum())
    avg_likes = int(df["likes"].mean())
    
    m1, m2, m3, m4 = st.columns(4)
    metrics_data = [
        ("Avg Engagement Rate", f"{avg_eng}"),
        ("Total Likes", f"{total_likes:,}"),
        ("Total Comments", f"{total_comments:,}"),
        ("Avg Likes/Video", f"{avg_likes:,}")
    ]

    cols = [m1, m2, m3, m4]
    for i, (label, val) in enumerate(metrics_data):
        cols[i].markdown(f"""
            <div class="eng-metric-card">
                <div class="eng-metric-label">{label}</div>
                <div class="eng-metric-value">{val}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div style="margin-top:10px; color:#64748b; font-size:0.8rem;">💡 <b>Engagement Rate</b> = (Likes + Comments) / Views</div>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # ==============================
    # 1. LIKES VS COMMENTS CORRELATION
    # ==============================
    st.markdown("### 📊 Likes vs Comments Correlation")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    scatter_chart = alt.Chart(df).mark_circle(size=100, opacity=0.7).encode(
        x=alt.X('likes:Q', title='Likes', axis=alt.Axis(format='~s', labelColor='#94a3b8', gridColor='#1a2733')),
        y=alt.Y('comments:Q', title='Comments', axis=alt.Axis(format='~s', labelColor='#94a3b8', gridColor='#1a2733')),
        color=alt.Color('engagement_rate:Q', scale=alt.Scale(scheme='redyellowgreen'), legend=alt.Legend(title='ER')),
        tooltip=['title', 'likes', 'comments', 'engagement_rate']
    ).properties(height=400)
    
    st.altair_chart(scatter_chart, use_container_width=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)

    # ==============================
    # 2. PIE CHART & 2x2 SQUARE GRID (FIXED)
    # ==============================
    st.markdown("### 🥧 Engagement Distribution")
    st.markdown("<hr>", unsafe_allow_html=True)
    df_copy = df.copy()
    df_copy['engagement_category'] = pd.cut(
        df_copy['engagement_rate'],
        bins=[0, 0.01, 0.03, 0.05, float('inf')],
        labels=['Low (0-1%)', 'Medium (1-3%)', 'High (3-5%)', 'Very High (5%+)']
    )
    dist_df = df_copy['engagement_category'].value_counts().reindex(['Low (0-1%)', 'Medium (1-3%)', 'High (3-5%)', 'Very High (5%+)']).reset_index()
    dist_df.columns = ['category', 'count']
    total_vids = dist_df['count'].sum()

    col_pie, col_grid_wrapper = st.columns([1.2, 1.8])

    with col_pie:
        pie = alt.Chart(dist_df).mark_arc(innerRadius=60, outerRadius=115).encode(
            theta='count:Q',
            color=alt.Color('category:N', scale=alt.Scale(range=['#FF6B6B', '#FFD93D', '#4ECDC4', '#45B7D1']), legend=None),
            tooltip=['category', 'count']
        ).properties(height=300)
        st.altair_chart(pie, use_container_width=True)

    with col_grid_wrapper:
        colors = ['#FF6B6B', '#FFD93D', '#4ECDC4', '#45B7D1']
        
        # We use two rows of columns to create a stable 2x2 grid
        row1_col1, row1_col2 = st.columns(2)
        row2_col1, row2_col2 = st.columns(2)
        
        grid_cols = [row1_col1, row1_col2, row2_col1, row2_col2]
        
        for i, row in dist_df.iterrows():
            pct = (row['count'] / total_vids) * 100 if total_vids > 0 else 0
            with grid_cols[i]:
                st.markdown(f"""
                <div class="dist-square-item">
                    <div class="dist-dot-row">
                        <div class="dot" style="background: {colors[i]}"></div>
                        <div class="dist-cat-name">{row['category']}</div>
                    </div>
                    <div class="dist-main-pct">{pct:.1f}%</div>
                    <div class="dist-sub-count">{int(row['count'])} Videos</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ==============================
    # 3. VIEWS VS ENGAGEMENT RATE
    # ==============================
    st.markdown("### 📈 Views vs Engagement Rate")
    st.markdown("<hr>", unsafe_allow_html=True)
    views_eng_chart = alt.Chart(df).mark_circle(size=100, opacity=0.7).encode(
        x=alt.X('views:Q', title='Views', axis=alt.Axis(format='~s', labelColor='#94a3b8', gridColor='#1a2733')),
        y=alt.Y('engagement_rate:Q', title='ER', axis=alt.Axis(format='.4f', labelColor='#94a3b8', gridColor='#1a2733')),
        color=alt.Color('likes:Q', scale=alt.Scale(scheme='blues')),
        tooltip=['title', 'views', 'engagement_rate']
    ).properties(height=400)
    st.altair_chart(views_eng_chart, use_container_width=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)

    # ==============================
    # 4. MONTHLY TREND
    # ==============================
    st.markdown("### 📅 Monthly Engagement Trend")
    st.markdown("<hr>", unsafe_allow_html=True)
    monthly_eng = df.groupby(['year', 'month_name', 'month'])['engagement_rate'].mean().reset_index().sort_values(['year', 'month'])
    monthly_eng['month_label'] = monthly_eng['month_name'] + " " + monthly_eng['year'].astype(str)

    line = alt.Chart(monthly_eng).mark_line(point=True, strokeWidth=4, color='#00e5ff', interpolate='monotone').encode(
        x=alt.X('month_label:N', title=None, axis=alt.Axis(labelAngle=-45, labelColor='#94a3b8')),
        y=alt.Y('engagement_rate:Q', title='Avg ER', axis=alt.Axis(format='.4f', labelColor='#94a3b8', gridColor='#1a2733')),
        tooltip=['month_name', 'year', 'engagement_rate']
    )
    
    area = alt.Chart(monthly_eng).mark_area(
        interpolate='monotone',
        color=alt.Gradient(gradient='linear', stops=[alt.GradientStop(color='rgba(0, 229, 255, 0.7)', offset=0), alt.GradientStop(color='transparent', offset=1)], x1=0, x2=0, y1=0, y2=1)
    ).encode(x='month_label:N', y='engagement_rate:Q')

    st.altair_chart((area + line).properties(height=400), use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)