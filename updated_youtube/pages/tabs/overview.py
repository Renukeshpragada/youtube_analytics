import streamlit as st
import analytics.analytics as analytics

def format_compact(num):
    if num >= 1_000_000_000: return f'{num / 1_000_000_000:.1f}B'
    if num >= 1_000_000: return f'{num / 1_000_000:.1f}M'
    if num >= 1_000: return f'{num / 1_000:.1f}K'
    return str(num)

def render(df, channel_id, channels_df):
    # --- 1. METRIC CARDS ---
    ch_row = channels_df[channels_df['channel_id'] == channel_id]

    if ch_row.empty:
        st.info("Channel metadata is still syncing. Please wait a moment…")
        return

    ch_data = ch_row.iloc[0]

    c1, c2, c3,c4 = st.columns(4)
    with c1:
        val = format_compact(ch_data.get('subscribers', 0))
        st.markdown(f'<div class="overview-card"><div class="overview-card-label">Subscribers</div><div class="overview-card-value">{val}</div></div>', unsafe_allow_html=True)
    with c2:
        val = format_compact(int(df["views"].mean()))
        st.markdown(f'<div class="overview-card"><div class="overview-card-label">Average Views</div><div class="overview-card-value">{val}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="overview-card"><div class="overview-card-label">Total Videos</div><div class="overview-card-value">{len(df)}</div></div>', unsafe_allow_html=True)
    with c4:
        val = format_compact(int(df["likes"].mean()))
        st.markdown(f'<div class="overview-card"><div class="overview-card-label">Avg likes</div><div class="overview-card-value">{val}</div></div>', unsafe_allow_html=True)
    # --- 2. THE DYNAMIC SLIDER ---
    st.markdown("### 📽️ Latest Published Videos")
    
    if 'slide_idx' not in st.session_state:
        st.session_state.slide_idx = 0

    recent_vids = df.sort_values("published_date", ascending=False).head(16)
    
    # 3-part layout: [Left Button, Cards, Right Button]
    col_l, col_content, col_r = st.columns([0.6, 11, 0.6])

    with col_l:
        # Transparent vertical adjustment is handled via CSS "top" property
        if st.button("〈", key="slider_l"):
            if st.session_state.slide_idx > 0:
                st.session_state.slide_idx -= 1

    with col_r:
        if st.button("〉", key="slider_r"):
            if st.session_state.slide_idx < len(recent_vids) - 4:
                st.session_state.slide_idx += 1

    with col_content:
        # Display the current "Window" of 4 videos
        idx = st.session_state.slide_idx
        vids = recent_vids.iloc[idx : idx + 4]
        v_cols = st.columns(4)
        for i, (_, video) in enumerate(vids.iterrows()):
            with v_cols[i]:
                yt_link = f"https://www.youtube.com/watch?v={video['video_id']}"
                thumb = f"https://i.ytimg.com/vi/{video['video_id']}/mqdefault.jpg"
                st.markdown(f"""
                <a href="{yt_link}" target="_blank" style="text-decoration:none;">
                    <div class="video-card">
                        <img src="{thumb}" style="width:100%;">
                        <div style="padding:15px;">
                            <div style="color:white; font-size:14px; font-weight:600; height:40px; overflow:hidden;">{video['title']}</div>
                            <div class="video-stats">
                                <span>▶ {format_compact(video['views'])} · 👍 {format_compact(video['likes'])}</span>
                                <span style="font-size:10px;">{video['published_date'].strftime('%b %d')}</span>
                            </div>
                        </div>
                    </div>
                </a>
                """, unsafe_allow_html=True)

    st.markdown("---")
    # --- 3. BOTTOM TABLES --
    st.subheader("High Engagement Content")
    tv = analytics.top_videos_by_views(df, n=10)
    st.subheader("Top 10 Videos by Views")
    tv = analytics.top_videos_by_views(df)
    tv["title"] = tv["title"].apply(analytics.truncate_title)

    st.dataframe(tv,
        column_config={
            "title": st.column_config.TextColumn("Video Title", width="large"),
            "views": st.column_config.NumberColumn("Views", format="%d"),
            "engagement_rate": st.column_config.NumberColumn("Engagement Rate", format="%.4f"),
        },
        hide_index=True, # This removes the row numbers
        width="stretch"
    )

    

    st.markdown("---")

    st.subheader("Top 10 Videos by Likes")
    tl = analytics.top_videos_by_likes(df)
    tl["title"] = tl["title"].apply(analytics.truncate_title)
    st.dataframe(tl, use_container_width=True, hide_index=True)

    st.markdown("---")

    st.subheader("Top 10 Videos by Engagement Rate")
    te = analytics.top_videos_by_engagement(df)
    te["title"] = te["title"].apply(analytics.truncate_title)
    st.dataframe(te, use_container_width=True, hide_index=True)

    st.markdown("---")
