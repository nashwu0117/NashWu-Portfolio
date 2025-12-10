import os
import json
import requests

def main():
    # Get configuration from Environment Variables (set in GitHub Secrets)
    api_key = os.environ.get("YOUTUBE_API_KEY")
    channel_id = os.environ.get("CHANNEL_ID")
    
    # Validation
    if not api_key or not channel_id:
        print("Warning: YOUTUBE_API_KEY or CHANNEL_ID not found. Skipping API fetch.")
        # Create dummy file if it doesn't exist to prevent 404 errors on frontend
        if not os.path.exists("videos.json"):
            with open("videos.json", "w", encoding="utf-8") as f:
                json.dump([], f)
        return

    # YouTube API URL
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": api_key,
        "channelId": channel_id,
        "part": "snippet,id",
        "order": "date",
        "maxResults": 9,
        "type": "video"
    }

    try:
        print(f"Fetching videos for channel: {channel_id}...")
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        videos = []
        for item in data.get("items", []):
            # Only process if it's a video (just in case)
            if "videoId" in item["id"]:
                video_id = item["id"]["videoId"]
                snippet = item["snippet"]
                
                videos.append({
                    "id": video_id,
                    "title": snippet["title"],
                    "desc": snippet["description"],
                    "thumbnail": snippet["thumbnails"]["high"]["url"],
                    "url": f"https://www.youtube.com/watch?v={video_id}"
                })

        # Save to videos.json
        with open("videos.json", "w", encoding="utf-8") as f:
            json.dump(videos, f, indent=2, ensure_ascii=False)
        
        print(f"Success! Updated videos.json with {len(videos)} videos.")

    except Exception as e:
        print(f"Error fetching videos: {e}")

if __name__ == "__main__":
    main()