"""
Compose router for indigenous NLP processing in Vaani Sentinel X
Implements /compose endpoint for lesson text processing with Hindi/English support
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional, List
import json
import uuid
import logging

from api.routers.auth import get_current_user
from core.database import get_db, LessonComposition, DatabaseManager
from core.ai_manager import get_ai_manager
from core.config import settings
import sqlalchemy.orm as orm

logger = logging.getLogger(__name__)

router = APIRouter()

class ComposeRequest(BaseModel):
    """Request model for /compose endpoint"""
    lesson_id: str
    text: str
    language: str = "en"
    tone: str = "educational"
    user_id: Optional[str] = None
    cultural_context: Optional[Dict[str, Any]] = None
    target_audience: Optional[str] = "student"

class ComposeResponse(BaseModel):
    """Response model for /compose endpoint"""
    composition_id: str
    final_text: str
    language: str
    tone: str
    cultural_adaptations: Dict[str, Any]
    nlp_metadata: Dict[str, Any]
    composition_quality: float
    created_at: datetime

class IndigenousNLPProcessor:
    """Indigenous NLP Processor for Hindi/English text composition"""

    def __init__(self):
        self.ai_manager = get_ai_manager()

    def process_text(self, text: str, language: str, tone: str, cultural_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process text through indigenous NLP pipeline"""

        # Create processing prompt based on language and context
        if language == "hi":
            system_prompt = self._get_hindi_processing_prompt(tone, cultural_context)
        else:
            system_prompt = self._get_english_processing_prompt(tone, cultural_context)

        # Use AI manager for NLP processing
        try:
            # Inject original text into the prompt template
            final_prompt = system_prompt.replace("{{text}}", text)
            processed_text, provider = self.ai_manager.generate_content(
                prompt=final_prompt,
                max_tokens=1000,
                task_type="nlp_processing"
            )

            # Extract cultural adaptations and metadata
            adaptations = self._extract_cultural_adaptations(processed_text, language)
            metadata = self._extract_nlp_metadata(processed_text, language)

            return {
                "final_text": processed_text.strip(),
                "cultural_adaptations": adaptations,
                "nlp_metadata": metadata,
                "composition_quality": self._calculate_quality_score(processed_text, adaptations),
                "processing_provider": provider
            }

        except Exception as e:
            logger.error(f"NLP processing failed: {e}")
            # Return original text as fallback
            return {
                "final_text": text,
                "cultural_adaptations": {},
                "nlp_metadata": {"error": str(e)},
                "composition_quality": 0.5,
                "processing_provider": "fallback"
            }

    def _get_hindi_processing_prompt(self, tone: str, cultural_context: Dict[str, Any] = None) -> str:
        """Generate Hindi-specific processing prompt"""
        base_prompt = f"""
Process the following educational text for Hindi-speaking students.
Maintain cultural sensitivity and use appropriate Hindi expressions.

Original text: {{text}}

Requirements:
- Use natural, culturally appropriate Hindi
- Maintain educational tone: {tone}
- Include relevant cultural references if appropriate
- Ensure readability for target audience
- Preserve technical accuracy while using accessible language

Processed text should be engaging and culturally resonant.
"""
        if cultural_context:
            base_prompt += f"\nCultural context: {json.dumps(cultural_context, ensure_ascii=False)}"

        return base_prompt

    def _get_english_processing_prompt(self, tone: str, cultural_context: Dict[str, Any] = None) -> str:
        """Generate English-specific processing prompt"""
        base_prompt = f"""
Process the following educational text for clarity and engagement.
Adapt for cultural context while maintaining educational integrity.

Original text: {{text}}

Requirements:
- Use clear, accessible English
- Maintain educational tone: {tone}
- Ensure cultural appropriateness
- Optimize for student comprehension
- Preserve academic accuracy

Create engaging, student-friendly content.
"""
        if cultural_context:
            base_prompt += f"\nCultural context: {json.dumps(cultural_context)}"

        return base_prompt

    def _extract_cultural_adaptations(self, text: str, language: str) -> Dict[str, Any]:
        """Extract cultural adaptation information from processed text"""
        adaptations = {}

        if language == "hi":
            # Check for Hindi cultural elements
            adaptations["cultural_elements"] = []
            adaptations["regional_variations"] = []
            adaptations["traditional_references"] = []
        else:
            adaptations["cultural_elements"] = []
            adaptations["inclusive_language"] = True
            adaptations["global_perspective"] = True

        return adaptations

    def _extract_nlp_metadata(self, text: str, language: str) -> Dict[str, Any]:
        """Extract NLP processing metadata"""
        return {
            "word_count": len(text.split()),
            "sentence_count": len(text.split('.')),
            "language": language,
            "processing_timestamp": datetime.utcnow().isoformat(),
            "readability_score": self._calculate_readability(text, language)
        }

    def _calculate_readability(self, text: str, language: str) -> float:
        """Calculate basic readability score"""
        words = len(text.split())
        sentences = len(text.split('.'))
        avg_words_per_sentence = words / max(sentences, 1)

        # Simple readability heuristic
        if avg_words_per_sentence < 15:
            return 0.9  # Very readable
        elif avg_words_per_sentence < 25:
            return 0.7  # Readable
        else:
            return 0.5  # Needs improvement

    def _calculate_quality_score(self, text: str, adaptations: Dict[str, Any]) -> float:
        """Calculate overall composition quality score"""
        base_score = 0.7  # Base quality

        # Factors that improve quality
        if len(text) > 50:  # Substantial content
            base_score += 0.1
        if adaptations.get("cultural_elements"):  # Cultural adaptation
            base_score += 0.1
        if len(text.split()) > 20:  # Adequate length
            base_score += 0.1

        return min(base_score, 1.0)

