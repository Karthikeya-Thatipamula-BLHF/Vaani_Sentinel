"""
Language Mapper for Vaani Sentinel X
Task 4 Component 1: Language Metadata Enhancer
Auto-detect user language preference and expand content metadata schema
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

class LanguageMapper:
    """
    Language Metadata Enhancer that auto-detects user language preferences
    and expands content_metadata.json schema as per Task 4 requirements
    """
    
    def __init__(self):
        self.config_dir = "./config"
        
        # Load configurations
        self.user_profiles = self._load_user_profiles()
        self.language_voice_map = self._load_language_voice_map()
        
        # Supported languages (10 Indian + 10 Global as per Task 4)
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
    
    def _load_user_profiles(self) -> Dict[str, Any]:
        """Load user profiles from JSON file"""
        profiles_path = os.path.join(self.config_dir, "user_profiles.json")
        
        try:
            with open(profiles_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading user profiles: {e}")
            return {"user_profiles": {}}
    
    def _load_language_voice_map(self) -> Dict[str, Any]:
        """Load language voice mapping from JSON file"""
        voice_map_path = os.path.join(self.config_dir, "language_voice_map.json")
        
        try:
            with open(voice_map_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading language voice map: {e}")
            return {"language_voice_mapping": {}, "fallback_voices": {}}
    
    def detect_user_language_preference(
        self, 
        user_profile_id: str = "general",
        content_text: str = "",
        platform: str = "twitter"
    ) -> Dict[str, Any]:
        """
        Auto-detect or simulate user language preference from user_profile.json
        Task 4 Component 1 implementation
        """
        
        # Get user profile
        user_profiles_dict = self.user_profiles.get("user_profiles", {})
        user_profile = user_profiles_dict.get(user_profile_id, {})
        
        # Extract language preferences
        preferred_languages = user_profile.get("language_preferences", ["en"])
        primary_language = preferred_languages[0] if preferred_languages else "en"
        
        # Auto-detect content language (simplified simulation for Task 4)
        content_language = self._simulate_content_language_detection(content_text, primary_language)
        
        # Get appropriate voice tag
        voice_tag = self._get_voice_tag_for_language(content_language, user_profile.get("preferred_tone", "neutral"))
        
        return {
            "user_profile_id": user_profile_id,
            "preferred_languages": preferred_languages,
            "primary_language": primary_language,
            "content_language": content_language,
            "voice_tag": voice_tag,
            "detection_confidence": 0.85,  # Simulated confidence
            "platform": platform,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _simulate_content_language_detection(self, content_text: str, fallback_language: str) -> str:
        """
        Simulate content language detection (placeholder for Task 4)
        In Task 5, this would use actual NLP/LLM detection
        """
        
        # Simple keyword-based detection for simulation
        language_keywords = {
            "hi": ["नमस्ते", "धन्यवाद", "आप", "है", "में", "और", "का", "की", "से"],
            "sa": ["नमः", "श्री", "ॐ", "मन्त्र", "योग", "धर्म", "आत्मा", "ब्रह्म"],
            "mr": ["नमस्कार", "धन्यवाद", "आहे", "आणि", "मी", "तुम्ही"],
            "es": ["hola", "gracias", "por", "favor", "sí", "no", "muy", "bien"],
            "fr": ["bonjour", "merci", "s'il", "vous", "plaît", "oui", "non", "très"],
            "de": ["hallo", "danke", "bitte", "ja", "nein", "sehr", "gut", "wie"],
            "ja": ["こんにちは", "ありがとう", "はい", "いいえ", "です", "ます"],
            "zh": ["你好", "谢谢", "是", "不", "很", "好", "的", "在"]
        }
        
        content_lower = content_text.lower()
        
        # Check for language-specific keywords
        for lang, keywords in language_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    return lang
        
        # Fallback to user's primary language
        return fallback_language
    
    def _get_voice_tag_for_language(self, language: str, tone: str = "neutral") -> str:
        """Get appropriate voice tag for language and tone"""
        
        language_voices = self.language_voice_map.get("language_voice_mapping", {}).get(language, {})
        
        # Try to get tone-specific voice
        tone_voice = language_voices.get(tone, {})
        if tone_voice and "voice_tag" in tone_voice:
            return tone_voice["voice_tag"]
        
        # Fallback to neutral tone for the language
        neutral_voice = language_voices.get("neutral", {})
        if neutral_voice and "voice_tag" in neutral_voice:
            return neutral_voice["voice_tag"]
        
        # Fallback to first available voice for the language
        if language_voices:
            first_tone = list(language_voices.keys())[0]
            first_voice = language_voices[first_tone]
            if "voice_tag" in first_voice:
                return first_voice["voice_tag"]
        
        # Final fallback to English default
        fallback_voices = self.language_voice_map.get("fallback_voices", {})
        return fallback_voices.get("default_neutral", "en_us_neutral")
    
    def expand_content_metadata_schema(
        self,
        original_metadata: Dict[str, Any],
        user_profile_id: str = "general",
        content_text: str = "",
        platform: str = "twitter"
    ) -> Dict[str, Any]:
        """
        Expand content_metadata.json schema with new fields as per Task 4
        
        New schema fields:
        - preferred_languages: list
        - content_language: auto-filled
        - voice_tag: e.g., "hindi_female_1" or "japanese_male_2"
        """
        
        # Get language detection results
        language_info = self.detect_user_language_preference(
            user_profile_id, content_text, platform
        )
        
        # Expand metadata schema
        expanded_metadata = original_metadata.copy()
        
        # Add Task 4 required fields
        expanded_metadata.update({
            "preferred_languages": language_info["preferred_languages"],
            "content_language": language_info["content_language"],
            "voice_tag": language_info["voice_tag"],
            
            # Additional metadata enhancements
            "user_profile_id": user_profile_id,
            "primary_language": language_info["primary_language"],
            "detection_confidence": language_info["detection_confidence"],
            "language_detection_method": "simulated_keyword_based",  # Task 4 simulation
            "voice_mapping_applied": True,
            "metadata_version": "task4_enhanced",
            "enhanced_at": language_info["timestamp"]
        })
        
        return expanded_metadata
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages (20 total: 10 Indian + 10 Global)"""
        return self.supported_languages.copy()
    
    def get_language_statistics(self) -> Dict[str, Any]:
        """Get statistics about language support and voice mapping"""
        
        voice_mapping = self.language_voice_map.get("language_voice_mapping", {})
        
        stats = {
            "total_supported_languages": len(self.supported_languages),
            "indian_languages": 10,
            "global_languages": 10,
            "languages_with_voice_mapping": len(voice_mapping),
            "total_voice_variants": sum(len(voices) for voices in voice_mapping.values()),
            "fallback_voices_available": len(self.language_voice_map.get("fallback_voices", {})),
            "user_profiles_count": len(self.user_profiles.get("user_profiles", {}))
        }
        
        return stats
    
    def validate_language_support(self, language: str) -> Dict[str, Any]:
        """Validate if a language is supported and has voice mapping"""
        
        is_supported = language in self.supported_languages
        voice_mapping = self.language_voice_map.get("language_voice_mapping", {})
        has_voice_mapping = language in voice_mapping
        
        voice_variants = []
        if has_voice_mapping:
            voice_variants = list(voice_mapping[language].keys())
        
        return {
            "language": language,
            "language_name": self.supported_languages.get(language, "Unknown"),
            "is_supported": is_supported,
            "has_voice_mapping": has_voice_mapping,
            "voice_variants": voice_variants,
            "voice_count": len(voice_variants),
            "fallback_available": len(self.language_voice_map.get("fallback_voices", {})) > 0
        }

# Global language mapper instance
language_mapper = LanguageMapper()

def get_language_mapper() -> LanguageMapper:
    """Get the global language mapper instance"""
    return language_mapper
