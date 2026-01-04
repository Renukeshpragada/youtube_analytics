import streamlit as st
import analytics.analytics as analytics

def render(df):
    st.subheader("Engagement Analysis")
    avg_eng = round(df["engagement_rate"].mean(), 4)

    st.metric(
        label="Average Engagement Rate",
        value=avg_eng
    )

    st.caption(
        "Engagement Rate = (Likes + Comments) / Views"
    )
    st.subheader("Likes vs Comments Correlation")

    st.scatter_chart(
        df,
        x="likes",
        y="comments"
    )
    st.subheader("Views vs Engagement Rate")

    st.scatter_chart(
        df,
        x="views",
        y="engagement_rate"
    )

    st.caption(
        "High views + high engagement indicates viral content. "
        "Low engagement despite high views suggests passive audience."
    )