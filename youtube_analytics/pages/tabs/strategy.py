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

        /* Container Animation */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .strategy-container {
            animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            font-family: 'Inter', sans-serif;
        }

        /* Strategy Metric Cards */
        .stat-card {
            background: rgba(13, 22, 31, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 18px; 
            padding: 25px;
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: 0 10px 30px rgba(139, 144, 150, 0.4);
        }
        .stat-card:hover {
            border-color: #00e5ff;
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 229, 255, 0.1);
        }
        .stat-label { color: #94a3b8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 10px; }
        .stat-value { color: #00e5ff; font-size: 1.8rem; font-weight: 800; }


        /* Table Custom Styling */
        div[data-testid="stDataFrame"] {
            border-radius: 15px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        hr { border: none; height: 1px; background: rgba(255,255,255,0.05); margin: 40px 0; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="strategy-container">', unsafe_allow_html=True)

    # ==============================
    # 2. HEADER
    # ==============================
    st.markdown("""
       <div style="margin-bottom:30px;">
        <h2 style="font-weight:800; color:white; font-size:2.2rem;margin-left:499px;">🎯 Content Strategy</h2>
        <p style="color:#94a3b8; font-size:1rem;margin-left:480px;">Optimization recommendations based on historical peak performance times.t</p>
    </div>
    """, unsafe_allow_html=True)
    

    # ==============================
    # 3. WINNING STRATEGY METRICS
    # ==============================
    day_df = df.groupby("day_name")["views"].mean().reset_index(name="avg_views")
    hour_df = df.groupby("hour")["views"].mean().reset_index(name="avg_views")
    
    best_day = day_df.sort_values("avg_views", ascending=False).iloc[0]["day_name"]
    best_hour = hour_df.sort_values("avg_views", ascending=False).iloc[0]["hour"]
    avg_monthly_uploads = df.groupby(['year', 'month'])['video_id'].count().mean()

    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Best Day</div><div class="stat-value">{best_day}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Prime Hour</div><div class="stat-value">{int(best_hour)}:00</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Avg Frequency</div><div class="stat-value">{int(avg_monthly_uploads)} / Mo</div></div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ==============================
    # 4. BEST DAY CHART (BARS)
    # ==============================
    st.markdown("### 📅 Weekly Performance Hub")
    st.markdown("<hr>", unsafe_allow_html=True)
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    day_chart = alt.Chart(day_df).mark_bar(cornerRadiusTopLeft=10, cornerRadiusTopRight=10).encode(
        x=alt.X('day_name:N', sort=day_order, title=None, axis=alt.Axis(labelAngle=0, labelColor='#94a3b8')),
        y=alt.Y('avg_views:Q', title='Avg Views', axis=alt.Axis(format='~s', labelColor='#94a3b8', gridColor='#1a2733')),
        color=alt.Color('avg_views:Q', scale=alt.Scale(scheme='blues'), legend=None),
        tooltip=['day_name', 'avg_views']
    ).properties(height=350).configure_view(strokeOpacity=0)

    st.altair_chart(day_chart, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ==============================
    # 5. BEST HOUR CHART (LINE/AREA)
    # ==============================
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### ⏰ Hourly Traffic Analysis", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    line = alt.Chart(hour_df).mark_line(point=True, strokeWidth=6, color='#00e5ff', interpolate='monotone').encode(
        x=alt.X('hour:O', title='Hour (24h)', axis=alt.Axis(labelColor='#94a3b8', grid=False)),
        y=alt.Y('avg_views:Q', title='Views', axis=alt.Axis(format='~s', labelColor='#94a3b8', gridColor='#1a2733')),
        tooltip=['hour', 'avg_views']
    )
    
    area = alt.Chart(hour_df).mark_area(
        interpolate='monotone',
        color=alt.Gradient(gradient='linear', stops=[alt.GradientStop(color='rgba(0, 229, 255, 0.5)', offset=0.3), alt.GradientStop(color='transparent', offset=0.9)], x1=0, x2=0, y1=0, y2=1)
    ).encode(x='hour:O', y='avg_views:Q')

    st.altair_chart((area + line).properties(height=350), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ==============================
    # 6. TABLE: PEAK SLOTS (Styled Table)
    # ==============================
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 🏆 Peak Performance Matrix", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Calculate views by Day + Hour for a Heatmap-style table
    pivot_df = df.groupby(['day_name', 'hour'])['views'].mean().reset_index()
    top_slots = pivot_df.sort_values("views", ascending=False).head(10)
    top_slots.columns = ["Day", "Hour (UTC)", "Average Predicted Views"]
    
    st.markdown('<div style="margin-bottom:15px; color:#94a3b8;">Top 10 recommended historical upload slots for this channel:</div>', unsafe_allow_html=True)
    st.dataframe(top_slots, use_container_width=True, hide_index=True)

    # ==============================
    # 7. FREQUENCY VS PERFORMANCE
    # ==============================
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 📊 Consistency vs. Reach")
    st.markdown("<hr>", unsafe_allow_html=True)
    freq_perf_df = df.groupby(['year', 'month']).agg(uploads=('video_id', 'count'), avg_views=('views', 'mean')).reset_index()

    scatter = alt.Chart(freq_perf_df).mark_circle(size=140, opacity=0.8).encode(
        x=alt.X('uploads:Q', title='Uploads per Month', axis=alt.Axis(labelColor='#94a3b8')),
        y=alt.Y('avg_views:Q', title='Avg Views/Video', axis=alt.Axis(format='~s', labelColor='#94a3b8', gridColor='#1a2733')),
        color=alt.Color('avg_views:Q', scale=alt.Scale(scheme='tealblues'), legend=None),
        tooltip=['year', 'uploads', 'avg_views']
    ).properties(height=400)
    st.altair_chart(scatter, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # End strategy-container