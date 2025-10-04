"""
Database configuration and models for Vaani Sentinel X
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from datetime import datetime
from core.config import settings
import asyncio

# Database setup
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Content(Base):
    __tablename__ = "contents"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(String, unique=True, index=True)
    original_text = Column(Text)
    language = Column(String, default="en")
    content_type = Column(String)  # tweet, instagram_post, voice_script
    content_metadata = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_verified = Column(Boolean, default=False)
    verification_score = Column(Float, default=0.0)

class TranslatedContent(Base):
    __tablename__ = "translated_contents"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(String, index=True)
    original_content_id = Column(String, index=True)
    language = Column(String)
    translated_text = Column(Text)
    confidence_score = Column(Float)
    tone = Column(String)
    platform = Column(String)
    created_at = Column(DateTime, default=func.now())

class ScheduledPost(Base):
    __tablename__ = "scheduled_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String, unique=True, index=True)
    content_id = Column(String, index=True)
    platform = Column(String)
    scheduled_time = Column(DateTime)
    status = Column(String, default="scheduled")  # scheduled, published, failed
    post_metadata = Column(JSON)
    created_at = Column(DateTime, default=func.now())

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String, index=True)
    platform = Column(String)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    preferred_languages = Column(JSON)
    tone_preferences = Column(JSON)
    platform_preferences = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class SecurityLog(Base):
    __tablename__ = "security_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(String, index=True)
    flag_type = Column(String)  # profanity, bias, controversy
    severity = Column(String)  # low, medium, high, critical
    details = Column(JSON)
    action_taken = Column(String)
    created_at = Column(DateTime, default=func.now())

class TTSOutput(Base):
    __tablename__ = "tts_outputs"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(String, index=True)
    language = Column(String)
    voice_tag = Column(String)
    tone = Column(String)
    audio_path = Column(String)
    duration = Column(Float)
    created_at = Column(DateTime, default=func.now())

class NativeTTSOutput(Base):
    """Native TTS Output - Production-ready tracking for indigenous TTS with RL prosody control.
    Extends existing TTS architecture while maintaining compatibility with existing Agent B patterns.
    Tracks prosody parameters, quality metrics, and RL controller performance for Gurukul voice identity."""
    __tablename__ = "native_tts_outputs"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(String, index=True)
    text_hash = Column(String, index=True)  # For caching (same as existing TTS cache pattern)
    prosody_params = Column(JSON)  # RL-controlled: pitch_shift, speed, energy, emotion
    model_version = Column(String)  # gurukul_tts_adapter_v1, etc.
    audio_path = Column(String)
    latency_ms = Column(Integer)  # Performance tracking: <500ms cached, <2000ms new
    cache_hit = Column(Boolean, default=False)
    quality_score = Column(Float)  # MOS-proxy: spectral distance + quality metrics
    language = Column(String)
    voice_tag = Column(String)  # gurukul_neutral, gurukul_warm, etc.
    duration = Column(Float)  # Audio duration in seconds
    created_at = Column(DateTime, default=func.now())

class Assessment(Base):
    """Assessment entity for lesson pipeline - tracks user knowledge levels and learning goals"""
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    subject = Column(String)  # mathematics, science, history, etc.
    topic = Column(String)  # specific topic within subject
    difficulty_level = Column(String)  # beginner, intermediate, advanced
    current_score = Column(Float, default=0.0)  # 0.0 to 1.0
    questions_asked = Column(JSON)  # list of question IDs
    answers_given = Column(JSON)  # list of answers
    assessment_metadata = Column(JSON)  # additional assessment data
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Curriculum(Base):
    """Curriculum entity - defines learning paths and module structures"""
    __tablename__ = "curriculums"

    id = Column(Integer, primary_key=True, index=True)
    curriculum_id = Column(String, unique=True, index=True)
    title = Column(String)
    subject = Column(String)
    grade_level = Column(String)  # class 1, class 2, etc.
    language = Column(String, default="en")
    modules = Column(JSON)  # list of module objects with topics, objectives
    prerequisites = Column(JSON)  # prerequisite knowledge requirements
    learning_objectives = Column(JSON)  # main learning goals
    estimated_duration = Column(Integer)  # in minutes
    curriculum_metadata = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Lesson(Base):
    """Lesson entity - individual learning units within curriculum"""
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(String, unique=True, index=True)
    curriculum_id = Column(String, index=True)
    title = Column(String)
    content = Column(Text)  # lesson text content
    language = Column(String, default="en")
    lesson_type = Column(String)  # theory, practice, assessment, interactive
    objectives = Column(JSON)  # learning objectives for this lesson
    media_urls = Column(JSON)  # associated images, videos, audio
    duration = Column(Integer)  # estimated duration in minutes
    difficulty_level = Column(String)
    prerequisites = Column(JSON)  # prerequisite lessons or knowledge
    lesson_metadata = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class LessonComposition(Base):
    """Composed lesson output from indigenous NLP processing"""
    __tablename__ = "lesson_compositions"

    id = Column(Integer, primary_key=True, index=True)
    composition_id = Column(String, unique=True, index=True)
    lesson_id = Column(String, index=True)
    user_id = Column(String, index=True)
    original_text = Column(Text)
    composed_text = Column(Text)  # processed by indigenous NLP
    language = Column(String, default="en")
    tone = Column(String, default="educational")
    cultural_adaptations = Column(JSON)  # cultural context adjustments
    nlp_metadata = Column(JSON)  # NLP processing results
    composition_quality = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())

class Conversation(Base):
    """Conversation entity for vaani_converse dialogue system"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    session_id = Column(String, index=True)  # for grouping related conversations
    conversation_type = Column(String)  # lesson, general_chat, assessment
    language = Column(String, default="en")
    context_memory = Column(JSON)  # conversation history and context
    current_topic = Column(String)
    emotional_state = Column(String)  # user emotional context
    conversation_metadata = Column(JSON)
    started_at = Column(DateTime, default=func.now())
    last_activity = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class ConversationTurn(Base):
    """Individual turns within a conversation"""
    __tablename__ = "conversation_turns"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, index=True)
    turn_number = Column(Integer)
    user_input = Column(Text)
    user_input_type = Column(String)  # text, speech, gesture
    system_response = Column(Text)
    response_audio_url = Column(String)
    response_video_url = Column(String)
    nlp_processing = Column(JSON)  # NLP analysis results
    emotional_response = Column(String)
    latency_ms = Column(Integer)
    created_at = Column(DateTime, default=func.now())

