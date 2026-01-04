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
    # CHART (STABLE + CLEAN)
    # ------------------------------
    earnings_chart = (
        alt.Chart(monthly_df)
        .mark_area(
            interpolate="monotone",
            line={"color": "#1E90FF", "size": 3},
            color=alt.Gradient(
                gradient="linear",
                stops=[
                    alt.GradientStop(color="#1E90FF", offset=1),
                    alt.GradientStop(color="rgba(30,144,255,0.05)", offset=0),
                ],
                x1=0, x2=0, y1=1, y2=0,
            ),
        )
        .encode(
            x=alt.X(
                "month:T",
                title=None,
                axis=alt.Axis(
                    format="%b '%y",
                    labelColor="#9bbcd6",
                    grid=False,
                ),
            ),
            y=alt.Y(
                "earnings:Q",
                title=None,
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
        .properties(height=400)
        .configure_view(strokeOpacity=0)
    )

    st.altair_chart(earnings_chart, use_container_width=True)

    st.caption(
        f"Estimated revenue calculated using Earnings = (Total Views / 1,000) × RPM (${RPM})."
    )
