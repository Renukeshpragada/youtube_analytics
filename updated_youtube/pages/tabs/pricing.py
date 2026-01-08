import streamlit as st
import pandas as pd
import altair as alt

def render(df):
    st.markdown("## 💰 Revenue Insights")

    # ------------------------------
    # HARD VALIDATION (NO GUESSING)
    # ------------------------------
    required_cols = {"views", "published_date"}
    if not required_cols.issubset(df.columns):
        st.error(f"Missing columns: {required_cols - set(df.columns)}")
        return

    df = df.copy()
    df["published_date"] = pd.to_datetime(df["published_date"], errors="coerce")
    df = df.dropna(subset=["published_date"])

    # ------------------------------
    # CONFIG
    # ------------------------------
    RPM = 4.00  # USD per 1000 views

    # ------------------------------
    # METRIC CALCULATIONS
    # ------------------------------
    total_views = df["views"].sum()
    estimated_total_earnings = (total_views / 1000) * RPM
    avg_earnings_per_video = (df["views"].mean() / 1000) * RPM

    # ------------------------------
    # TOP METRIC CARDS (CSS SAFE)
    # ------------------------------
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="overview-card">
            <div class="overview-card-label">Total Estimated Earnings</div>
            <div class="overview-card-value">${estimated_total_earnings:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="overview-card">
            <div class="overview-card-label">Avg. Earnings Per Video</div>
            <div class="overview-card-value">${avg_earnings_per_video:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="overview-card">
            <div class="overview-card-label">Applied RPM Rate</div>
            <div class="overview-card-value">${RPM:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ------------------------------
    # MONTHLY EARNINGS (CORRECT)
    # ------------------------------
    df["month"] = df["published_date"].dt.to_period("M").dt.to_timestamp()

    monthly_df = (
        df.groupby("month", as_index=False)["views"]
        .sum()
    )

    monthly_df["earnings"] = (monthly_df["views"] / 1000) * RPM

    since_date = df["published_date"].min().strftime("%d %b %Y")

    st.markdown(f"**Estimated earnings since {since_date}**")
    st.markdown("### Estimated Earnings")

    # ------------------------------
    # CHART (COLORFUL & ATTRACTIVE)
    # ------------------------------
    # Line chart
    earnings_line = alt.Chart(monthly_df).mark_line(
        point=True,
        strokeWidth=4,
        color='#FF0000',
        interpolate='monotone'
    ).encode(
        x=alt.X(
            "month:T",
            title="Month",
            axis=alt.Axis(
                format="%b '%y",
                labelColor="#9bbcd6",
                grid=False,
                labelAngle=-45
            ),
        ),
        y=alt.Y(
            "earnings:Q",
            title="Estimated Earnings ($)",
            axis=alt.Axis(
                format="$~s",
                labelColor="#9bbcd6",
                grid=True,
                gridColor="#1c3d5a",
                gridDash=[3, 3],
            ),
        ),
        tooltip=[
            alt.Tooltip("month:T", title="Month", format="%B %Y"),
            alt.Tooltip("earnings:Q", title="Earnings", format="$,.2f"),
        ],
    )
    
    # Area fill
    earnings_area = alt.Chart(monthly_df).mark_area(
        color=alt.Gradient(
            gradient="linear",
            stops=[
                alt.GradientStop(color="rgba(255, 0, 0, 0.6)", offset=0),
                alt.GradientStop(color="rgba(255, 0, 0, 0.1)", offset=1),
            ],
            x1=0, x2=0, y1=0, y2=1,
        ),
        interpolate='monotone'
    ).encode(
        x=alt.X("month:T"),
        y=alt.Y("earnings:Q")
    )
    
    earnings_chart = (earnings_area + earnings_line).resolve_scale().properties(height=450).configure_view(strokeOpacity=0).configure_axis(titleColor='#9bbcd6')

    st.altair_chart(earnings_chart, use_container_width=True)
    
    st.markdown("---")
    
    # ------------------------------
    # EARNINGS BY YEAR PIE CHART
    # ------------------------------
    st.markdown("### 💰 Earnings Distribution by Year")

# ------------------------------
# DATA (UNCHANGED)
# ------------------------------
    yearly_earnings = monthly_df.copy()
    yearly_earnings['year'] = pd.to_datetime(yearly_earnings['month']).dt.year
    yearly_earnings_sum = yearly_earnings.groupby('year')['earnings'].sum().reset_index()

    total_earnings = yearly_earnings_sum['earnings'].sum()

# ------------------------------
# PIE CHART (CENTERED)
# ------------------------------
    pie_chart = alt.Chart(yearly_earnings_sum).mark_arc(
        innerRadius=60,
        outerRadius=140   # slightly smaller for balance
    ).encode(
        theta=alt.Theta('earnings:Q', stack=True),
        color=alt.Color(
            'year:O',
            scale=alt.Scale(scheme='reds'),
            legend=alt.Legend(
                title='Year',
                labelColor='#9bbcd6',
                titleColor='#9bbcd6'
            )
        ),
        tooltip=[
            alt.Tooltip('year:O', title='Year'),
            alt.Tooltip('earnings:Q', title='Earnings', format='$,.2f')
        ]
    ).properties(
        height=380,
        width=380
    )

    st.altair_chart(pie_chart, use_container_width=True)

    st.markdown("---")

# ------------------------------
# DISTRIBUTION GRID (3 PER ROW)
# ------------------------------
    st.markdown("### 📊 Yearly Earnings Breakdown")

    rows = [
        yearly_earnings_sum.iloc[i:i+3]
        for i in range(0, len(yearly_earnings_sum), 3)
    ]

    for row_df in rows:
        cols = st.columns(3)
        for col, (_, r) in zip(cols, row_df.iterrows()):
            pct = (r['earnings'] / total_earnings) * 100
            with col:
                st.markdown(
                    f"""
                    <div class="year-stat-card">
                        <div class="year-stat-year">{int(r['year'])}</div>
                        <div class="year-stat-views">${r['earnings']:,.2f}</div>
                        <div class="year-stat-pct">{pct:.1f}%</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# ------------------------------
# FOOTNOTE
# ------------------------------
    st.caption(
        "Estimated revenue calculated using: Earnings = (Total Views / 1,000) × RPM."
    )
