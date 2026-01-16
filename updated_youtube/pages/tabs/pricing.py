import streamlit as st
import pandas as pd
import altair as alt

def render(df):
    # ==============================
    # 1. LUXURY UI CSS & ANIMATIONS
    # ==============================
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');

        /* Main Container Entry Animation */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .pricing-main {
            animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            font-family: 'Inter', sans-serif;
        }

        /* Hero Revenue Cards */
        .revenue-hero-card {
            background: #0d161f;
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 18px;
            padding: 30px;
            text-align: center;
            transition: 0.4s ease;
        }
        .revenue-hero-card:hover {
            border-color: #00e5ff;
            transform: translateY(-5px);
            background: rgba(13, 22, 31, 0.9);
        }
        .rev-label {
            color: #94a3b8; font-size: 0.8rem; font-weight: 700; 
            text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 12px;
        }
        .rev-value {
            color: #00e5ff; font-size: 2.2rem; font-weight: 800;
        }

        /* UPDATED GRADIENT DISTRIBUTION CARDS */
        .grad-dist-card {
            border-radius: 20px;
            padding: 25px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.4s ease;
            margin-bottom: 20px;
            min-height: 150px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 12px 24px rgba(0,0,0,0.4);
        }
        .grad-dist-card:hover { 
            transform: scale(1.04);
            border-color: rgba(255,255,255,0.4);
        }
        
        .year-label { font-size: 0.75rem; font-weight: 700; color: rgba(255,255,255,0.8); text-transform: uppercase; margin-bottom: 8px; }
        .amt-val { color: white; font-size: 1.7rem; font-weight: 800; letter-spacing: -0.5px; }
        .pct-badge { 
            background: rgba(255,255,255,0.18); border-radius: 20px; 
            padding: 4px 12px; font-size: 0.75rem; font-weight: 700; 
            width: fit-content; margin: 12px auto 0 auto; 
            color: white;
        }

        hr { border: none; height: 1px; background: rgba(255,255,255,0.05); margin: 50px 0; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="pricing-main">', unsafe_allow_html=True)

    # ==============================
    # 2. DATA CALCULATION
    # ==============================
    df = df.copy()
    df["published_date"] = pd.to_datetime(df["published_date"], errors="coerce").dropna()
    RPM = 4.00 
    
    total_views = df["views"].sum()
    est_total = (total_views / 1000) * RPM
    avg_per_vid = (df["views"].mean() / 1000) * RPM

    # ==============================
    # 3. HEADER & HERO CARDS
    # ==============================
    st.markdown("""
    <div style="margin-bottom:30px;">
        <h2 style="font-weight:800; color:white; font-size:2.2rem;margin-left:499px;">💰 Revenue Insights</h2>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: 
        st.markdown(f'<div class="revenue-hero-card"><div class="rev-label">Total Estimated Earnings</div><div class="rev-value">${est_total:,.2f}</div></div>', unsafe_allow_html=True)
    with c2: 
        st.markdown(f'<div class="revenue-hero-card"><div class="rev-label">Avg Earnings Per Video</div><div class="rev-value" style="color:white;">${avg_per_vid:,.2f}</div></div>', unsafe_allow_html=True)
    with c3: 
        st.markdown(f'<div class="revenue-hero-card"><div class="rev-label">Applied RPM Rate</div><div class="rev-value">${RPM:,.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ==============================
    # 4. EARNINGS TREND CHART (UNCHANGED RED STYLE)
    # ==============================
    df["month"] = df["published_date"].dt.to_period("M").dt.to_timestamp()
    monthly_df = df.groupby("month", as_index=False)["views"].sum()
    monthly_df["earnings"] = (monthly_df["views"] / 1000) * RPM

    st.markdown("<h3 style='text-align:center;'>Estimated Earnings Overview</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    line = alt.Chart(monthly_df).mark_line(point=True, strokeWidth=4, color='#FF0000', interpolate='monotone').encode(
        x=alt.X("month:T", title=None, axis=alt.Axis(format="%b '%y", labelColor="#94a3b8", grid=False)),
        y=alt.Y("earnings:Q", title="Earnings ($)", axis=alt.Axis(format="$~s", labelColor="#94a3b8", gridColor="#1a2733")),
        tooltip=[alt.Tooltip("month:T", format="%B %Y"), alt.Tooltip("earnings:Q", format="$,.2f")]
    )
    
    area = alt.Chart(monthly_df).mark_area(
        color=alt.Gradient(gradient="linear", stops=[alt.GradientStop(color="rgba(255, 0, 0, 0.5)", offset=0.5), alt.GradientStop(color="transparent", offset=1)], x1=0, x2=0, y1=0, y2=1),
        interpolate='monotone'
    ).encode(x="month:T", y="earnings:Q")

    st.altair_chart((area + line).properties(height=450), use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ==============================
    # 5. CENTERED PIE CHART
    # ==============================
    st.markdown("<h3 style='text-align:center;'>🥧 Yearly Earnings Distribution</h3>", unsafe_allow_html=True)
    st.markdown("---")
    yearly_df = monthly_df.copy()
    yearly_df['year'] = yearly_df['month'].dt.year
    year_agg_full = yearly_df.groupby('year')['earnings'].sum().reset_index()
    total_revenue = year_agg_full['earnings'].sum()

    col_l, col_center, col_r = st.columns([1, 2, 1])
    with col_center:
        pie = alt.Chart(year_agg_full).mark_arc(innerRadius=80, outerRadius=160).encode(
            theta='earnings:Q',
            color=alt.Color('year:O', scale=alt.Scale(scheme='reds'), legend=alt.Legend(title="Year")),
            tooltip=['year', alt.Tooltip('earnings:Q', format='$,.2f')]
        ).properties(height=450)
        st.altair_chart(pie, use_container_width=True)

    # ==========================================
    # 6. FILTER RECENT 6 YEARS & GRADIENT GRID
    # ==========================================
    st.markdown("<br><h3 style='text-align:center; color:#94a3b8;'>📊 Recent 6-Year Performance Matrix</h3>", unsafe_allow_html=True)
    
    # Filter only recent 6 years
    year_agg_6 = year_agg_full.sort_values('year', ascending=False).head(6).sort_values('year')

    # Cleaner, high-contrast gradient palette
    gradients = [
        "linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)", # Steel
        "linear-gradient(135deg, #141e30 0%, #243b55 100%)",            # Space
        "linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%)",            # Ocean
        "linear-gradient(135deg, #373b44 0%, #4286f4 100%)",            # Power Blue
        "linear-gradient(135deg, #200122 0%, #6f0000 100%)",            # Deep Crimson
        "linear-gradient(135deg, #000000 0%, #434343 100%)"             # Midnight
    ]

    for i in range(0, len(year_agg_6), 3):
        chunk = year_agg_6.iloc[i : i + 3]
        row_cols = st.columns(3)
        for idx, (_, row) in enumerate(chunk.iterrows()):
            pct = (row['earnings'] / total_revenue) * 100
            grad_style = gradients[(i + idx) % len(gradients)]
            
            with row_cols[idx]:
                st.markdown(f"""
                <div class="grad-dist-card" style="background: {grad_style};">
                    <div class="year-label">Year {int(row['year'])}</div>
                    <div class="amt-val">${row['earnings']:,.2f}</div>
                    <div class="pct-badge">{pct:.1f}% Impact</div>
                </div>
                """, unsafe_allow_html=True) 

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)