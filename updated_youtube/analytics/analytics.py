import pandas as pd
import mysql.connector
import streamlit as st
def load_video_data_by_channel(channel_id):
    conn = mysql.connector.connect(
        host="localhost",
        user=st.secrets["database"]["user"],
        password=st.secrets["database"]["password"],
        database=st.secrets["database"]["name"]
    )

    query = """
        SELECT *
        FROM videos_detailed
        WHERE channel_id = %s
    """

    df = pd.read_sql(query, conn, params=(channel_id,))
    conn.close()

    if df.empty:
        return df

    df["published_date"] = pd.to_datetime(df["published_date"])
    df["year"] = df["published_date"].dt.year
    df["month"] = df["published_date"].dt.month
    df["month_name"] = df["published_date"].dt.strftime("%b")
    df["day_name"] = df["published_date"].dt.day_name()
    df["hour"] = df["published_date"].dt.hour

    df["engagement_rate"] = (
        (df["likes"] + df["comments"]) / df["views"]
    ).replace([float("inf")], 0).fillna(0)

    return df


def load_video_data(conn):
    df = pd.read_sql("SELECT * FROM videos_detailed", conn)

    df["published_date"] = pd.to_datetime(df["published_date"])

    df["year"] = df["published_date"].dt.year
    df["month"] = df["published_date"].dt.month
    df["month_name"] = df["published_date"].dt.strftime("%b")
    df["day_name"] = df["published_date"].dt.day_name()
    df["hour"] = df["published_date"].dt.hour

    df["engagement_rate"] = (
        (df["likes"] + df["comments"]) / df["views"]
    ).replace([float("inf")], 0).fillna(0)

    return df


def monthly_views(df):
    return (
        df.groupby(["year", "month_name"])["views"]
        .sum()
        .reset_index()
    )


def upload_frequency_vs_views(df):
    return (
        df.groupby(["year", "month"])
        .agg(
            uploads=("video_id", "count"),
            avg_views=("views", "mean")
        )
        .reset_index()
    )

def top_videos_by_views(df, n=10):
    return (
        df.sort_values("views", ascending=False)
          .loc[:, ["title", "views", "engagement_rate"]]
          .head(n)
    )


def top_videos_by_likes(df, n=10):
    return (
        df.sort_values("likes", ascending=False)
          .loc[:, ["title", "likes", "engagement_rate"]]
          .head(n)
    )


def top_videos_by_engagement(df, n=10):
    return (
        df.sort_values("engagement_rate", ascending=False)
          .loc[:, ["video_id", "title", "engagement_rate"]]
          .head(n)
    )
def truncate_title(title, length=60):
    return title if len(title) <= length else title[:length] + "..."



def best_upload_day(df):
    return df.groupby("day_name")["views"].mean().sort_values(ascending=False)


def best_upload_hour(df):
    return df.groupby("hour")["views"].mean().sort_values(ascending=False)


def top_videos(df, n=10):
    return df.sort_values("views", ascending=False).head(n)


def monthly_views_styled(df):
    """Groups views by year and month and sorts them chronologically."""
    # 1. Group by Year and Month
    mv = df.groupby(["year", "month"]).agg({"views": "sum"}).reset_index()
    
    # 2. Create a sortable 'period' string (e.g., "2024-01")
    mv["period"] = mv["year"].astype(str) + "-" + mv["month"].astype(str).str.zfill(2)
    
    # 3. Sort chronologically so the graph doesn't jump
    mv = mv.sort_values("period")
    return mv



def load_video_data_for_ai(channel_id):
    """
    SAFE function for AI chatbot.
    Uses its own DB connection to avoid unread result errors.
    """

    conn = mysql.connector.connect(
        host="localhost",
        user=st.secrets["database"]["user"],
        password=st.secrets["database"]["password"],
        database=st.secrets["database"]["name"]
    )

    query = """
        SELECT title, views, published_date, likes, comments
        FROM videos_detailed
        WHERE channel_id = %s
    """

    df = pd.read_sql(query, conn, params=(channel_id,))
    conn.close()

    if df.empty:
        return df

    df["published_date"] = pd.to_datetime(df["published_date"])

    df["engagement_rate"] = (
        (df["likes"] + df["comments"]) / df["views"]
    ).replace([float("inf")], 0).fillna(0)

    return df
