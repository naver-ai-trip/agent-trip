"""Test script for LLM-based translation functionality"""

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.translator import LanguageDetector

async def test_translations():
    """Test the LLM-based translation functionality"""
    
    detector = LanguageDetector()
    
    print("=" * 60)
    print("Testing LLM-Based Translation System")
    print("=" * 60)
    
    # Test 1: Translate English to Korean
    print("\n1. English to Korean:")
    english_text = "Show me the best restaurants in Seoul"
    print(f"   Input:  {english_text}")
    korean = await detector.translate_to_korean(english_text)
    print(f"   Output: {korean}")
    
    # Test 2: Translate Korean to English
    print("\n2. Korean to English:")
    korean_text = "서울의 최고의 레스토랑을 보여주세요"
    print(f"   Input:  {korean_text}")
    english = await detector.translate_to_language(korean_text, "English")
    print(f"   Output: {english}")
    
    # Test 3: Language detection
    print("\n3. Language Detection:")
    test_cases = [
        "Hello, how are you?",
        "안녕하세요, 어떻게 지내세요?",
        "こんにちは、お元気ですか？",
        "你好，你好吗？"
    ]
    for text in test_cases:
        detected = detector.detect_language(text)
        print(f"   '{text}' → {detected}")
    
    # Test 4: Travel planning query
    print("\n4. Travel Planning Query:")
    query = "I want to visit Busan for 3 days. What should I see?"
    print(f"   Input:  {query}")
    korean_query = await detector.translate_to_korean(query)
    print(f"   Output: {korean_query}")
    
    print("\n" + "=" * 60)
    print("✓ All translation tests completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found in environment")
        print("Please set it in your .env file or environment variables")
        sys.exit(1)
    
    asyncio.run(test_translations())
