"""
Lesson router for Vaani-Composer-TTV Integration
Implements /lesson/play endpoint producing complete lesson clips (text, audio, video synced)
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from api.routers.auth import get_current_user
from core.lesson_pipeline import get_lesson_orchestrator

logger = logging.getLogger(__name__)

router = APIRouter()

class LessonPlayRequest(BaseModel):
    """Request model for /lesson/play endpoint"""
    user_id: Optional[str] = None
    subject: str
    topic: str
    grade_level: str = "class_8"
    language: str = "en"
    assessment_answers: Optional[List[str]] = None  # If provided, skip assessment
    voice_preference: str = "gurukul_neutral"
    video_quality: str = "720p"

class LessonPlayResponse(BaseModel):
    """Response model for /lesson/play endpoint"""
    playback_id: str
    lesson_id: str
    video_url: str
    audio_url: str
    text_content: str
    citations: List[Dict[str, Any]]
    language: str
    duration_seconds: int
    created_at: datetime
    pipeline_latency_ms: int

class LessonPreviewRequest(BaseModel):
    """Request model for lesson preview"""
    lesson_id: str
    voice: str = "gurukul_neutral"
    language: str = "en"

class LessonPreviewResponse(BaseModel):
    """Response model for lesson preview"""
    lesson_id: str
    preview_audio_url: str
    preview_text: str
    estimated_duration: int
    language: str

@router.post("/play", response_model=LessonPlayResponse)
async def play_lesson(
    request: LessonPlayRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Main lesson play endpoint - produces complete lesson clips (text, audio, video synced)"""
    try:
        orchestrator = get_lesson_orchestrator()

        # Use provided user_id or get from current user
        user_id = request.user_id or current_user.get("user_id")

        # Orchestrate full pipeline
        result = await orchestrator.orchestrate_full_pipeline(
            user_id=user_id,
            subject=request.subject,
            topic=request.topic,
            grade_level=request.grade_level,
            language=request.language,
            assessment_answers=request.assessment_answers
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lesson pipeline failed: {result.get('error', 'Unknown error')}"
            )

        # Calculate duration from text length (rough estimate)
        duration_seconds = len(result["text_content"].split()) * 0.5  # ~0.5 seconds per word

        return LessonPlayResponse(
            playback_id=result["playback_id"],
            lesson_id=result["lesson_id"],
            video_url=result["video_url"],
            audio_url=result["audio_url"],
            text_content=result["text_content"],
            citations=result["citations"],
            language=request.language,
            duration_seconds=int(duration_seconds),
            created_at=datetime.utcnow(),
            pipeline_latency_ms=result["total_latency_ms"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lesson play error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lesson playback failed: {str(e)}"
        )

@router.post("/preview", response_model=LessonPreviewResponse)
async def preview_lesson(
    request: LessonPreviewRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate lesson preview (audio + text) without full video pipeline"""
    try:
        orchestrator = get_lesson_orchestrator()

        # Get lesson and composition data
        from core.database import get_db, Lesson, LessonComposition
        db = next(get_db())
        try:
            lesson = db.query(Lesson).filter(
                Lesson.lesson_id == request.lesson_id
            ).first()

            if not lesson:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lesson not found"
                )

            # Get or create composition
            composition = db.query(LessonComposition).filter(
                LessonComposition.lesson_id == request.lesson_id,
                LessonComposition.language == request.language
            ).first()

            if not composition:
                # Create composition on the fly
                composition_id = await orchestrator.compose_lesson_text(
                    request.lesson_id,
                    current_user.get("user_id"),
                    request.language
                )

                composition = db.query(LessonComposition).filter(
                    LessonComposition.composition_id == composition_id
                ).first()

            if not composition:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lesson composition not found"
                )

            # Generate audio preview
            audio_result = await orchestrator.generate_audio_content(
                composition.composition_id,
                request.voice
            )

            # Estimate duration
            duration_seconds = len(composition.composed_text.split()) * 0.5

            return LessonPreviewResponse(
                lesson_id=request.lesson_id,
                preview_audio_url=audio_result["audio_url"],
                preview_text=composition.composed_text[:500] + "..." if len(composition.composed_text) > 500 else composition.composed_text,
                estimated_duration=int(duration_seconds),
                language=request.language
            )

        finally:
            db.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lesson preview error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lesson preview failed: {str(e)}"
        )

@router.get("/subjects")
async def get_supported_subjects():
    """Get list of supported subjects for lessons"""
    return {
        "subjects": [
            {"code": "mathematics", "name": "Mathematics", "description": "Numbers, algebra, geometry"},
            {"code": "science", "name": "Science", "description": "Physics, chemistry, biology"},
            {"code": "history", "name": "History", "description": "Historical events and civilizations"},
            {"code": "geography", "name": "Geography", "description": "World geography and cultures"},
            {"code": "literature", "name": "Literature", "description": "Stories, poems, and writing"},
            {"code": "computer_science", "name": "Computer Science", "description": "Programming and technology"}
        ],
        "grade_levels": [
            {"code": "class_1", "name": "Class 1", "age_range": "6-7 years"},
            {"code": "class_2", "name": "Class 2", "age_range": "7-8 years"},
            {"code": "class_3", "name": "Class 3", "age_range": "8-9 years"},
            {"code": "class_4", "name": "Class 4", "age_range": "9-10 years"},
            {"code": "class_5", "name": "Class 5", "age_range": "10-11 years"},
            {"code": "class_6", "name": "Class 6", "age_range": "11-12 years"},
            {"code": "class_7", "name": "Class 7", "age_range": "12-13 years"},
            {"code": "class_8", "name": "Class 8", "age_range": "13-14 years"},
            {"code": "class_9", "name": "Class 9", "age_range": "14-15 years"},
            {"code": "class_10", "name": "Class 10", "age_range": "15-16 years"}
        ]
    }

@router.get("/playback/{playback_id}")
async def get_lesson_playback(
    playback_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get lesson playback details"""
    try:
        from core.database import get_db, LessonPlayback
        db = next(get_db())
        try:
            playback = db.query(LessonPlayback).filter(
                LessonPlayback.playback_id == playback_id
            ).first()

            if not playback:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Playback not found"
                )

            return {
                "playback_id": playback.playback_id,
                "lesson_id": playback.lesson_id,
                "video_url": playback.video_url,
                "audio_url": playback.audio_url,
                "text_content": playback.text_content,
                "citations": playback.citations,
                "lip_sync_score": playback.lip_sync_score,
                "latency_ms": playback.latency_ms,
                "created_at": playback.created_at,
                "metadata": playback.playback_metadata
            }

        finally:
            db.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get playback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get playback: {str(e)}"
        )

