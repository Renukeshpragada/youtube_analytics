from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import mysql.connector
import pandas as pd
import isodate
from datetime import datetime
import time

# ==============================
# CONFIGURATION
# ==============================

API_KEY = "AIzaSyBWERKpHNY6G-y7Qrdcu-C7dccdeXPmELw"

CSV_PATH = "selected_channels.csv"  
# CSV must have columns: channel_id, channel_type (small/medium/large)

VIDEO_LIMITS = {
    "small": 450,
    "medium": 1000,
    "large": 1500
}

DB_CONFIG = {
    "host": "localhost",
    "user": "yt_user",
    "password": "StrongPass@123",
    "database": "youtube_analytics"
}

# ==============================
# YOUTUBE CLIENT
# ==============================

youtube = build("youtube", "v3", developerKey=API_KEY)

# ==============================
# DATABASE CONNECTION
# ==============================

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# ==============================
# YOUTUBE API FUNCTIONS
# ==============================

def fetch_channel_details(channel_id):
    res = youtube.channels().list(
        part="snippet,statistics",
        id=channel_id
    ).execute()

    if not res["items"]:
        return None

    item = res["items"][0]

    return (
        channel_id,
        item["snippet"]["title"],
        int(item["statistics"].get("subscriberCount", 0)),
        int(item["statistics"].get("viewCount", 0)),
        int(item["statistics"].get("videoCount", 0)),
        item["snippet"]["publishedAt"],
        datetime.now()
    )


def get_uploads_playlist(channel_id):
    res = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    ).execute()

    return res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


def get_video_ids(playlist_id, max_videos):
    video_ids = []
    next_page = None

    while True:
        res = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,  # API LIMIT
            pageToken=next_page
        ).execute()

        for item in res["items"]:
            video_ids.append(item["contentDetails"]["videoId"])
            if len(video_ids) >= max_videos:
                return video_ids

        next_page = res.get("nextPageToken")
        if not next_page:
            break

    return video_ids


def fetch_video_details(video_ids, channel_id):
    videos = []

    for i in range(0, len(video_ids), 50):
        res = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(video_ids[i:i+50])
        ).execute()

        for v in res["items"]:
            duration = isodate.parse_duration(
                v["contentDetails"]["duration"]
            ).total_seconds()

            videos.append((
                v["id"],
                channel_id,
                v["snippet"]["title"],
                v["snippet"]["publishedAt"],
                int(v["statistics"].get("viewCount", 0)),
                int(v["statistics"].get("likeCount", 0)),
                int(v["statistics"].get("commentCount", 0)),
                int(duration)
            ))

    return videos

# ==============================
# DATABASE INSERT FUNCTIONS
# ==============================

def insert_channel(cursor, data):
    cursor.execute("""
        INSERT IGNORE INTO channels_detailed
        (channel_id, channel_name, subscribers, total_views,
         total_videos, channel_created_date, last_updated)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, data)


def insert_videos(cursor, videos):
    cursor.executemany("""
        INSERT IGNORE INTO videos_detailed
        (video_id, channel_id, title, published_date,
         views, likes, comments, duration_seconds)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, videos)

# ==============================
# MAIN EXTRACTION LOGIC
# ==============================

channels_df = pd.read_csv("../data/selected_channels.csv")

for _, row in channels_df.iterrows():

    channel_id = row["channel_id"]
    channel_type = row["channel_type"].lower()

    max_videos = VIDEO_LIMITS.get(channel_type, 450)

    print(f"\n▶ Processing {channel_id} | type={channel_type} | limit={max_videos}")

    try:
        # Channel details
        channel_data = fetch_channel_details(channel_id)
        if not channel_data:
            print("  ⚠ Channel not found, skipping")
            continue

        insert_channel(cursor, channel_data)

        # Playlist
        playlist_id = get_uploads_playlist(channel_id)

        # Video IDs
        video_ids = get_video_ids(playlist_id, max_videos)

        # Video details
        videos = fetch_video_details(video_ids, channel_id)
        insert_videos(cursor, videos)

        conn.commit()
        print(f"  ✅ Inserted {len(videos)} videos")

        time.sleep(1)  # small delay to reduce quota burst

    except HttpError as e:
        if e.resp.status == 403:
            print("  ❌ QUOTA EXCEEDED — STOPPING")
            conn.commit()
            break
        else:
            print("  ❌ API ERROR:", e)

    except Exception as e:
        print("  ❌ ERROR:", e)

# ==============================
# CLEANUP
# ==============================

cursor.close()
conn.close()

print("\n🎯 EXTRACTION COMPLETED")
