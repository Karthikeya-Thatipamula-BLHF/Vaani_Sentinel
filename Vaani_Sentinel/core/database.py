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
