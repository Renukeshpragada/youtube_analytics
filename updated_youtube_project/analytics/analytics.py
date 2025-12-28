import pandas as pd
def load_video_data_by_channel(conn, channel_id):
    query = """
        SELECT *
        FROM videos_detailed
        WHERE channel_id = %s
    """
    df = pd.read_sql(query, conn, params=(channel_id,))

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
