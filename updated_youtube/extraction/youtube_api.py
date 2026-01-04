import googleapiclient.discovery
import googleapiclient.errors
import requests
import mysql.connector
from datetime import datetime
import isodate  # To parse YouTube duration strings

# ==========================================
# 1. OAUTH & AUTHENTICATION FUNCTIONS
# ==========================================

def get_youtube_channel_info(access_token):
    """Fetches the logged-in user's YouTube channel details using the OAuth token."""
    headers = {'Authorization': f'Bearer {access_token}'}
    url = "https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&mine=true"
    
    response = requests.get(url, headers=headers).json()
    
    if "items" in response and len(response["items"]) > 0:
        item = response["items"][0]
        return {
            "channel_id": item["id"],
            "channel_name": item["snippet"]["title"],
            "thumbnail": item["snippet"]["thumbnails"]["default"]["url"],
            "subscriber_count": item["statistics"].get("subscriberCount", 0)
        }
    return None

def get_authenticated_channel_details(credentials):
    """Fetches the logged-in user's YouTube channel ID and Name using credentials."""
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
    
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        mine=True
    )
    response = request.execute()
    
    if response.get('items'):
        item = response['items'][0]
        return {
            "channel_id": item['id'],
            "channel_name": item['snippet']['title'],
            "custom_url": item['snippet'].get('customUrl', ''),
            "thumbnail": item['snippet']['thumbnails']['default']['url']
        }
    return None

# ==========================================
# 2. SEARCH & LOOKUP FUNCTIONS
# ==========================================

def get_channel_id_by_name(api_key, channel_name):
    """Searches YouTube for a channel name and returns its ID."""
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    request = youtube.search().list(
        q=channel_name,
        type="channel",
        part="snippet",
        maxResults=1
    )
    response = request.execute()
    if response.get("items"):
        return response["items"][0]["snippet"]["channelId"]
    return None

def fetch_channel_stats_from_api(api_key, channel_id):
    """Fetches high-level stats (Total Views, Sub Count, etc.) for any channel."""
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    request = youtube.channels().list(
        part="snippet,statistics",
        id=channel_id
    )
    response = request.execute()
    if response.get("items"):
        item = response["items"][0]
        return {
            "channel_id": item["id"],
            "channel_name": item["snippet"]["title"],
            "total_views": int(item["statistics"].get("viewCount", 0)),
            "subscribers": int(item["statistics"].get("subscriberCount", 0)),
            "video_count": int(item["statistics"].get("videoCount", 0))
        }
    return None

# ==========================================
# 3. DATABASE SYNC FUNCTION (NEW)
# ==========================================


def sync_channel_to_db(conn, api_key, channel_id):
    """Fetches ALL channel and video data from API using pagination."""
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    cursor = conn.cursor()

    try:
        # 1. Fetch Channel Info
        ch_res = youtube.channels().list(part="snippet,statistics,contentDetails", id=channel_id).execute()
        if not ch_res.get('items'): return False
        
        ch_item = ch_res['items'][0]
        uploads_playlist_id = ch_item['contentDetails']['relatedPlaylists']['uploads']

        # Update Channel Table
        sql_ch = """INSERT INTO channels_detailed 
                    (channel_id, channel_name, subscribers, total_views, total_videos, channel_created_date, last_updated)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE subscribers=%s, total_views=%s, total_videos=%s, last_updated=%s"""
        cursor.execute(sql_ch, (
            channel_id, ch_item['snippet']['title'], int(ch_item['statistics'].get('subscriberCount', 0)),
            int(ch_item['statistics'].get('viewCount', 0)), int(ch_item['statistics'].get('videoCount', 0)),
            ch_item['snippet']['publishedAt'].replace('Z', ''), datetime.now(),
            int(ch_item['statistics'].get('subscriberCount', 0)), int(ch_item['statistics'].get('viewCount', 0)), 
            int(ch_item['statistics'].get('videoCount', 0)), datetime.now()
        ))

        # 2. Fetch ALL Video IDs using Pagination
        video_ids = []
        next_page_token = None
        while True:
            pl_res = youtube.playlistItems().list(
                playlistId=uploads_playlist_id, 
                part="contentDetails", 
                maxResults=1200, 
                pageToken=next_page_token
            ).execute()
            
            video_ids.extend([item['contentDetails']['videoId'] for item in pl_res['items']])
            next_page_token = pl_res.get('nextPageToken')
            if not next_page_token: break

        # 3. Fetch detailed stats in batches of 50
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i+50]
            v_res = youtube.videos().list(id=",".join(batch), part="snippet,statistics,contentDetails").execute()

            for v in v_res['items']:
                duration_sec = int(isodate.parse_duration(v['contentDetails']['duration']).total_seconds())
                sql_vid = """INSERT INTO videos_detailed 
                             (video_id, channel_id, title, published_date, views, likes, comments, duration_seconds)
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                             ON DUPLICATE KEY UPDATE views=%s, likes=%s, comments=%s"""
                cursor.execute(sql_vid, (
                    v['id'], channel_id, v['snippet']['title'], v['snippet']['publishedAt'].replace('Z', ''),
                    int(v['statistics'].get('viewCount', 0)), int(v['statistics'].get('likeCount', 0)),
                    int(v['statistics'].get('commentCount', 0)), duration_sec,
                    int(v['statistics'].get('viewCount', 0)), int(v['statistics'].get('likeCount', 0)),
                    int(v['statistics'].get('commentCount', 0))
                ))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        cursor.close()