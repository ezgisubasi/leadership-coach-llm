# src/services/youtube_service.py
from pytubefix import Playlist, YouTube
import os
import json

class YouTubeService:
    def __init__(self, audio_dir="data/audio", output_json="data/transcripts.json"):
        self.audio_dir = audio_dir
        self.output_json = output_json
        self.metadata = []
        
        os.makedirs(self.audio_dir, exist_ok=True)
        
        if os.path.exists(self.output_json):
            with open(self.output_json, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)

    def download_single_video(self, video_url):
        try:
            yt = YouTube(video_url)
            video_id = yt.video_id
            file_path = os.path.join(self.audio_dir, f"{video_id}.mp4")

            if not os.path.exists(file_path):
                stream = yt.streams.filter(only_audio=True).first()
                stream.download(output_path=self.audio_dir, filename=f"{video_id}.mp4")
                print(f"✅ Downloaded: {yt.title}")
            else:
                print(f"⏭️ Already exists: {yt.title}")

            video_info = {
                "file_name": f"{video_id}.mp4",
                "video_title": yt.title,
                "video_url": video_url,
                "video_id": video_id,
                "video_text": ""
            }
            
            return video_info
            
        except Exception as e:
            print(f"❌ Error downloading {video_url}: {e}")
            return None

    def download_playlist(self, playlist_url):
        try:
            playlist = Playlist(playlist_url)
            
            for url in playlist.video_urls:
                video_info = self.download_single_video(url)
                if video_info:
                    # Add or update metadata
                    existing = next((i for i, v in enumerate(self.metadata) 
                                   if v.get("video_id") == video_info["video_id"]), None)
                    if existing is not None:
                        self.metadata[existing] = video_info
                    else:
                        self.metadata.append(video_info)

            self.save_metadata()
            print(f"🎉 Done! Downloaded {len(self.metadata)} videos")
            return True
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False

    def save_metadata(self):
        with open(self.output_json, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)


# Simple testing - just run this
if __name__ == "__main__":
    service = YouTubeService()
    
    # Test with the playlist
    playlist_url = "https://www.youtube.com/playlist?list=PLCi3Q_-uGtdlCsFXHLDDHBSLyq4BkQ6gZ"
    service.download_playlist(playlist_url)