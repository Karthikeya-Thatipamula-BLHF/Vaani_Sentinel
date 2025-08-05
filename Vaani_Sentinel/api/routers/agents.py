"""
Agents router for Vaani Sentinel X
Exposes AI agent functionality through REST APIs
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import os
from datetime import datetime

from core.database import get_db, DatabaseManager
from api.models import (
    ContentGenerationResponse, TTSRequest, TTSOutputResponse,
    StatusResponse, Platform, Tone
)
from api.routers.auth import get_current_user
from agents.ai_writer_voicegen import AIWriterVoiceGen
from agents.translation_agent import get_translation_agent
from agents.personalization_agent import get_personalization_agent
from agents.tts_simulator import get_tts_simulator
from agents.weekly_adaptive_hook import get_weekly_adaptive_hook
from agents.publisher_sim import get_multilingual_publisher_sim
from agents.analytics_collector import get_analytics_collector
from agents.strategy_recommender import get_strategy_recommender
from agents.sentiment_tuner import get_sentiment_tuner
from agents.adaptive_targeter import get_platform_targeter
from utils.language_mapper import get_language_mapper
from utils.simulate_translation import get_simulated_translator
from core.ai_manager import get_ai_manager
from pydantic import BaseModel

router = APIRouter()

# Request Models
class ContentGenerationRequest(BaseModel):
    content_id: str
    platforms: Optional[List[Platform]] = None
    tone: Optional[Tone] = Tone.NEUTRAL
    language: Optional[str] = "en"

class VoiceGenerationRequest(BaseModel):
    content_id: str
    language: str = "en"
    tone: Optional[Tone] = Tone.NEUTRAL
    voice_tag: Optional[str] = None

@router.post("/generate-content", response_model=ContentGenerationResponse)
async def generate_content_for_platforms(
    request: ContentGenerationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate platform-specific content using Agent B"""
    try:
        # Get original content
        content = DatabaseManager.get_content_by_id(db, request.content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Initialize Agent B
        ai_writer = AIWriterVoiceGen()
        
        # Convert platforms to strings
        platforms = [p.value for p in request.platforms] if request.platforms else None
        
        # Generate content
        result = ai_writer.generate_content_for_platforms(
            content_text=content.original_text,
            content_id=request.content_id,
            platforms=platforms,
            tone=request.tone.value,
            language=request.language
        )
        
        return ContentGenerationResponse(
            content_id=result["content_id"],
            generated_content=result["generated_content"],
            voice_scripts=result["voice_scripts"],
            metadata=result["metadata"],
            created_at=datetime.fromisoformat(result["metadata"]["created_at"])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating content: {str(e)}"
        )

@router.post("/generate-voice", response_model=List[TTSOutputResponse])
async def generate_voice_content(
    request: VoiceGenerationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate voice content using Agent B"""
    try:
        # Get original content
        content = DatabaseManager.get_content_by_id(db, request.content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Initialize Agent B
        ai_writer = AIWriterVoiceGen()
        
        # Generate voice script and TTS
        result = ai_writer.generate_content_for_platforms(
            content_text=content.original_text,
            content_id=request.content_id,
            platforms=["voice_script"],
            tone=request.tone.value,
            language=request.language
        )
        
        # Convert TTS outputs to response format
        tts_responses = []
        for tts_output in result["tts_outputs"]:
            tts_responses.append(TTSOutputResponse(
                content_id=tts_output["content_id"],
                language=tts_output["language"],
                voice_tag=tts_output["voice_tag"],
                tone=tts_output["tone"],
                audio_path=tts_output["audio_path"],
                duration=tts_output["duration"],
                created_at=datetime.fromisoformat(tts_output["created_at"])
            ))
        
        return tts_responses
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating voice content: {str(e)}"
        )

@router.get("/content-versions/{content_id}")
async def get_content_versions(
    content_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all versions of generated content"""
    try:
        ai_writer = AIWriterVoiceGen()
        versions = ai_writer.get_content_versions(content_id)
        
        return {
            "content_id": content_id,
            "versions": versions,
            "total_versions": len(versions)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving content versions: {str(e)}"
        )

@router.get("/download-audio/{content_id}/{language}")
async def download_audio_file(
    content_id: str,
    language: str,
    current_user: dict = Depends(get_current_user)
):
    """Download generated audio file"""
    try:
        ai_writer = AIWriterVoiceGen()
        versions = ai_writer.get_content_versions(content_id)
        
        if not versions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No versions found for this content"
            )
        
        # Get latest version
        latest_version = versions[-1]
        
        # Find audio file for the specified language
        audio_path = None
        for tts_output in latest_version.get("tts_outputs", []):
            if tts_output["language"] == language:
                audio_path = tts_output["audio_path"]
                break
        
        if not audio_path or audio_path.startswith("simulated://"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audio file not found or is simulated"
            )
        
        if not os.path.exists(audio_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audio file does not exist on disk"
            )
        
        return FileResponse(
            path=audio_path,
            media_type="audio/mpeg",
            filename=f"{content_id}_{language}.mp3"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading audio file: {str(e)}"
        )

@router.get("/platforms")
async def get_supported_platforms():
    """Get list of supported platforms"""
    from core.config import PLATFORM_CONFIGS
    
    return {
        "platforms": list(PLATFORM_CONFIGS.keys()),
        "platform_configs": PLATFORM_CONFIGS
    }

@router.get("/tones")
async def get_supported_tones():
    """Get list of supported tones"""
    from core.config import TONE_CONFIGS
    
    return {
        "tones": list(TONE_CONFIGS.keys()),
        "tone_configs": TONE_CONFIGS
    }

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    from core.config import LANGUAGE_CONFIGS
    
    return {
        "languages": list(LANGUAGE_CONFIGS.keys()),
        "language_configs": LANGUAGE_CONFIGS
    }

@router.post("/batch-generate")
async def batch_generate_content(
    content_ids: List[str],
    platforms: Optional[List[Platform]] = None,
    tone: Optional[Tone] = Tone.NEUTRAL,
    language: Optional[str] = "en",
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Batch generate content for multiple content items"""
    try:
        ai_writer = AIWriterVoiceGen()
        results = []
        errors = []
        
        platforms_list = [p.value for p in platforms] if platforms else None
        
        for content_id in content_ids:
            try:
                # Get original content
                content = DatabaseManager.get_content_by_id(db, content_id)
                if not content:
                    errors.append(f"Content {content_id} not found")
                    continue
                
                # Generate content
                result = ai_writer.generate_content_for_platforms(
                    content_text=content.original_text,
                    content_id=content_id,
                    platforms=platforms_list,
                    tone=tone.value,
                    language=language
                )
                
                results.append({
                    "content_id": content_id,
                    "status": "success",
                    "generated_content": result["generated_content"],
                    "voice_scripts": result["voice_scripts"],
                    "tts_outputs": result["tts_outputs"]
                })
                
            except Exception as e:
                errors.append(f"Error processing {content_id}: {str(e)}")
        
        return {
            "total_processed": len(content_ids),
            "successful": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in batch generation: {str(e)}"
        )

@router.delete("/clear-cache")
async def clear_content_cache(
    current_user: dict = Depends(get_current_user)
):
    """Clear generated content cache"""
    try:
        ai_writer = AIWriterVoiceGen()
        cache_dir = ai_writer.output_dir

        if os.path.exists(cache_dir):
            import shutil
            shutil.rmtree(cache_dir)
            os.makedirs(cache_dir, exist_ok=True)

        return StatusResponse(
            status="success",
            message="Content cache cleared successfully",
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing cache: {str(e)}"
        )

@router.get("/ai-status")
async def get_ai_status(
    current_user: dict = Depends(get_current_user)
):
    """Get AI model status and usage statistics"""
    try:
        ai_manager = get_ai_manager()
        usage_stats = ai_manager.get_usage_stats()

        return {
            "ai_models": {
                "primary_provider": usage_stats["primary_provider"],
                "fallback_provider": usage_stats["fallback_provider"],
                "groq_model": ai_manager.model_configs["groq"]["primary"],
                "groq_fallback": ai_manager.model_configs["groq"]["fallback"],
                "gemini_model": ai_manager.model_configs["gemini"]["model"]
            },
            "usage_statistics": usage_stats["rate_limits"],
            "rate_limits": usage_stats["limits"],
            "status": "operational",
            "free_tier_optimized": True,
            "last_updated": usage_stats["current_time"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving AI status: {str(e)}"
        )

@router.post("/test-ai-models")
async def test_ai_models(
    current_user: dict = Depends(get_current_user)
):
    """Test both AI models with a simple prompt"""
    try:
        ai_manager = get_ai_manager()

        test_prompt = "Generate a short inspirational message about perseverance."

        # Test both providers
        results = {}

        try:
            # Test primary provider
            text1, provider1 = ai_manager.generate_content(
                prompt=test_prompt,
                max_tokens=100,
                task_type="general"
            )
            results["primary_test"] = {
                "provider": provider1,
                "response": text1[:100] + "..." if len(text1) > 100 else text1,
                "status": "success"
            }
        except Exception as e:
            results["primary_test"] = {
                "provider": settings.primary_ai_provider,
                "error": str(e),
                "status": "failed"
            }

        # Test fallback provider
        try:
            # Force fallback by temporarily marking primary as rate limited
            original_primary = ai_manager.rate_limits[settings.primary_ai_provider]["requests"]
            ai_manager.rate_limits[settings.primary_ai_provider]["requests"] = 999

            text2, provider2 = ai_manager.generate_content(
                prompt=test_prompt,
                max_tokens=100,
                task_type="general"
            )

            # Restore original count
            ai_manager.rate_limits[settings.primary_ai_provider]["requests"] = original_primary

            results["fallback_test"] = {
                "provider": provider2,
                "response": text2[:100] + "..." if len(text2) > 100 else text2,
                "status": "success"
            }
        except Exception as e:
            results["fallback_test"] = {
                "provider": settings.fallback_ai_provider,
                "error": str(e),
                "status": "failed"
            }

        return {
            "test_results": results,
            "timestamp": datetime.utcnow().isoformat(),
            "test_prompt": test_prompt
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error testing AI models: {str(e)}"
        )

# Task 5 Endpoints - Multilingual Personalisation with LLM + TTS Integration

@router.post("/translate-content")
async def translate_content_endpoint(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Task 5 Component 1: Translation Agent endpoint"""
    try:
        translation_agent = get_translation_agent()

        content_text = request.get("content_text", "")
        source_language = request.get("source_language", "en")
        target_languages = request.get("target_languages", ["hi", "sa", "es", "fr"])
        content_metadata = request.get("content_metadata", {})

        if not content_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content text is required"
            )

        result = translation_agent.translate_content(
            content_text=content_text,
            source_language=source_language,
            target_languages=target_languages,
            content_metadata=content_metadata
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )

@router.post("/personalize-content")
async def personalize_content_endpoint(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Task 5 Component 2: Personalization Agent endpoint"""
    try:
        personalization_agent = get_personalization_agent()

        content_text = request.get("content_text", "")
        user_profile_id = request.get("user_profile_id", "general")
        target_tone = request.get("target_tone")
        content_metadata = request.get("content_metadata", {})

        if not content_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content text is required"
            )

        result = personalization_agent.personalize_content(
            content_text=content_text,
            user_profile_id=user_profile_id,
            target_tone=target_tone,
            content_metadata=content_metadata
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Personalization failed: {str(e)}"
        )

@router.post("/simulate-tts")
async def simulate_tts_endpoint(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Task 5 Component 4: TTS Simulation Layer endpoint"""
    try:
        tts_simulator = get_tts_simulator()

        content_text = request.get("content_text", "")
        language = request.get("language", "en")
        tone = request.get("tone", "neutral")
        content_id = request.get("content_id")
        voice_tag_override = request.get("voice_tag_override")

        if not content_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content text is required"
            )

        result = tts_simulator.simulate_tts_generation(
            content_text=content_text,
            language=language,
            tone=tone,
            content_id=content_id,
            voice_tag_override=voice_tag_override
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TTS simulation failed: {str(e)}"
        )

@router.post("/weekly-strategy")
async def generate_weekly_strategy(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Task 5 Component 6: Weekly Adaptive Hook endpoint"""
    try:
        weekly_hook = get_weekly_adaptive_hook()

        start_date = request.get("start_date")
        end_date = request.get("end_date")

        result = weekly_hook.analyze_weekly_performance(
            start_date=start_date,
            end_date=end_date
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Weekly strategy analysis failed: {str(e)}"
        )

@router.get("/user-profiles")
async def get_user_profiles(
    current_user: dict = Depends(get_current_user)
):
    """Get available user profiles for personalization"""
    try:
        personalization_agent = get_personalization_agent()
        profiles = personalization_agent.get_user_profiles()
        return profiles

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user profiles: {str(e)}"
        )

@router.get("/available-voices")
async def get_available_voices(
    language: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Get available voice options for TTS simulation"""
    try:
        tts_simulator = get_tts_simulator()
        voices = tts_simulator.get_available_voices(language)
        return voices

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving available voices: {str(e)}"
        )

# Task 4 Endpoints - Multilingual Content Personalisation & Metadata Enrichment

@router.post("/detect-language-preference")
async def detect_language_preference(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Task 4 Component 1: Language Metadata Enhancer endpoint"""
    try:
        language_mapper = get_language_mapper()

        user_profile_id = request.get("user_profile_id", "general")
        content_text = request.get("content_text", "")
        platform = request.get("platform", "twitter")

        result = language_mapper.detect_user_language_preference(
            user_profile_id=user_profile_id,
            content_text=content_text,
            platform=platform
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Language preference detection failed: {str(e)}"
        )

@router.post("/expand-content-metadata")
async def expand_content_metadata(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Task 4 Component 1: Expand content metadata schema"""
    try:
        language_mapper = get_language_mapper()

        original_metadata = request.get("original_metadata", {})
        user_profile_id = request.get("user_profile_id", "general")
        content_text = request.get("content_text", "")
        platform = request.get("platform", "twitter")

        expanded_metadata = language_mapper.expand_content_metadata_schema(
            original_metadata=original_metadata,
            user_profile_id=user_profile_id,
            content_text=content_text,
            platform=platform
        )

        return expanded_metadata

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Metadata expansion failed: {str(e)}"
        )

@router.post("/simulate-translation")
async def simulate_translation_endpoint(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Task 4 Component 3: Simulated translation with dummy content"""
    try:
        simulated_translator = get_simulated_translator()

        content_text = request.get("content_text", "")
        target_language = request.get("target_language", "hi")
        source_language = request.get("source_language", "en")

        if not content_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content text is required"
            )

        result = simulated_translator.simulate_translation(
            content_text=content_text,
            target_language=target_language,
            source_language=source_language
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulated translation failed: {str(e)}"
        )

@router.post("/multilingual-preview")
async def generate_multilingual_preview(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Task 4 Component 3: Generate multilingual preview for multiple languages"""
    try:
        simulated_translator = get_simulated_translator()

        content_text = request.get("content_text", "")
        target_languages = request.get("target_languages", ["hi", "sa", "es"])
        platform = request.get("platform", "twitter")
        source_language = request.get("source_language", "en")

        if not content_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content text is required"
            )

        result = simulated_translator.generate_multilingual_preview(
            content_text=content_text,
            target_languages=target_languages,
            platform=platform,
            source_language=source_language
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multilingual preview generation failed: {str(e)}"
        )

@router.post("/post-output-preview")
async def generate_post_output_preview(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Task 4 Component 4: Post Output Preview JSON"""
    try:
        publisher_sim = get_multilingual_publisher_sim()

        original_post_id = request.get("original_post_id", f"post_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
        content_text = request.get("content_text", "")
        target_languages = request.get("target_languages", ["hi", "sa", "es"])
        platforms = request.get("platforms", ["twitter", "instagram"])
        user_profile_id = request.get("user_profile_id", "general")
        tone = request.get("tone", "neutral")

        if not content_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content text is required"
            )

        result = publisher_sim.generate_multilingual_post_preview(
            original_post_id=original_post_id,
            content_text=content_text,
            target_languages=target_languages,
            platforms=platforms,
            user_profile_id=user_profile_id,
            tone=tone
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Post output preview generation failed: {str(e)}"
        )

@router.get("/language-statistics")
async def get_language_statistics(
    current_user: dict = Depends(get_current_user)
):
    """Get language support statistics"""
    try:
        language_mapper = get_language_mapper()
        stats = language_mapper.get_language_statistics()
        return stats

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving language statistics: {str(e)}"
        )

@router.get("/validate-language/{language}")
async def validate_language_support(
    language: str,
    current_user: dict = Depends(get_current_user)
):
    """Validate if a language is supported"""
    try:
        language_mapper = get_language_mapper()
        validation = language_mapper.validate_language_support(language)
        return validation

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating language support: {str(e)}"
        )

# Task 3 Endpoints - Akshara Pulse: Platform Publisher + Analytics Agent

@router.post("/simulate-platform-publishing")
async def simulate_platform_publishing(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Task 3 Agent J: Simulate posting to 3 platforms (Instagram, Twitter, LinkedIn)"""
    try:
        publisher_sim = get_multilingual_publisher_sim()

        content_id = request.get("content_id", f"content_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
        content_text = request.get("content_text", "")
        platforms = request.get("platforms", ["instagram", "twitter", "linkedin"])
        preview_mode = request.get("preview_mode", True)
        user_profile_id = request.get("user_profile_id", "general")
        tone = request.get("tone", "neutral")

        if not content_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content text is required"
            )

        result = publisher_sim.simulate_platform_publishing(
            content_id=content_id,
            content_text=content_text,
            platforms=platforms,
            preview_mode=preview_mode,
            user_profile_id=user_profile_id,
            tone=tone
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Platform publishing simulation failed: {str(e)}"
        )

@router.post("/generate-engagement-stats")
async def generate_engagement_stats(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Task 3 Agent K: Generate dummy engagement stats for simulated posts"""
    try:
        analytics_collector = get_analytics_collector()

        content_id = request.get("content_id", "")
        platform = request.get("platform", "twitter")
        content_text = request.get("content_text", "")
        language = request.get("language", "en")
        voice_tag = request.get("voice_tag", "neutral")
        tone = request.get("tone", "neutral")

        if not content_id or not content_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content ID and content text are required"
            )

        result = analytics_collector.generate_task3_engagement_stats(
            content_id=content_id,
            platform=platform,
            content_text=content_text,
            language=language,
            voice_tag=voice_tag,
            tone=tone
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Engagement stats generation failed: {str(e)}"
        )

@router.post("/create-feedback-signals")
async def create_feedback_signals(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Task 3 Agent K: Create feedback signals for high/underperforming content"""
    try:
        analytics_collector = get_analytics_collector()

        days_back = request.get("days_back", 7)

        result = analytics_collector.create_feedback_signals(days_back=days_back)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feedback signals creation failed: {str(e)}"
        )

@router.post("/adjust-future-content-strategy")
async def adjust_future_content_strategy(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Task 3 Loop Hook: Adaptive Improvement Trigger - adjust_future_content_strategy()"""
    try:
        strategy_recommender = get_strategy_recommender()

        analysis_days = request.get("analysis_days", 7)

        result = strategy_recommender.adjust_future_content_strategy(analysis_days=analysis_days)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content strategy adjustment failed: {str(e)}"
        )

@router.get("/analytics-db-status")
async def get_analytics_db_status(
    current_user: dict = Depends(get_current_user)
):
    """Get status of analytics database"""
    try:
        analytics_collector = get_analytics_collector()

        analytics_db_file = os.path.join(analytics_collector.analytics_db_path, "post_metrics.json")

        if os.path.exists(analytics_db_file):
            try:
                with open(analytics_db_file, 'r', encoding='utf-8') as f:
                    analytics_db = json.load(f)

                status = {
                    "database_exists": True,
                    "total_posts": len(analytics_db.get("posts", [])),
                    "last_updated": analytics_db.get("metadata", {}).get("last_updated"),
                    "created_at": analytics_db.get("metadata", {}).get("created_at"),
                    "recent_posts": len([
                        post for post in analytics_db.get("posts", [])
                        if datetime.fromisoformat(post["timestamp"]) >= datetime.utcnow() - timedelta(days=7)
                    ])
                }
            except Exception:
                status = {
                    "database_exists": True,
                    "error": "Failed to read analytics database",
                    "total_posts": 0
                }
        else:
            status = {
                "database_exists": False,
                "total_posts": 0,
                "message": "Analytics database will be created when first post is analyzed"
            }

        return status

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking analytics database status: {str(e)}"
        )

# Task 2 Endpoints - Agent H: Sentiment Tuner & Agent I: Context-Aware Platform Targeter

@router.post("/analyze-sentiment")
async def analyze_sentiment(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Task 2 Agent H: Analyze current sentiment of content"""
    try:
        sentiment_tuner = get_sentiment_tuner()

        content_text = request.get("content_text", "")

        if not content_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content text is required"
            )

        result = sentiment_tuner.analyze_current_sentiment(content_text)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sentiment analysis failed: {str(e)}"
        )

@router.post("/adjust-sentiment")
async def adjust_sentiment(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Task 2 Agent H: Adjust content sentiment to target emotional tone"""
    try:
        sentiment_tuner = get_sentiment_tuner()

        content_text = request.get("content_text", "")
        target_sentiment = request.get("target_sentiment", "uplifting")
        intensity = request.get("intensity", "moderate")
        language = request.get("language", "en")
        preserve_meaning = request.get("preserve_meaning", True)

        if not content_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content text is required"
            )

        result = sentiment_tuner.adjust_sentiment(
            content_text=content_text,
            target_sentiment=target_sentiment,
            intensity=intensity,
            language=language,
            preserve_meaning=preserve_meaning
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sentiment adjustment failed: {str(e)}"
        )

@router.get("/available-sentiments")
async def get_available_sentiments(
    current_user: dict = Depends(get_current_user)
):
    """Get list of available sentiment types"""
    try:
        sentiment_tuner = get_sentiment_tuner()
        sentiments = sentiment_tuner.get_available_sentiments()
        return {"available_sentiments": sentiments}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving available sentiments: {str(e)}"
        )

@router.post("/analyze-content-context")
async def analyze_content_context(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Task 2 Agent I: Analyze content context for platform targeting"""
    try:
        platform_targeter = get_platform_targeter()

        content_text = request.get("content_text", "")
        language = request.get("language", "en")

        if not content_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content text is required"
            )

        result = platform_targeter.analyze_content_context(content_text, language)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content context analysis failed: {str(e)}"
        )

@router.post("/target-platform-content")
async def target_platform_content(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Task 2 Agent I: Generate platform-targeted content with context-aware formatting"""
    try:
        platform_targeter = get_platform_targeter()

        content_text = request.get("content_text", "")
        platform = request.get("platform", "instagram")
        context = request.get("context")
        language = request.get("language", "en")
        tone = request.get("tone", "neutral")

        if not content_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content text is required"
            )

        result = platform_targeter.target_platform_content(
            content_text=content_text,
            platform=platform,
            context=context,
            language=language,
            tone=tone
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Platform targeting failed: {str(e)}"
        )

@router.get("/platform-capabilities")
async def get_platform_capabilities(
    current_user: dict = Depends(get_current_user)
):
    """Get platform capabilities and configurations"""
    try:
        platform_targeter = get_platform_targeter()
        capabilities = platform_targeter.get_platform_capabilities()
        return capabilities

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving platform capabilities: {str(e)}"
        )
