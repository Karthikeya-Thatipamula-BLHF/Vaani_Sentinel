"""
Translation Agent for Vaani Sentinel X
Implements LLM-powered translation with confidence scoring for 20 languages
Task 5 Component 1: Translation Agent
"""

import json
import os
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from core.ai_manager import get_ai_manager
from core.config import LANGUAGE_CONFIGS

class TranslationAgent:
    """
    Dedicated translation agent with LLM integration and confidence scoring
    Supports 10 Indian + 10 global languages as per Task 5 requirements
    """
    
    def __init__(self):
        self.ai_manager = get_ai_manager()
        self.output_dir = "./data"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Supported languages (10 Indian + 10 Global)
        self.supported_languages = {
            # 10 Indian Languages
            "hi": "Hindi",
            "sa": "Sanskrit", 
            "mr": "Marathi",
            "gu": "Gujarati",
            "ta": "Tamil",
            "te": "Telugu",
            "kn": "Kannada",
            "ml": "Malayalam",
            "bn": "Bengali",
            "pa": "Punjabi",
            
            # 10 Global Languages
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese"
        }
    
    def translate_content(
        self,
        content_text: str,
        source_language: str = "en",
        target_languages: List[str] = None,
        content_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Translate content to multiple languages with confidence scoring
        
        Args:
            content_text: Text to translate
            source_language: Source language code
            target_languages: List of target language codes
            content_metadata: Additional metadata for context
            
        Returns:
            Translation results with confidence scores
        """
        
        if target_languages is None:
            # Default to all supported languages except source
            target_languages = [lang for lang in self.supported_languages.keys() 
                              if lang != source_language]
        
        translation_id = str(uuid.uuid4())
        
        translation_results = {
            "translation_id": translation_id,
            "source_language": source_language,
            "source_text": content_text,
            "target_languages": target_languages,
            "translations": {},
            "metadata": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "agent": "translation_agent",
                "version": "1.0",
                "content_metadata": content_metadata or {}
            }
        }
        
        # Translate to each target language
        for target_lang in target_languages:
            if target_lang in self.supported_languages:
                try:
                    translation_result = self._translate_to_language(
                        content_text, source_language, target_lang, content_metadata
                    )
                    translation_results["translations"][target_lang] = translation_result
                except Exception as e:
                    translation_results["translations"][target_lang] = {
                        "translated_text": content_text,  # Fallback to original
                        "confidence_score": 0.0,
                        "translation_quality": "failed",
                        "error": str(e),
                        "status": "error"
                    }
        
        # Save translation results
        self._save_translation_results(translation_results)
        
        return translation_results
    
    def _translate_to_language(
        self,
        content_text: str,
        source_lang: str,
        target_lang: str,
        content_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Translate content to a specific language with confidence scoring"""
        
        source_name = self.supported_languages.get(source_lang, source_lang)
        target_name = self.supported_languages.get(target_lang, target_lang)
        
        # Get language-specific context
        source_config = LANGUAGE_CONFIGS.get(source_lang, {})
        target_config = LANGUAGE_CONFIGS.get(target_lang, {})
        
        # Build context-aware translation prompt
        prompt = f"""
        Translate the following content from {source_name} to {target_name}.
        
        Source text: {content_text}
        
        Translation requirements:
        1. Maintain the original meaning and emotional tone
        2. Adapt cultural references appropriately for {target_name} audience
        3. Preserve any spiritual, devotional, or cultural context
        4. Use natural, fluent {target_name} language
        5. Keep the same level of formality
        6. Maintain any metaphors or poetic elements where possible
        
        Content context: {content_metadata.get('content_type', 'general') if content_metadata else 'general'}
        
        Provide ONLY the translated text, no explanations or additional content.
        """
        
        try:
            # Use AI manager for translation
            translated_text, provider_used = self.ai_manager.generate_content(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.3,  # Lower temperature for accuracy
                task_type="translation"
            )
            
            # Calculate confidence score based on various factors
            confidence_score = self._calculate_confidence_score(
                content_text, translated_text, source_lang, target_lang, provider_used
            )
            
            # Determine translation quality
            quality = self._assess_translation_quality(confidence_score)
            
            return {
                "translated_text": translated_text.strip(),
                "confidence_score": confidence_score,
                "translation_quality": quality,
                "provider_used": provider_used,
                "source_language": source_lang,
                "target_language": target_lang,
                "status": "success"
            }
            
        except Exception as e:
            raise Exception(f"Translation failed for {target_lang}: {e}")
    
    def _calculate_confidence_score(
        self,
        source_text: str,
        translated_text: str,
        source_lang: str,
        target_lang: str,
        provider_used: str
    ) -> float:
        """Calculate confidence score for translation quality"""
        
        confidence = 0.7  # Base confidence
        
        # Length ratio check (reasonable translations should have similar length ratios)
        length_ratio = len(translated_text) / len(source_text) if len(source_text) > 0 else 1.0
        
        if 0.5 <= length_ratio <= 2.0:
            confidence += 0.1
        elif 0.3 <= length_ratio <= 3.0:
            confidence += 0.05
        else:
            confidence -= 0.1
        
        # Provider reliability
        if "groq" in provider_used.lower():
            confidence += 0.1  # Groq is good for translations
        elif "gemini" in provider_used.lower():
            confidence += 0.15  # Gemini is excellent for translations
        
        # Language pair difficulty
        if source_lang == "en" and target_lang in ["hi", "sa", "mr"]:
            confidence += 0.05  # English to Indian languages is well-supported
        elif source_lang in ["hi", "sa"] and target_lang == "en":
            confidence += 0.05  # Indian languages to English
        
        # Content quality indicators
        if len(translated_text.strip()) > 0:
            confidence += 0.05
        
        if translated_text != source_text:  # Actually translated
            confidence += 0.05
        else:
            confidence -= 0.2  # Likely failed translation
        
        # Ensure confidence is between 0 and 1
        return max(0.0, min(1.0, confidence))
    
    def _assess_translation_quality(self, confidence_score: float) -> str:
        """Assess translation quality based on confidence score"""
        
        if confidence_score >= 0.8:
            return "excellent"
        elif confidence_score >= 0.6:
            return "good"
        elif confidence_score >= 0.4:
            return "fair"
        else:
            return "poor"
    
    def _save_translation_results(self, translation_results: Dict[str, Any]):
        """Save translation results to JSON file"""
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"translated_content_{translation_results['translation_id']}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(translation_results, f, indent=2, ensure_ascii=False)
            
            print(f"Translation results saved to: {filepath}")
            
        except Exception as e:
            print(f"Error saving translation results: {e}")
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.supported_languages.copy()
    
    def batch_translate(
        self,
        content_list: List[Dict[str, Any]],
        target_languages: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Batch translate multiple content items"""
        
        results = []
        
        for content_item in content_list:
            content_text = content_item.get("text", "")
            source_lang = content_item.get("language", "en")
            metadata = content_item.get("metadata", {})
            
            if content_text:
                translation_result = self.translate_content(
                    content_text=content_text,
                    source_language=source_lang,
                    target_languages=target_languages,
                    content_metadata=metadata
                )
                results.append(translation_result)
        
        return results

# Global translation agent instance
translation_agent = TranslationAgent()

def get_translation_agent() -> TranslationAgent:
    """Get the global translation agent instance"""
    return translation_agent
