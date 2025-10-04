"""
Converse router for Vaani-Converse dialogue system
Implements /vaani_converse endpoint connecting NLP + native TTS with <3s latency
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from api.routers.auth import get_current_user
from core.conversation_manager import get_conversation_manager

logger = logging.getLogger(__name__)

router = APIRouter()

class ConverseRequest(BaseModel):
    """Request model for /vaani_converse endpoint"""
    conversation_id: Optional[str] = None  # None for new conversation
    user_input: str
    input_type: str = "text"  # text, speech, gesture
    language: Optional[str] = None  # Auto-detect if None
    conversation_type: str = "general_chat"  # general_chat, lesson, assessment
    context_override: Optional[Dict[str, Any]] = None

class ConverseResponse(BaseModel):
    """Response model for /vaani_converse endpoint"""
    conversation_id: str
    response: str
    audio_url: str
    language: str
    emotional_response: str
    latency_ms: int
    turn_number: int
    context_memory: Dict[str, Any]

class ConversationStatus(BaseModel):
    """Conversation status response"""
    conversation_id: str
    status: str
    turn_count: int
    language: str
    conversation_type: str
    current_topic: str
    emotional_state: str
    started_at: datetime
    last_activity: datetime

@router.post("/vaani_converse", response_model=ConverseResponse)
async def vaani_converse(
    request: ConverseRequest,
    current_user: dict = Depends(get_current_user)
):
    """Main converse endpoint - spoken dialogue loop with NLP + TTS"""
    try:
        manager = get_conversation_manager()

        # Start new conversation if none provided
        conversation_id = request.conversation_id
        if not conversation_id:
            conversation_id = manager.start_conversation(
                user_id=current_user.get("user_id", "anonymous"),
                conversation_type=request.conversation_type,
                language=request.language,
                initial_context=request.context_override
            )

        # Process the conversation turn
        result = manager.process_turn(
            conversation_id=conversation_id,
            user_input=request.user_input,
            input_type=request.input_type,
            language=request.language
        )

        return ConverseResponse(
            conversation_id=result["conversation_id"],
            response=result["response"],
            audio_url=result["audio_url"],
            language=result["language"],
            emotional_response=result["emotional_response"],
            latency_ms=result["latency_ms"],
            turn_number=result["turn_number"],
            context_memory=result["context_memory"]
        )

    except Exception as e:
        logger.error(f"Vaani converse error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversation processing failed: {str(e)}"
        )

@router.post("/start_conversation")
async def start_new_conversation(
    conversation_type: str = "general_chat",
    language: str = "en",
    initial_context: Optional[Dict[str, Any]] = None,
    current_user: dict = Depends(get_current_user)
):
    """Start a new conversation session"""
    try:
        manager = get_conversation_manager()

        conversation_id = manager.start_conversation(
            user_id=current_user.get("user_id", "anonymous"),
            conversation_type=conversation_type,
            language=language,
            initial_context=initial_context
        )

        return {
            "conversation_id": conversation_id,
            "status": "started",
            "message": "New conversation started successfully"
        }

    except Exception as e:
        logger.error(f"Start conversation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start conversation: {str(e)}"
        )

@router.get("/conversation/{conversation_id}/status", response_model=ConversationStatus)
async def get_conversation_status(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get conversation status and metadata"""
    try:
        manager = get_conversation_manager()
        status_info = manager.get_conversation_status(conversation_id)

        if "error" in status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=status_info["error"]
            )

        return ConversationStatus(**status_info)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get conversation status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation status: {str(e)}"
        )

@router.delete("/conversation/{conversation_id}")
async def end_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """End a conversation session"""
    try:
        manager = get_conversation_manager()

        success = manager.end_conversation(conversation_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        return {
            "conversation_id": conversation_id,
            "status": "ended",
            "message": "Conversation ended successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"End conversation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end conversation: {str(e)}"
        )

@router.get("/conversation_types")
async def get_supported_conversation_types():
    """Get supported conversation types"""
    return {
        "conversation_types": [
            {
                "code": "general_chat",
                "name": "General Chat",
                "description": "General conversational assistance"
            },
            {
                "code": "lesson",
                "name": "Lesson Support",
                "description": "Educational content and learning assistance"
            },
            {
                "code": "assessment",
                "name": "Assessment",
                "description": "Knowledge assessment and testing"
            }
        ],
        "default_type": "general_chat"
    }

@router.get("/performance_stats")
async def get_conversation_performance_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get performance statistics for conversation system"""
    try:
        # This would typically aggregate from database
        # For now, return mock stats
        return {
            "total_conversations": 0,
            "active_conversations": 0,
            "average_latency_ms": 1500,
            "average_turns_per_conversation": 5,
            "language_distribution": {
                "en": 0.7,
                "hi": 0.3
            },
            "conversation_types": {
                "general_chat": 0.6,
                "lesson": 0.3,
                "assessment": 0.1
            },
            "target_latency_ms": 3000,
            "cache_hit_rate": 0.0
        }

    except Exception as e:
        logger.error(f"Get performance stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance stats: {str(e)}"
        )
