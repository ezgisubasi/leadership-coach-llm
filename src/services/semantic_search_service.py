# src/services/embedding_service.py
import os
import json
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct


class SemanticSearchService:
    def __init__(
        self, 
        model_name: str = "altaidevorg/bge-m3-distill-8l",
        db_path: str = "data/youtube_videos_db",
        transcripts_json: str = "data/transcripts.json",
        collection_name: str = "video-descriptions"
    ):
        self.model_name = model_name
        self.db_path = db_path
        self.transcripts_json = transcripts_json
        self.collection_name = collection_name
        
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.client = QdrantClient(path=db_path)
        
        print("Embedding service initialized!")
    
    def create_embeddings(self, batch_size: int = 12):
        """Create embeddings from transcript data and store in vector database."""
        if not os.path.exists(self.transcripts_json):
            print(f"Transcript file not found: {self.transcripts_json}")
            return
        
        with open(self.transcripts_json, 'r', encoding='utf-8') as f:
            videos = json.load(f)
        
        valid_videos = [v for v in videos if v.get("video_text", "").strip()]
        
        if not valid_videos:
            print("No valid transcripts found!")
            return
        
        print(f"Processing {len(valid_videos)} videos with transcripts...")
        
        video_texts = [video["video_text"] for video in valid_videos]
        
        print("Generating embeddings...")
        embeddings = self.model.encode(video_texts, batch_size=batch_size, show_progress_bar=True)
        
        vector_dim = embeddings.shape[1]
        
        try:
            self.client.delete_collection(self.collection_name)
        except:
            pass
        
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE)
        )
        
        points = []
        for i, (video, embedding) in enumerate(zip(valid_videos, embeddings)):
            payload = {
                "video_id": video.get("video_id", ""),
                "video_title": video.get("video_title", "Unknown Title"),
                "video_url": video.get("video_url", ""),
                "file_name": video.get("file_name", ""),
                "video_text": video.get("video_text", "")
            }
            
            points.append(PointStruct(
                id=i,
                vector=embedding.tolist(),
                payload=payload
            ))
        
        self.client.upsert(collection_name=self.collection_name, points=points)
        
        print(f"Successfully processed {len(valid_videos)} videos!")
        print(f"Vector dimension: {vector_dim}")
    
    def search_videos(self, query: str, limit: int = 3) -> Dict[str, Any]:
        """Perform semantic search for videos based on user query."""
        try:
            query_embedding = self.model.encode(query)
            
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                limit=limit
            )
            
            videos = []
            titles = []
            scores = []
            
            for result in search_results:
                payload = result.payload
                videos.append(payload.get("video_url", ""))
                titles.append(payload.get("video_title", "Unknown Title"))
                scores.append(round(result.score, 3))
            
            return {
                "videos": videos,
                "titles": titles,
                "scores": scores,
                "message": f"Found {len(videos)} relevant videos"
            }
            
        except Exception as e:
            print(f"Search error: {str(e)}")
            return {"videos": [], "titles": [], "scores": [], "message": "Search failed"}


if __name__ == "__main__":
    service = SemanticSearchService()
    service.create_embeddings()