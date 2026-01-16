import streamlit as st
import analytics.analytics as analytics

def format_compact(num):
    if num >= 1_000_000_000: return f'{num / 1_000_000_000:.1f}B'
    if num >= 1_000_000: return f'{num / 1_000_000:.1f}M'
    if num >= 1_000: return f'{num / 1_000:.1f}K'
    return str(num)

def render(df, channel_id, channels_df):
    # --- INTERNAL CSS ---
    st.markdown("""
    <style>
        .metric-container {
            background: #0d161f;
            border: 1px solid #1a2733;
            border-radius: 16px;
            padding: 35px 20px;
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: 0 10px 30px rgba(6, 159, 177, 0.4);
        }
        .metric-container:hover {
            border-color: #00e5ff;
            transform: translateY(-5px);
        }
        .m-label { color: #94a3b8; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; }
        .m-value { color: #00e5ff; font-size: 2.6rem; font-weight: 800; }

        .video-box {
            background: #0d161f;
            border: 1px solid #1a2733;
            border-radius: 12px;
            overflow: hidden;
            transition: 0.3s;
        }
        .video-box:hover { border-color: #00e5ff; }
        
        .slider-btn button {
            border-radius: 50% !important;
            width: 44px !important; height: 44px !important;
            background: rgba(255,255,255,0.05) !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # 1. METRICS
    ch_row = channels_df[channels_df['channel_id'] == channel_id]
    if not ch_row.empty:
        ch_data = ch_row.iloc[0]
        m1, m2, m3, m4 = st.columns(4)
        
        metrics = [
            ("Subscribers", format_compact(ch_data.get('subscribers', 0))),
            ("Avg Views", format_compact(int(df["views"].mean()))),
            ("Total Videos", len(df)),
            ("Avg Likes", format_compact(int(df["likes"].mean())))
        ]
        
        cols = [m1, m2, m3, m4]
        for i, (label, val) in enumerate(metrics):
            cols[i].markdown(f'<div class="metric-container"><div class="m-label">{label}</div><div class="m-value">{val}</div></div>', unsafe_allow_html=True)

    # 2. SLIDER
    st.markdown("<h2 style='margin-top:70px;margin-bottom:20px;'>📹 Latest Content</h2>", unsafe_allow_html=True)
    if 'slide_idx' not in st.session_state: st.session_state.slide_idx = 0
    
    recent_vids = df.sort_values("published_date", ascending=False).head(16)
    c_prev, c_main, c_next = st.columns([0.5, 11, 0.5])
    
    with c_prev:
        st.write("<div style='height:100px;'></div>", unsafe_allow_html=True)
        if st.button("〈", key="p_btn"):
            if st.session_state.slide_idx > 0:
                st.session_state.slide_idx -= 1
                st.rerun()
    with c_next:
        st.write("<div style='height:100px;'></div>", unsafe_allow_html=True)
        if st.button("〉", key="n_btn"):
            if st.session_state.slide_idx < len(recent_vids) - 4: 
                st.session_state.slide_idx += 1 
                st.rerun()
    
    with c_main:
        idx = st.session_state.slide_idx
        v_cols = st.columns(4)
        vids = recent_vids.iloc[idx:idx+4]
        for i, (_, video) in enumerate(vids.iterrows()):
            with v_cols[i]:
                thumb = f"https://i.ytimg.com/vi/{video['video_id']}/mqdefault.jpg"
                st.markdown(f"""
                <div class="video-box">
                    <img src="{thumb}" style="width:100%;">
                    <div style="padding:15px;">
                        <div style="color:white; font-size:13px; font-weight:600; height:40px; overflow:hidden;">{video['title']}</div>
                        <div style="color:#94a3b8; font-size:11px; margin-top:8px;">▶ {format_compact(video['views'])} · {video['published_date'].strftime('%b %d')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # 3. TABLES
    st.markdown("<br><br>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🔥 Top Views", "❤️ Top Likes", "📊 Top Engagement"])
     
    with t1:
        st.dataframe(analytics.top_videos_by_views(df, 10), use_container_width=True, hide_index=True)
    with t2:
        st.dataframe(analytics.top_videos_by_likes(df, 10), use_container_width=True, hide_index=True)
    with t3:
        st.dataframe(analytics.top_videos_by_engagement(df, 10), use_container_width=True, hide_index=True)  