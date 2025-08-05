"""
Configuration settings for Vaani Sentinel X
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # API Keys
    google_gemini_api_key: str
    groq_api_key: str
    elevenlabs_api_key: str = ""
    
    # Database
    database_url: str = "sqlite:///./vaani_sentinel.db"
    redis_url: str = "redis://localhost:6379"
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 43200  # 30 days (30 * 24 * 60 minutes)
    
    # Application
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    environment: str = "development"
    
    # Content
    max_content_size: int = 10485760  # 10MB
    supported_languages: str = "en,hi,sa,mr,gu,ta,te,kn,ml,bn,de,fr,es,it,pt,ru,ja,ko,zh,ar"
    default_language: str = "en"
    
    # Security Features
    profanity_check_enabled: bool = True
    bias_detection_enabled: bool = True
    content_encryption_enabled: bool = True
    
    # TTS
    google_tts_credentials_path: str = "./config/google-tts-credentials.json"

    # AI Model Configuration - Optimized for FREE TIER
    # Best free models based on performance, speed, and availability
    gemini_model: str = "gemini-1.5-flash"  # Free: 15 RPM, 1M tokens/day, fast
    groq_model: str = "llama-3.1-8b-instant"  # Free: 30 RPM, 14.4k/day, fastest
    groq_fallback_model: str = "mixtral-8x7b-32768"  # Free: reliable backup

    # Model selection strategy - Groq first (faster + higher limits)
    primary_ai_provider: str = "groq"  # Primary: Groq (faster, higher free limits)
    fallback_ai_provider: str = "gemini"  # Fallback: Gemini (reliable)

    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def supported_languages_list(self) -> List[str]:
        return self.supported_languages.split(",")


# Global settings instance
settings = Settings()

# Language configurations
LANGUAGE_CONFIGS = {
    "en": {"name": "English", "voice_type": "en-US", "region": "US"},
    "hi": {"name": "Hindi", "voice_type": "hi-IN", "region": "IN"},
    "sa": {"name": "Sanskrit", "voice_type": "hi-IN", "region": "IN"},  # Fallback to Hindi
    "mr": {"name": "Marathi", "voice_type": "mr-IN", "region": "IN"},
    "gu": {"name": "Gujarati", "voice_type": "gu-IN", "region": "IN"},
    "ta": {"name": "Tamil", "voice_type": "ta-IN", "region": "IN"},
    "te": {"name": "Telugu", "voice_type": "te-IN", "region": "IN"},
    "kn": {"name": "Kannada", "voice_type": "kn-IN", "region": "IN"},
    "ml": {"name": "Malayalam", "voice_type": "ml-IN", "region": "IN"},
    "bn": {"name": "Bengali", "voice_type": "bn-IN", "region": "IN"},
    "de": {"name": "German", "voice_type": "de-DE", "region": "DE"},
    "fr": {"name": "French", "voice_type": "fr-FR", "region": "FR"},
    "es": {"name": "Spanish", "voice_type": "es-ES", "region": "ES"},
    "it": {"name": "Italian", "voice_type": "it-IT", "region": "IT"},
    "pt": {"name": "Portuguese", "voice_type": "pt-PT", "region": "PT"},
    "ru": {"name": "Russian", "voice_type": "ru-RU", "region": "RU"},
    "ja": {"name": "Japanese", "voice_type": "ja-JP", "region": "JP"},
    "ko": {"name": "Korean", "voice_type": "ko-KR", "region": "KR"},
    "zh": {"name": "Chinese", "voice_type": "zh-CN", "region": "CN"},
    "ar": {"name": "Arabic", "voice_type": "ar-SA", "region": "SA"},
}

# Platform configurations
PLATFORM_CONFIGS = {
    "twitter": {
        "max_length": 280,
        "hashtag_limit": 2,
        "supports_audio": True,
        "audio_max_duration": 140  # seconds
    },
    "instagram": {
        "max_length": 2200,
        "hashtag_limit": 30,
        "supports_audio": True,
        "audio_max_duration": 60
    },
    "linkedin": {
        "max_length": 3000,
        "hashtag_limit": 5,
        "supports_audio": True,
        "audio_max_duration": 30
    },
    "spotify": {
        "max_length": 500,
        "hashtag_limit": 0,
        "supports_audio": True,
        "audio_max_duration": 30
    }
}

# Content tone configurations
TONE_CONFIGS = {
    "formal": {
        "description": "Professional and formal tone",
        "platforms": ["linkedin"],
        "voice_style": "professional"
    },
    "casual": {
        "description": "Casual and friendly tone",
        "platforms": ["instagram", "twitter"],
        "voice_style": "conversational"
    },
    "devotional": {
        "description": "Spiritual and devotional tone",
        "platforms": ["spotify"],
        "voice_style": "calm"
    },
    "neutral": {
        "description": "Neutral and informative tone",
        "platforms": ["twitter", "linkedin"],
        "voice_style": "neutral"
    },
    "uplifting": {
        "description": "Positive and uplifting tone",
        "platforms": ["instagram"],
        "voice_style": "energetic"
    }
}