class LessonPlayback(Base):
    """Lesson playback tracking for /lesson/play endpoint"""
    __tablename__ = "lesson_playbacks"

    id = Column(Integer, primary_key=True, index=True)
    playback_id = Column(String, unique=True, index=True)
    lesson_id = Column(String, index=True)
    user_id = Column(String, index=True)
    video_url = Column(String)
    audio_url = Column(String)
    text_content = Column(Text)
    citations = Column(JSON)
    playback_metadata = Column(JSON)
    lip_sync_score = Column(Float, default=0.0)  # lip-sync quality metric
    latency_ms = Column(Integer)  # end-to-end latency
    created_at = Column(DateTime, default=func.now())

# Database dependency
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database
async def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")

# Database utilities
class DatabaseManager:
    @staticmethod
    def create_content(db: Session, content_data: dict) -> Content:
        """Create new content entry"""
        content = Content(**content_data)
        db.add(content)
        db.commit()
        db.refresh(content)
        return content
    
    @staticmethod
    def get_content_by_id(db: Session, content_id: str) -> Content:
        """Get content by ID"""
        return db.query(Content).filter(Content.content_id == content_id).first()
    
    @staticmethod
    def create_scheduled_post(db: Session, post_data: dict) -> ScheduledPost:
        """Create scheduled post entry"""
        post = ScheduledPost(**post_data)
        db.add(post)
        db.commit()
        db.refresh(post)
        return post
    
    @staticmethod
    def create_analytics_entry(db: Session, analytics_data: dict) -> Analytics:
        """Create analytics entry"""
        analytics = Analytics(**analytics_data)
        db.add(analytics)
        db.commit()
        db.refresh(analytics)
        return analytics
