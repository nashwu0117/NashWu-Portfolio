def fetch_videos():
    print(f"Starting fetch for Channel ID: {CHANNEL_ID}")

    if not YOUTUBE_API_KEY or not CHANNEL_ID:
        print("Error: Missing API key or Channel ID.")
        save_videos(FALLBACK_DATA)
        return

    # 1. 讀取現有的 videos.json（已記錄的影片）
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

    # 2. 只抓最新 10 支去比對（省 quota）
    url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?key={YOUTUBE_API_KEY}"
        f"&channelId={CHANNEL_ID}"
        f"&part=snippet,id"
        f"&order=date"
        f"&maxResults=10"
        f"&type=video"
    )

    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"API Failed: {response.status_code} - {response.text}")
            print("Keeping existing data unchanged.")
            return  # 不動 videos.json，保留舊的

        data = response.json()
        new_videos = []

        for item in data.get("items", []):
            video_id = item["id"].get("videoId")
            if not video_id or video_id in existing_ids:
                continue  # 已經有了，跳過
            snippet = item["snippet"]
            new_videos.append({
                "id": video_id,
                "title": snippet["title"],
                "desc": snippet["description"],
                "thumbnail": snippet["thumbnails"]["high"]["url"],
                "url": f"https://www.youtube.com/watch?v={video_id}"
            })

        if new_videos:
            print(f"Found {len(new_videos)} new video(s)! Adding to list.")
            # 新影片放最前面
            merged = new_videos + existing_videos
            save_videos(merged)
        else:
            print("No new videos found. Cache is up to date.")
            # 不需要儲存，檔案沒變化

    except Exception as e:
        print(f"Exception: {e}")
        print("Keeping existing data unchanged.")