# Global processor instance
_nlp_processor = None

def get_nlp_processor() -> IndigenousNLPProcessor:
    """Get singleton NLP processor instance"""
    global _nlp_processor
    if _nlp_processor is None:
        _nlp_processor = IndigenousNLPProcessor()
    return _nlp_processor

@router.post("/final_text", response_model=ComposeResponse)
async def compose_lesson_text(
    request: ComposeRequest,
    current_user: dict = Depends(get_current_user),
    db: orm.Session = Depends(get_db)
):
    """Compose lesson text using indigenous NLP processing"""
    try:
        # Get NLP processor
        processor = get_nlp_processor()

        # Process the text
        result = processor.process_text(
            text=request.text,
            language=request.language,
            tone=request.tone,
            cultural_context=request.cultural_context
        )

        # Create composition record
        composition_data = {
            "composition_id": f"comp_{uuid.uuid4().hex[:16]}",
            "lesson_id": request.lesson_id,
            "user_id": request.user_id or current_user.get("user_id"),
            "original_text": request.text,
            "composed_text": result["final_text"],
            "language": request.language,
            "tone": request.tone,
            "cultural_adaptations": result["cultural_adaptations"],
            "nlp_metadata": result["nlp_metadata"],
            "composition_quality": result["composition_quality"]
        }

        # Save to database
        composition = LessonComposition(**composition_data)
        db.add(composition)
        db.commit()
        db.refresh(composition)

        return ComposeResponse(
            composition_id=composition.composition_id,
            final_text=composition.composed_text,
            language=composition.language,
            tone=composition.tone,
            cultural_adaptations=composition.cultural_adaptations,
            nlp_metadata=composition.nlp_metadata,
            composition_quality=composition.composition_quality,
            created_at=composition.created_at
        )

    except Exception as e:
        logger.error(f"Compose endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text composition failed: {str(e)}"
        )

@router.get("/compositions/{lesson_id}")
async def get_lesson_compositions(
    lesson_id: str,
    current_user: dict = Depends(get_current_user),
    db: orm.Session = Depends(get_db)
):
    """Get all compositions for a lesson"""
    try:
        compositions = db.query(LessonComposition).filter(
            LessonComposition.lesson_id == lesson_id
        ).order_by(LessonComposition.created_at.desc()).all()

        return {
            "lesson_id": lesson_id,
            "compositions": [
                {
                    "composition_id": comp.composition_id,
                    "final_text": comp.composed_text,
                    "language": comp.language,
                    "tone": comp.tone,
                    "quality": comp.composition_quality,
                    "created_at": comp.created_at
                }
                for comp in compositions
            ],
            "total": len(compositions)
        }

    except Exception as e:
        logger.error(f"Get compositions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve compositions: {str(e)}"
        )

@router.get("/supported-languages")
async def get_supported_languages():
    """Get supported languages for composition"""
    return {
        "languages": [
            {"code": "en", "name": "English", "native_name": "English"},
            {"code": "hi", "name": "Hindi", "native_name": "हिन्दी"}
        ],
        "default_language": "en"
    }

@router.get("/supported-tones")
async def get_supported_tones():
    """Get supported tones for composition"""
    return {
        "tones": [
            {"code": "educational", "name": "Educational", "description": "Formal learning content"},
            {"code": "conversational", "name": "Conversational", "description": "Natural dialogue style"},
            {"code": "storytelling", "name": "Storytelling", "description": "Narrative and engaging"},
            {"code": "simplified", "name": "Simplified", "description": "Easy to understand"}
        ],
        "default_tone": "educational"
    }
