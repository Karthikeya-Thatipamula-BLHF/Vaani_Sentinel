"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

# Enums
class ContentType(str, Enum):
    TWEET = "tweet"
    INSTAGRAM_POST = "instagram_post"
    LINKEDIN_POST = "linkedin_post"
    VOICE_SCRIPT = "voice_script"

class Platform(str, Enum):
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"

class Tone(str, Enum):
    FORMAL = "formal"
    CASUAL = "casual"
    DEVOTIONAL = "devotional"
    NEUTRAL = "neutral"
    UPLIFTING = "uplifting"

class PostStatus(str, Enum):
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"

# Request Models
class ContentInput(BaseModel):
    text: str = Field(..., description="Raw content text")
    content_type: Optional[ContentType] = ContentType.TWEET
    language: Optional[str] = "en"
    metadata: Optional[Dict[str, Any]] = {}

class ContentUpload(BaseModel):
    file_type: str = Field(..., description="File type: csv or json")
    data: List[Dict[str, Any]] = Field(..., description="Content data")

class TranslationRequest(BaseModel):
    content_id: str
    target_languages: List[str]
    tone: Optional[Tone] = Tone.NEUTRAL

class PersonalizationRequest(BaseModel):
    content_id: str
    user_id: str
    platform: Platform
    tone: Optional[Tone] = None

class ScheduleRequest(BaseModel):
    content_id: str
    platform: Platform
    scheduled_time: datetime
    metadata: Optional[Dict[str, Any]] = {}

class TTSRequest(BaseModel):
    content_id: str
    language: str
    voice_tag: Optional[str] = None
    tone: Optional[Tone] = Tone.NEUTRAL

# Response Models
class ContentResponse(BaseModel):
    content_id: str
    original_text: str
    language: str
    content_type: str
    metadata: Dict[str, Any]
    created_at: datetime
    is_verified: bool
    verification_score: float

class TranslatedContentResponse(BaseModel):
    content_id: str
    original_content_id: str
    language: str
    translated_text: str
    confidence_score: float
    tone: str
    platform: str
    created_at: datetime

class ScheduledPostResponse(BaseModel):
    post_id: str
    content_id: str
    platform: str
    scheduled_time: datetime
    status: str
    metadata: Dict[str, Any]
    created_at: datetime

class AnalyticsResponse(BaseModel):
    post_id: str
    platform: str
    views: int
    likes: int
    shares: int
    comments: int
    engagement_rate: float
    created_at: datetime

class TTSOutputResponse(BaseModel):
    content_id: str
    language: str
    voice_tag: str
    tone: str
    audio_path: str
    duration: float
    created_at: datetime

class SecurityFlagResponse(BaseModel):
    content_id: str
    flag_type: str
    severity: str
    details: Dict[str, Any]
    action_taken: str
    created_at: datetime

# Complex Response Models
class ContentGenerationResponse(BaseModel):
    content_id: str
    generated_content: Dict[str, str]  # platform -> content
    voice_scripts: Dict[str, str]  # language -> script
    metadata: Dict[str, Any]
    created_at: datetime

class MultilingualContentResponse(BaseModel):
    original_content_id: str
    translations: List[TranslatedContentResponse]
    tts_outputs: List[TTSOutputResponse]
    metadata: Dict[str, Any]

class PublishingPreviewResponse(BaseModel):
    post_id: str
    platform: str
    content: str
    language: str
    voice_tag: Optional[str]
    audio_path: Optional[str]
    hashtags: List[str]
    estimated_engagement: Dict[str, int]
    metadata: Dict[str, Any]

class WeeklyStrategyResponse(BaseModel):
    week_start: datetime
    top_performers: List[Dict[str, Any]]
    underperformers: List[Dict[str, Any]]
    recommendations: List[str]
    suggested_tones: List[str]
    suggested_languages: List[str]
    metadata: Dict[str, Any]

# User Profile Models
class UserProfileRequest(BaseModel):
    user_id: str
    preferred_languages: List[str]
    tone_preferences: Dict[str, float]  # tone -> preference score
    platform_preferences: Dict[str, bool]  # platform -> enabled

class UserProfileResponse(BaseModel):
    user_id: str
    preferred_languages: List[str]
    tone_preferences: Dict[str, float]
    platform_preferences: Dict[str, bool]
    created_at: datetime
    updated_at: datetime

# Error Models
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None

# Status Models
class StatusResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime
    data: Optional[Dict[str, Any]] = None
