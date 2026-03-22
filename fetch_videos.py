import json
import os
import requests

# Config
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
OUTPUT_FILE = "videos.json"

HEADERS = {
    "Referer": "https://nashwu0117.github.io/NashWu-Portfolio/",
    "User-Agent": "Mozilla/5.0 (compatible; NashWuPortfolio/1.0; +https://nashwu0117.github.io/NashWu-Portfolio/)"
}

FALLBACK_DATA = [
    {
        "id": "1",
        "title": "Welcome to Nash Wu 17",
        "desc": "This is a placeholder. API request failed.",
        "thumbnail": "https://picsum.photos/seed/nash/800/450",
        "url": "https://www.youtube.com/@Nash_Wu_17"
    }
]

def save_videos(data):
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(data)} videos to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Failed to save file: {e}")

def fetch_videos():
    print(f"Starting fetch for Channel ID: {CHANNEL_ID}")

    if not YOUTUBE_API_KEY or not CHANNEL_ID:
        print("Error: Missing YOUTUBE_API_KEY or CHANNEL_ID.")
        save_videos(FALLBACK_DATA)
        return

    # 1. 讀取現有的 videos.json
    existing_videos = []
    existing_ids = set()
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                existing_videos = json.load(f)
                existing_ids = {v["id"] for v in existing_videos}
            print(f"Loaded {len(existing_videos)} existing videos from cache.")
        except Exception as e:
            print(f"Could not read existing file: {e}")

    # 2. 用 uploads playlist 抓全部影片（UC 換成 UU）
    uploads_playlist_id = "UU" + CHANNEL_ID[2:]
    print(f"Using uploads playlist: {uploads_playlist_id}")

    new_videos = []
    next_page_token = None

    while True:
        url = (
            f"https://www.googleapis.com/youtube/v3/playlistItems"
            f"?key={YOUTUBE_API_KEY}"
            f"&playlistId={uploads_playlist_id}"
            f"&part=snippet"
            f"&maxResults=50"
        )
        if next_page_token:
            url += f"&pageToken={next_page_token}"

        try:
            response = requests.get(url, headers=HEADERS)
            if response.status_code != 200:
                print(f"API Failed: {response.status_code} - {response.text}")
                break

            data = response.json()

            for item in data.get("items", []):
                video_id = item["snippet"]["resourceId"]["videoId"]
                if not video_id or video_id in existing_ids:
                    continue
                snippet = item["snippet"]
                thumbnail = (
                    snippet["thumbnails"].get("maxres") or
                    snippet["thumbnails"].get("high") or
                    snippet["thumbnails"].get("medium") or
                    {}
                ).get("url", "")
                new_videos.append({
                    "id": video_id,
                    "title": snippet["title"],
                    "desc": snippet["description"],
                    "thumbnail": thumbnail,
                    "url": f"https://www.youtube.com/watch?v={video_id}"
                })

            next_page_token = data.get("nextPageToken")
            print(f"Fetched {len(new_videos)} new videos so far...")

            if not next_page_token:
                break

        except Exception as e:
            print(f"Exception: {e}")
            break

    # 3. 合併新舊影片
    if new_videos:
        print(f"Found {len(new_videos)} new video(s)!")
        merged = new_videos + existing_videos
        save_videos(merged)
    else:
        if existing_videos:
            print("No new videos found. Cache is up to date.")
        else:
            print("No videos found at all. Using fallback.")
            save_videos(FALLBACK_DATA)

if __name__ == "__main__":
    fetch_videos()