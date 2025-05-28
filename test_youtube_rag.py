# test_youtube_rag.py
# Test file for YouTube RAG Assistant

from src.services.chat_service import YouTubeRAGAssistant
import getpass

def simple_test():
    """Simple test with default configuration"""
    
    print("YouTube RAG Assistant - Simple Test")
    print("=" * 40)
    
    # Create assistant with default settings
    assistant = YouTubeRAGAssistant()
    
    # Get API key securely
    print("Enter your Gemini API key:")
    api_key = getpass.getpass("API Key: ")
    
    # Set API key
    assistant.set_api_key(api_key)
    
    # Test questions
    test_questions = [
        "Etkili liderlik için en önemli özellikler nelerdir?",
        "Takım motivasyonu nasıl sağlanır?",
        "İş hayatında başarı için ne gerekli?"
    ]
    
    print("\nTesting with sample questions...")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n[Test {i}] Question: {question}")
        
        result = assistant.generate_response_with_citations(question)
        
        print(f"Response: {result['response'][:200]}...")
        print(f"Sources found: {len(result['sources'])}")
        
        if result['sources']:
            for j, source in enumerate(result['sources'], 1):
                print(f"  {j}. {source['title']} (Score: {source['score']})")
    
    return assistant

def interactive_test(assistant):
    """Interactive testing"""
    print("\n" + "=" * 50)
    print("Interactive Mode")
    print("Type your questions in Turkish")
    print("Type 'quit' to exit")
    print("=" * 50)
    
    while True:
        question = input("\nYour question: ")
        
        if question.lower() == 'quit':
            break
            
        result = assistant.generate_response_with_citations(question)
        print(f"\nAnswer: {result['response']}")
        print(f"Sources: {len(result['sources'])} videos used")

def main():
    """Main test function"""
    print("Starting YouTube RAG Assistant Test")
    
    # Run simple test first
    assistant = simple_test()
    
    # Ask if user wants interactive mode
    while True:
        choice = input("\nDo you want to try interactive mode? (y/n): ").lower()
        if choice in ['y', 'yes']:
            interactive_test(assistant)
            break
        elif choice in ['n', 'no']:
            break
        else:
            print("Please enter 'y' or 'n'")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()