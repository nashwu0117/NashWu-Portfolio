# =============================================================================
# fetch_videos.py — Nash Wu Portfolio · YouTube Sync Script
# =============================================================================
# Copyright (c) 2025 Nash Wu (nashwu0990117@gmail.com)
# Repository: https://github.com/nashwu0117/NashWu-Portfolio
#
# LICENCE NOTICE
# All rights reserved. This source code and its design are the exclusive
# intellectual property of Nash Wu. You may NOT copy, reproduce, redistribute,
# sublicense, modify, or use any part of this code — in whole or in part —
# without prior written permission from the author.
#
# Unauthorised use will be pursued to the fullest extent permitted by law.
# =============================================================================

import json
import os
import requests

# ── Config ──────────────────────────────────────────────────────────────────
YOUTUBE_API_KEY  = os.environ.get("YOUTUBE_API_KEY")
CHANNEL_ID       = os.environ.get("CHANNEL_ID")
OUTPUT_FILE      = "videos.json"

HEADERS = {
    "Referer":    "https://nashwu0117.github.io/NashWu-Portfolio/",
    "User-Agent": (
        "Mozilla/5.0 (compatible; NashWuPortfolio/1.0; "
        "+https://nashwu0117.github.io/NashWu-Portfolio/)"
    ),
}

FALLBACK_DATA = [
    {
        "id":        "placeholder",
        "title":     "Nash Wu — Coming Soon",
        "desc":      "影片即將上線，敬請期待！",
        "thumbnail": "https://picsum.photos/seed/nashwu/800/450",
        "url":       "https://www.youtube.com/@Nash_Wu_17",
    }
]

# Private/deleted video sentinel titles returned by the playlist API
PRIVATE_TITLES = {"Private video", "Deleted video"}

# ── Helpers ──────────────────────────────────────────────────────────────────

def save_videos(data):
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(data)} videos to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Failed to save file: {e}")


def check_privacy_status(video_id, api_key):
    """
    Returns 'public', 'private', 'unlisted', or 'unknown'.
    Uses the videos.list endpoint with part=status.
    If the video doesn't appear in results it was deleted or is private.
    """
    url = (
        f"https://www.googleapis.com/youtube/v3/videos"
        f"?key={api_key}&id={video_id}&part=status"
    )
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            print(f"  [warn] videos.list {r.status_code} for {video_id}")
            return "unknown"
        items = r.json().get("items", [])
        if not items:
            return "private"   # not returned → deleted or private
        return items[0].get("status", {}).get("privacyStatus", "unknown")
    except Exception as e:
        print(f"  [warn] privacy check error for {video_id}: {e}")
        return "unknown"


def fetch_playlist_page(playlist_id, api_key, page_token):
    url = (
        f"https://www.googleapis.com/youtube/v3/playlistItems"
        f"?key={api_key}"
        f"&playlistId={playlist_id}"
        f"&part=snippet"
        f"&maxResults=50"
    )
    if page_token:
        url += f"&pageToken={page_token}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code != 200:
        raise RuntimeError(f"API {r.status_code}: {r.text[:300]}")
    return r.json()


# ── Main ─────────────────────────────────────────────────────────────────────

def fetch_videos():
    print(f"Starting fetch for Channel ID: {CHANNEL_ID}")

    if not YOUTUBE_API_KEY or not CHANNEL_ID:
        print("Error: Missing YOUTUBE_API_KEY or CHANNEL_ID.")
        save_videos(FALLBACK_DATA)
        return

    # 1. Load existing cache
    existing_videos = []
    existing_ids = set()
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                existing_videos = json.load(f)
                existing_ids = {v["id"] for v in existing_videos}
            print(f"Loaded {len(existing_videos)} cached videos.")
        except Exception as e:
            print(f"Could not read cache: {e}")

    # 2. Pull upload playlist (UC → UU)
    uploads_playlist_id = "UU" + CHANNEL_ID[2:]
    print(f"Using uploads playlist: {uploads_playlist_id}")

    new_videos = []
    ids_to_remove = set()
    next_page_token = None

    while True:
        try:
            data = fetch_playlist_page(uploads_playlist_id, YOUTUBE_API_KEY, next_page_token)
        except RuntimeError as e:
            print(f"Fetch error: {e}")
            break

        for item in data.get("items", []):
            snippet  = item.get("snippet", {})
            video_id = snippet.get("resourceId", {}).get("videoId", "")
            title    = snippet.get("title", "")

            if not video_id:
                continue

            # Fast check: playlist API returns sentinel titles for private videos
            if title in PRIVATE_TITLES:
                print(f"  [skip] Private/deleted sentinel: {video_id}")
                ids_to_remove.add(video_id)
                continue

            # Confirmed check via videos.list status
            privacy = check_privacy_status(video_id, YOUTUBE_API_KEY)
            if privacy in ("private", "unlisted"):
                print(f"  [skip] {privacy} confirmed: {video_id} — {title[:40]}")
                ids_to_remove.add(video_id)
                continue

            # Already cached and still public → no action needed
            if video_id in existing_ids:
                continue

            thumbnail = (
                snippet["thumbnails"].get("maxres")
                or snippet["thumbnails"].get("high")
                or snippet["thumbnails"].get("medium")
                or {}
            ).get("url", "")

            new_videos.append({
                "id":        video_id,
                "title":     title,
                "desc":      snippet.get("description", ""),
                "thumbnail": thumbnail,
                "url":       f"https://www.youtube.com/watch?v={video_id}",
            })

        next_page_token = data.get("nextPageToken")
        print(f"  {len(new_videos)} new public video(s) found so far...")
        if not next_page_token:
            break

    # 3. Purge videos that became private/deleted from the cache
    if ids_to_remove:
        before_count = len(existing_videos)
        existing_videos = [v for v in existing_videos if v["id"] not in ids_to_remove]
        purged = before_count - len(existing_videos)
        print(f"Purged {purged} now-private/deleted video(s) from cache.")

    # 4. Merge (newest first) and save
    if new_videos or ids_to_remove:
        merged = new_videos + existing_videos
        save_videos(merged)
    elif existing_videos:
        print("No changes. Cache is up to date.")
    else:
        print("No public videos found. Saving fallback.")
        save_videos(FALLBACK_DATA)


if __name__ == "__main__":
    fetch_videos()
