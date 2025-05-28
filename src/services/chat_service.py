# src/services/chat_service.py
import google.generativeai as genai
from typing import Dict, Any
import re
from .semantic_search_service import SemanticSearchService

class YouTubeRAGAssistant:
    def __init__(self, config=None):
        """
        Initialize YouTube RAG Assistant with configuration
        
        Args:
            config: ContentConfig object or None for default
        """
        self.model = None
        self.search_service = SemanticSearchService()
        self.config = config
        
        # Default system prompt if no config provided
        if self.config is None:
            self.system_prompt = """Sen bir AI asistanısın. Video içeriklerine dayanarak soruları yanıtlayacaksın.
            
Görevin:
- Video içeriklerini kaynak göstererek sorulara yanıt vermek
- Profesyonel ve yardımcı bir ton kullanmak
- Türkçe yanıtlar vermek"""
        else:
            self.system_prompt = self.config.system_prompt
        
    def set_api_key(self, api_key: str):
        """Set the API key and initialize the model"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        print("Gemini API configured successfully!")
        
    def set_config(self, config):
        """Update the assistant configuration"""
        self.config = config
        self.system_prompt = config.system_prompt
        print(f"Configuration updated to: {config.name}")
        
    def generate_response_with_citations(self, user_question: str, limit: int = 3) -> Dict[str, Any]:
        """Generate response with citations from YouTube videos"""
        
        if self.model is None:
            return {
                "response": "Error: API key not set. Please call set_api_key() first.",
                "sources": []
            }
        
        # Search relevant videos
        search_results = self.search_service.search_videos(user_question, limit=limit)
        
        if not search_results["videos"]:
            return {
                "response": "Bu konuda video arşivimde yeterli bilgi bulamadım.",
                "sources": []
            }
        
        # Prepare video information
        video_info = []
        context_text = ""
        
        for i, (title, url, score) in enumerate(zip(
            search_results["titles"], 
            search_results["videos"], 
            search_results["scores"]
        ), 1):
            video_info.append({
                "id": i,
                "title": title,
                "url": url,
                "score": score
            })
            context_text += f"Video {i}: {title} (Benzerlik Skoru: {score})\n"
        
        # Create dynamic prompt based on configuration
        prompt = f"""
{self.system_prompt}

İlgili Video İçerikleri:
{context_text}

Kullanıcı Sorusu: {user_question}

Yanıt kuralları:
- Soruyu detaylı yanıtla
- Hangi videodan bilgi aldığını [Video 1], [Video 2] şeklinde belirt
- {self.config.language if self.config else 'Türkçe'} yanıt ver
- Sonunda kullandığın kaynakları listele
"""
        
        # Generate response
        try:
            response = self.model.generate_content(prompt)
            formatted_response = self._add_video_links(response.text, video_info)
            
            return {
                "response": formatted_response,
                "sources": video_info,
                "config_used": self.config.name if self.config else "Default"
            }
            
        except Exception as e:
            return {
                "response": f"Bir hata oluştu: {str(e)}",
                "sources": []
            }
    
    def _add_video_links(self, response: str, video_info: list) -> str:
        """Convert [Video X] references to clickable links"""
        for video in video_info:
            pattern = f"\\[Video {video['id']}\\]"
            replacement = f"[{video['title']}]({video['url']})"
            response = re.sub(pattern, replacement, response)
        return response
    
    def get_example_questions(self) -> list:
        """Get example questions for current configuration"""
        if self.config:
            return self.config.example_questions
        return [
            "Bu konular hakkında ne öğrenebilirim?",
            "Hangi videolar en faydalı?",
            "Temel kavramlar nelerdir?"
        ]
    
    def get_assistant_info(self) -> dict:
        """Get information about current assistant configuration"""
        if self.config:
            return {
                "name": self.config.name,
                "description": self.config.description,
                "language": self.config.language,
                "playlist_url": self.config.playlist_url
            }
        return {
            "name": "Generic YouTube RAG Assistant",
            "description": "AI assistant for YouTube video content",
            "language": "tr",
            "playlist_url": "Not specified"
        }

# Backward compatibility
ChatService = YouTubeRAGAssistant

# Test function
if __name__ == "__main__":
    print("YouTube RAG Assistant loaded successfully!")
    print("Usage:")
    print("assistant = YouTubeRAGAssistant()")
    print("assistant.set_api_key('your-api-key')")
    print("result = assistant.generate_response_with_citations('your question')")