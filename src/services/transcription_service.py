# src/services/transcription_service.py
import whisper
import os
import json

class TranscriptionService:
    def __init__(self, model_size="base", audio_dir="data/audio", json_file="data/transcripts.json", text_dir="data/transcripts"):
        # Load Whisper model (downloads on first use)
        print(f"Loading Whisper {model_size} model...")
        self.model = whisper.load_model(model_size)
        self.audio_dir = audio_dir
        self.json_file = json_file
        self.text_dir = text_dir
        
        # Create transcripts directory
        os.makedirs(self.text_dir, exist_ok=True)
        
        print("Whisper model loaded!")
    
    def transcribe_single_file(self, file_path):
        try:
            print(f"Transcribing: {os.path.basename(file_path)}")
            result = self.model.transcribe(file_path, language="tr")
            return result["text"]
        except Exception as e:
            print(f"Error transcribing {file_path}: {e}")
            return None
    
    def save_individual_transcript(self, video_info, transcript):
        """Save transcript as individual text file"""
        # Create filename: video_id.txt (simple)
        filename = f"{video_info['video_id']}.txt"
        file_path = os.path.join(self.text_dir, filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(transcript)
            print(f"Saved: {filename}")
        except Exception as e:
            print(f"Error saving {filename}: {e}")
    
    def transcribe_all_videos(self):
        # Load videos
        with open(self.json_file, 'r', encoding='utf-8') as f:
            videos = json.load(f)
        
        print(f"Transcribing {len(videos)} videos...")
        print(f"Saving JSON to: {self.json_file}")
        print(f"Saving individual texts to: {self.text_dir}/")
        
        for i, video in enumerate(videos, 1):
            # Skip if already transcribed
            if video.get("video_text", "").strip():
                print(f"[{i}/{len(videos)}] Already done: {video['video_title']}")
                continue
            
            # Get audio file path
            audio_file = os.path.join(self.audio_dir, video["file_name"])
            
            if not os.path.exists(audio_file):
                print(f"[{i}/{len(videos)}] File not found: {video['file_name']}")
                continue
            
            print(f"[{i}/{len(videos)}] Processing: {video['video_title']}")
            
            # Transcribe
            transcript = self.transcribe_single_file(audio_file)
            
            if transcript:
                # Add to JSON
                video["video_text"] = transcript.strip()
                
                # Save individual text file
                self.save_individual_transcript(video, transcript.strip())
                
                print(f"Done: {video['video_title']}")
            else:
                print(f"Failed: {video['video_title']}")
        
        # Save updated JSON
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(videos, f, ensure_ascii=False, indent=2)
        
        print(f"\nTranscription complete!")
        print(f"Updated JSON: {self.json_file}")
        print(f"Individual transcripts: {self.text_dir}/")
        
        # Show summary
        transcribed_count = len([v for v in videos if v.get("video_text", "").strip()])
        print(f"Total transcribed: {transcribed_count}/{len(videos)} videos")


if __name__ == "__main__":
    # No API key needed!
    service = TranscriptionService(model_size="base")
    service.transcribe_all_videos()