@router.get("/performance_stats")
async def get_lesson_performance_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get performance statistics for lesson pipeline"""
    try:
        # This would typically aggregate from database
        # For now, return mock stats
        return {
            "total_lessons_generated": 0,
            "total_playbacks": 0,
            "average_pipeline_latency_ms": 5000,
            "average_lip_sync_score": 0.85,
            "language_distribution": {
                "en": 0.6,
                "hi": 0.4
            },
            "subject_popularity": {
                "mathematics": 0.3,
                "science": 0.25,
                "history": 0.2,
                "geography": 0.15,
                "literature": 0.1
            },
            "grade_level_distribution": {
                "class_8": 0.4,
                "class_9": 0.3,
                "class_7": 0.2,
                "class_10": 0.1
            },
            "target_latency_ms": 3000,
            "target_lip_sync_score": 0.9,
            "pipeline_success_rate": 0.95
        }

    except Exception as e:
        logger.error(f"Get performance stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance stats: {str(e)}"
        )

@router.post("/create_assessment")
async def create_lesson_assessment(
    subject: str,
    topic: str,
    difficulty_level: str = "intermediate",
    current_user: dict = Depends(get_current_user)
):
    """Create assessment for lesson pipeline"""
    try:
        orchestrator = get_lesson_orchestrator()

        assessment_id = await orchestrator.create_assessment(
            user_id=current_user.get("user_id"),
            subject=subject,
            topic=topic,
            difficulty_level=difficulty_level
        )

        return {
            "assessment_id": assessment_id,
            "status": "created",
            "message": "Assessment created successfully. Provide answers to evaluate.",
            "next_step": "evaluate_assessment"
        }

    except Exception as e:
        logger.error(f"Create assessment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create assessment: {str(e)}"
        )

@router.post("/evaluate_assessment")
async def evaluate_lesson_assessment(
    assessment_id: str,
    answers: List[str],
    current_user: dict = Depends(get_current_user)
):
    """Evaluate assessment answers"""
    try:
        orchestrator = get_lesson_orchestrator()

        results = await orchestrator.evaluate_assessment(assessment_id, answers)

        return {
            "assessment_id": assessment_id,
            "evaluation_results": results,
            "next_step": "generate_curriculum",
            "recommended_difficulty": results["knowledge_level"]
        }

    except Exception as e:
        logger.error(f"Evaluate assessment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate assessment: {str(e)}"
        )
