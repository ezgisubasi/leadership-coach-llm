from pytubefix import Playlist, YouTube
import os
import json

AUDIO_DIR = "data/audio"
OUTPUT_JSON = "data/transcripts.json"
PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLCi3Q_-uGtdlCsFXHLDDHBSLyq4BkQ6gZ"

os.makedirs(AUDIO_DIR, exist_ok=True)

def get_video_id(video_url):
    yt = YouTube(video_url)
    return yt.video_id

def download_audio(video_url):
    yt = YouTube(video_url)
    stream = yt.streams.filter(only_audio=True).first()
    video_id = get_video_id(video_url)
    file_path = os.path.join(AUDIO_DIR, f"{video_id}.mp4")

    if not os.path.exists(file_path):
        stream.download(output_path=AUDIO_DIR, filename=f"{video_id}.mp4")
        print(f"✅ Downloaded: {yt.title}")
    else:
        print(f"⏭️ Already exists: {yt.title}")

    return {
        "file_name": os.path.basename(file_path),
        "video_title": yt.title,
        "video_url": video_url,
        "video_text": ""
    }

def download_playlist(playlist_url):
    playlist = Playlist(playlist_url)
    metadata = []

    for url in playlist.video_urls:
        try:
            video_info = download_audio(url)
            metadata.append(video_info)
        except Exception as e:
            print(f"❌ Error downloading {url}: {e}")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 Done. Saved metadata to {OUTPUT_JSON}")

if __name__ == "__main__":
    download_playlist(PLAYLIST_URL)

