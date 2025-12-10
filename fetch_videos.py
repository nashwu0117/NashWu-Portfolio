import os
import json
import requests

# 從 GitHub Secrets 獲取環境變數
API_KEY = os.environ.get("YOUTUBE_API_KEY")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

def fetch_videos():
    # 檢查是否設定了必要的環境變數
    if not API_KEY or not CHANNEL_ID:
        print("Error: YOUTUBE_API_KEY or CHANNEL_ID not found in environment variables.")
        print("Please configure these secrets in your GitHub Repository settings.")
        return

    base_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": API_KEY,
        "channelId": CHANNEL_ID,
        "part": "snippet,id",
        "order": "date",
        "maxResults": 20,  # 抓取最新的 20 部影片
        "type": "video"
    }

    try:
        print(f"Fetching videos for Channel ID: {CHANNEL_ID}...")
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        videos = []

        for item in data.get("items", []):
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            
            # 取得最佳解析度的縮圖
            thumbnails = snippet.get("thumbnails", {})
            thumbnail_url = (
                thumbnails.get("high", {}).get("url") or 
                thumbnails.get("medium", {}).get("url") or 
                thumbnails.get("default", {}).get("url")
            )

            videos.append({
                "id": video_id,
                "title": snippet["title"],
                "desc": snippet["description"],
                "thumbnail": thumbnail_url,
                "url": f"https://www.youtube.com/watch?v={video_id}"
            })

        # 只有在成功抓取到影片時才更新檔案
        if videos:
            with open("videos.json", "w", encoding="utf-8") as f:
                json.dump(videos, f, indent=2, ensure_ascii=False)
            print(f"Successfully updated videos.json with {len(videos)} videos.")
        else:
            print("No videos found. videos.json was not updated.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fetch_videos()