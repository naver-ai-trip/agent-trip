"""Translation utilities using LLM for multilingual support."""

from typing import Optional
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import re

logger = logging.getLogger(__name__)


class LanguageDetector:
    """Detect and translate text using LLM."""
    
    def __init__(self):
        """Initialize the LLM for translation."""
        from src.config import settings
        self.llm = ChatOpenAI(
            model=settings.MODEL_NAME,
            temperature=0.3,  # Lower temperature for more consistent translations
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    def detect_language(self, text: str) -> str:
        """Detect the language of the input text using simple heuristics.
        
        Args:
            text: Text to detect language from
            
        Returns:
            ISO 639-1 language code (e.g., 'en', 'ko', 'ja')
        """
        try:
            # Simple heuristic: check for Korean characters
            if re.search(r'[가-힣]', text):
                logger.info("Detected language: ko (Korean)")
                return "ko"
            # Check for Japanese characters
            elif re.search(r'[ぁ-んァ-ン]', text):
                logger.info("Detected language: ja (Japanese)")
                return "ja"
            # Check for Chinese characters
            elif re.search(r'[\u4e00-\u9fff]', text):
                logger.info("Detected language: zh (Chinese)")
                return "zh"
            else:
                # Default to English
                logger.info("Detected language: en (English)")
                return "en"
        except Exception as e:
            logger.warning(f"Language detection failed: {e}. Defaulting to 'en'")
            return "en"
    
    async def translate_to_korean(self, text: str) -> str:
        """Translate text to Korean using LLM.
        
        Args:
            text: Text to translate
            
        Returns:
            Translated Korean text
        """
        try:
            # Check if already Korean
            if self.detect_language(text) == "ko":
                return text
            
            # Use LLM to translate
            messages = [
                SystemMessage(content="You are a professional translator. Translate the given text to Korean. Return ONLY the Korean translation, nothing else."),
                HumanMessage(content=f"Translate to Korean: {text}")
            ]
            
            response = await self.llm.ainvoke(messages)
            translated = response.content.strip()
            
            logger.info(f"Translated to Korean: {text} -> {translated}")
            return translated
            
        except Exception as e:
            logger.error(f"Translation to Korean failed: {e}")
            return text
    
    async def translate_to_language(self, text: str, target_lang: str) -> str:
        """Translate text to target language using LLM.
        
        Args:
            text: Text to translate
            target_lang: Target language code (en, ko, ja, zh, etc.)
            
        Returns:
            Translated text
        """
        try:
            lang_names = {
                "en": "English",
                "ko": "Korean",
                "ja": "Japanese",
                "zh": "Chinese",
                "es": "Spanish",
                "fr": "French",
                "de": "German"
            }
            
            target_lang_name = lang_names.get(target_lang, "English")
            
            messages = [
                SystemMessage(content=f"You are a professional translator. Translate the given text to {target_lang_name}. Return ONLY the translation, nothing else."),
                HumanMessage(content=f"Translate: {text}")
            ]
            
            response = await self.llm.ainvoke(messages)
            translated = response.content.strip()
            
            logger.info(f"Translated to {target_lang_name}: {translated}")
            return translated
            
        except Exception as e:
            logger.error(f"Translation to {target_lang} failed: {e}")
            return text
    
    def extract_korean_name(self, text: str) -> Optional[str]:
        """Extract Korean name from text with parentheses.
        
        Args:
            text: Text containing both English and Korean (e.g., "Gyeongbokgung Palace (경복궁)")
            
        Returns:
            Korean name if found, otherwise None
        """
        # Pattern to match Korean characters in parentheses
        pattern = r'\(([가-힣\s]+)\)'
        match = re.search(pattern, text)
        
        if match:
            korean_name = match.group(1).strip()
            logger.info(f"Extracted Korean name: {korean_name}")
            return korean_name
        
        # Check if the entire text is Korean
        if re.search(r'[가-힣]', text):
            return text
        
        return None


# Global translator instance
language_detector = LanguageDetector()
