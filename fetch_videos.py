import json
import os
import requests

# Config
# 嘗試從環境變數取得金鑰，如果沒有則為 None
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
OUTPUT_FILE = "videos.json"

# Default/Fallback Data (Used if API fails or Key is invalid)
# 這裡的資料會在 API 失敗時顯示在網站上，確保版面不會空白
FALLBACK_DATA = [
    {
        "id": "1",
        "title": "Welcome to Nash Wu 17",
        "desc": "This is a placeholder video. The API request failed (403/Quota Exceeded). Please check your GitHub Secrets.",
        "thumbnail": "https://picsum.photos/seed/nash/800/450",
        "url": "https://www.youtube.com/@Nash_Wu_17"
    },
    {
        "id": "2",
        "title": "Tokyo Trip: SHIBUYA SKY",
        "desc": "The new landmark of Tokyo, 360 degree view!",
        "thumbnail": "https://picsum.photos/seed/tokyo/800/450",
        "url": "https://www.youtube.com/@Nash_Wu_17"
    },
    {
        "id": "3",
        "title": "iPhone 15 Pro Max Review",
        "desc": "Is Titanium really lighter? 1 Month usage review.",
        "thumbnail": "https://picsum.photos/seed/iphone/800/450",
        "url": "https://www.youtube.com/@Nash_Wu_17"
    }
]

def fetch_videos():
    print(f"Starting fetch for Channel ID: {CHANNEL_ID}")

    # 1. 檢查金鑰是否存在
    if not YOUTUBE_API_KEY or not CHANNEL_ID:
        print("Error: YOUTUBE_API_KEY or CHANNEL_ID is missing from environment variables.")
        print("Using fallback data.")
        save_videos(FALLBACK_DATA)
        return

    api_url = f"https://www.googleapis.com/youtube/v3/search?key={YOUTUBE_API_KEY}&channelId={CHANNEL_ID}&part=snippet,id&order=date&maxResults=6&type=video"

    try:
        # 2. 發送請求
        response = requests.get(api_url)
        
        # 3. 檢查回應狀態碼 (Handle 403, 404, 500 errors gracefully)
        if response.status_code != 200:
            print(f"API Request Failed. Status Code: {response.status_code}")
            print(f"Error Message: {response.text}")
            print("Falling back to default data to prevent Action failure.")
            save_videos(FALLBACK_DATA)
            return

        # 4. 解析資料
        data = response.json()
        videos = []

        if "items" in data:
            for item in data["items"]:
                # 確保有 videoId
                video_id = item["id"].get("videoId")
                if not video_id:
                    continue
                    
                snippet = item["snippet"]
                videos.append({
                    "id": video_id,
                    "title": snippet["title"],
                    "desc": snippet["description"],
                    "thumbnail": snippet["thumbnails"]["high"]["url"],
                    "url": f"https://www.youtube.com/watch?v={video_id}"
                })
            
            if len(videos) > 0:
                print(f"Successfully fetched {len(videos)} videos.")
                save_videos(videos)
            else:
                print("No videos found in the response.")
                save_videos(FALLBACK_DATA)
        else:
            print("Invalid API response format (missing 'items').")
            save_videos(FALLBACK_DATA)

    except Exception as e:
        # 5. 捕捉其他未預期的錯誤 (例如網路斷線)
        print(f"Critical Exception occurred: {str(e)}")
        print("Using fallback data.")
        save_videos(FALLBACK_DATA)

def save_videos(data):
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved data to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Failed to save file: {e}")

if __name__ == "__main__":
    fetch_videos()