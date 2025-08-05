"""
Multilingual router for Vaani Sentinel X
Handles multilingual content processing and translation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

from core.database import get_db, DatabaseManager
from api.models import (
    TranslationRequest, MultilingualContentResponse, 
    StatusResponse, TranslatedContentResponse
)
from api.routers.auth import get_current_user
from agents.multilingual_pipeline import MultilingualContentPipeline

router = APIRouter()

# Request Models
class LanguageDetectionRequest(BaseModel):
    content: str

class MultilingualProcessingRequest(BaseModel):
    content_id: str
    target_languages: Optional[List[str]] = None
    auto_detect: bool = True

class BatchTranslationRequest(BaseModel):
    content_ids: List[str]
    target_languages: List[str]

# Response Models
class LanguageDetectionResponse(BaseModel):
    detected_language: str
    confidence: float
    routing_info: Dict[str, Any]

class MultilingualProcessingResponse(BaseModel):
    content_id: str
    source_language: str
    source_confidence: float
    target_languages: List[str]
    processed_languages: Dict[str, Any]
    metadata: Dict[str, Any]

@router.post("/detect-language", response_model=LanguageDetectionResponse)
async def detect_content_language(
    request: LanguageDetectionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Detect language of content"""
    try:
        pipeline = MultilingualContentPipeline()
        
        # Detect language
        detected_lang, confidence = pipeline.language_detector.detect_language(request.content)
        
        # Get routing information
        routing_info = pipeline.language_detector.route_content_by_language(
            request.content, detected_lang
        )
        
        return LanguageDetectionResponse(
            detected_language=detected_lang,
            confidence=confidence,
            routing_info=routing_info
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error detecting language: {str(e)}"
        )

@router.post("/process-multilingual", response_model=MultilingualProcessingResponse)
async def process_multilingual_content(
    request: MultilingualProcessingRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process content for multiple languages"""
    try:
        # Get original content
        content = DatabaseManager.get_content_by_id(db, request.content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Initialize multilingual pipeline
        pipeline = MultilingualContentPipeline()
        
        # Process content
        result = pipeline.process_multilingual_content(
            content=content.original_text,
            content_id=request.content_id,
            target_languages=request.target_languages,
            auto_detect=request.auto_detect
        )
        
        # Save translated content to database
        for lang, lang_data in result["processed_languages"].items():
            if lang_data.get("status") == "processed":
                translation_data = {
                    "content_id": f"{request.content_id}_{lang}",
                    "original_content_id": request.content_id,
                    "language": lang,
                    "translated_text": lang_data["content"],
                    "confidence_score": result["source_confidence"],
                    "tone": "neutral",  # Default tone
                    "platform": "general"
                }
                
                # Create translated content entry
                from core.database import TranslatedContent
                translated_content = TranslatedContent(**translation_data)
                db.add(translated_content)
        
        db.commit()
        
        return MultilingualProcessingResponse(
            content_id=result["content_id"],
            source_language=result["source_language"],
            source_confidence=result["source_confidence"],
            target_languages=result["target_languages"],
            processed_languages=result["processed_languages"],
            metadata=result["metadata"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing multilingual content: {str(e)}"
        )

@router.post("/translate", response_model=List[TranslatedContentResponse])
async def translate_content(
    request: TranslationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Translate content to target languages"""
    try:
        # Get original content
        content = DatabaseManager.get_content_by_id(db, request.content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Initialize multilingual pipeline
        pipeline = MultilingualContentPipeline()
        
        # Process for target languages
        result = pipeline.process_multilingual_content(
            content=content.original_text,
            content_id=request.content_id,
            target_languages=request.target_languages,
            auto_detect=True
        )
        
        # Create response
        translations = []
        for lang in request.target_languages:
            lang_data = result["processed_languages"].get(lang, {})
            if lang_data.get("status") == "processed":
                translations.append(TranslatedContentResponse(
                    content_id=f"{request.content_id}_{lang}",
                    original_content_id=request.content_id,
                    language=lang,
                    translated_text=lang_data["content"],
                    confidence_score=result["source_confidence"],
                    tone=request.tone.value if request.tone else "neutral",
                    platform="general",
                    created_at=datetime.utcnow()
                ))
        
        return translations
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error translating content: {str(e)}"
        )

@router.post("/batch-translate", response_model=StatusResponse)
async def batch_translate_content(
    request: BatchTranslationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Batch translate multiple content items"""
    try:
        pipeline = MultilingualContentPipeline()
        results = []
        errors = []
        
        for content_id in request.content_ids:
            try:
                # Get content
                content = DatabaseManager.get_content_by_id(db, content_id)
                if not content:
                    errors.append(f"Content {content_id} not found")
                    continue
                
                # Process multilingual content
                result = pipeline.process_multilingual_content(
                    content=content.original_text,
                    content_id=content_id,
                    target_languages=request.target_languages,
                    auto_detect=True
                )
                
                results.append({
                    "content_id": content_id,
                    "status": "success",
                    "processed_languages": list(result["processed_languages"].keys())
                })
                
            except Exception as e:
                errors.append(f"Error processing {content_id}: {str(e)}")
        
        return StatusResponse(
            status="completed",
            message=f"Batch translation completed: {len(results)} successful, {len(errors)} failed",
            timestamp=datetime.utcnow(),
            data={
                "successful": len(results),
                "failed": len(errors),
                "results": results,
                "errors": errors
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in batch translation: {str(e)}"
        )

@router.get("/supported-languages")
async def get_supported_languages(
    current_user: dict = Depends(get_current_user)
):
    """Get list of supported languages"""
    try:
        pipeline = MultilingualContentPipeline()
        return pipeline.get_supported_languages()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving supported languages: {str(e)}"
        )

@router.get("/language-statistics")
async def get_language_statistics(
    current_user: dict = Depends(get_current_user)
):
    """Get language processing statistics"""
    try:
        pipeline = MultilingualContentPipeline()
        return pipeline.get_language_statistics()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving language statistics: {str(e)}"
        )

@router.get("/translations/{content_id}")
async def get_content_translations(
    content_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all translations for a content item"""
    try:
        from core.database import TranslatedContent
        
        translations = db.query(TranslatedContent).filter(
            TranslatedContent.original_content_id == content_id
        ).all()
        
        return [
            {
                "content_id": t.content_id,
                "language": t.language,
                "translated_text": t.translated_text,
                "confidence_score": t.confidence_score,
                "tone": t.tone,
                "platform": t.platform,
                "created_at": t.created_at.isoformat()
            }
            for t in translations
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving translations: {str(e)}"
        )

@router.delete("/translations/{content_id}")
async def delete_content_translations(
    content_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete all translations for a content item"""
    try:
        from core.database import TranslatedContent
        
        deleted_count = db.query(TranslatedContent).filter(
            TranslatedContent.original_content_id == content_id
        ).delete()
        
        db.commit()
        
        return StatusResponse(
            status="success",
            message=f"Deleted {deleted_count} translations for content {content_id}",
            timestamp=datetime.utcnow(),
            data={"deleted_count": deleted_count}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting translations: {str(e)}"
        )
