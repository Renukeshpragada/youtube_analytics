import googleapiclient.discovery
import googleapiclient.errors

import requests

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
    """Fetches the logged-in user's YouTube channel ID and Name."""
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
    
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        mine=True
    )
    response = request.execute()
    
    if response['items']:
        item = response['items'][0]
        return {
            "channel_id": item['id'],
            "channel_name": item['snippet']['title'],
            "custom_url": item['snippet'].get('customUrl', ''),
            "thumbnail": item['snippet']['thumbnails']['default']['url']
        }
    return None

def fetch_channel_by_name(api_key, channel_name):
    """Fallback search for other channels by name."""
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    request = youtube.search().list(q=channel_name, type="channel", part="snippet", maxResults=1)
    res = request.execute()
    if res['items']:
        return res['items'][0]['snippet']['channelId']
    return None




def get_channel_id_by_name(api_key, channel_name):
    """Searches YouTube for a channel name and returns its ID."""
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    request = youtube.search().list(
        q=channel_name,
        type="channel",
        part="snippet",
        maxResults=1500
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