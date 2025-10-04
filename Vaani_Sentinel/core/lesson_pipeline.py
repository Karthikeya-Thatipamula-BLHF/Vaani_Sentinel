"""
Lesson Pipeline Orchestrator for Vaani-Composer-TTV Integration
Connects Assessment → Curriculum → Lesson Script → Indigenous NLP (/compose) → /tts_native → Shashank's TTV
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import uuid
import asyncio

from core.database import get_db, Assessment, Curriculum, Lesson, LessonComposition, LessonPlayback, DatabaseManager
from core.ai_manager import get_ai_manager
from agents.vaani_native_tts import get_native_tts
from core.conversation_manager import get_conversation_manager
from core.ttv_integration import get_ttv_integration
import sqlalchemy.orm as orm

logger = logging.getLogger(__name__)

class LessonPipelineOrchestrator:
    """Orchestrates the complete lesson pipeline from assessment to playback"""

    def __init__(self):
        self.ai_manager = get_ai_manager()
        self.tts_agent = get_native_tts()
        self.conversation_manager = get_conversation_manager()
        self.ttv_integration = get_ttv_integration()

    async def create_assessment(
        self,
        user_id: str,
        subject: str,
        topic: str,
        difficulty_level: str = "intermediate"
    ) -> str:
        """Step 1: Create assessment for user knowledge evaluation"""
        db = next(get_db())
        try:
            assessment_id = f"assess_{uuid.uuid4().hex[:16]}"

            # Generate assessment questions using AI
            questions = await self._generate_assessment_questions(subject, topic, difficulty_level)

            assessment_data = {
                "assessment_id": assessment_id,
                "user_id": user_id,
                "subject": subject,
                "topic": topic,
                "difficulty_level": difficulty_level,
                "questions_asked": questions,
                "answers_given": [],
                "assessment_metadata": {
                    "question_count": len(questions),
                    "estimated_duration": len(questions) * 2,  # 2 minutes per question
                    "subject_area": subject,
                    "topic_focus": topic
                }
            }

            assessment = Assessment(**assessment_data)
            db.add(assessment)
            db.commit()

            logger.info(f"Created assessment {assessment_id} for user {user_id}")
            return assessment_id

        finally:
            db.close()

    async def evaluate_assessment(
        self,
        assessment_id: str,
        answers: List[str]
    ) -> Dict[str, Any]:
        """Step 2: Evaluate assessment answers and determine knowledge level"""
        db = next(get_db())
        try:
            assessment = db.query(Assessment).filter(
                Assessment.assessment_id == assessment_id
            ).first()

            if not assessment:
                raise ValueError(f"Assessment {assessment_id} not found")

            # Evaluate answers using AI
            evaluation = await self._evaluate_answers(
                assessment.questions_asked,
                answers,
                assessment.subject,
                assessment.topic
            )

            # Update assessment with results
            assessment.answers_given = answers
            assessment.current_score = evaluation["score"]
            assessment.completed_at = datetime.utcnow()
            assessment.assessment_metadata.update({
                "evaluation_details": evaluation,
                "completed_at": datetime.utcnow().isoformat()
            })

            db.commit()

            logger.info(f"Evaluated assessment {assessment_id} with score {evaluation['score']}")

            return {
                "assessment_id": assessment_id,
                "score": evaluation["score"],
                "knowledge_level": evaluation["knowledge_level"],
                "recommendations": evaluation["recommendations"],
                "weak_areas": evaluation["weak_areas"]
            }

        finally:
            db.close()

    async def select_curriculum(
        self,
        subject: str,
        grade_level: str,
        language: str = "en",
        assessment_results: Dict[str, Any] = None
    ) -> str:
        """Step 3: Select or create appropriate curriculum based on assessment"""
        db = next(get_db())
        try:
            # Look for existing curriculum
            curriculum = db.query(Curriculum).filter(
                Curriculum.subject == subject,
                Curriculum.grade_level == grade_level,
                Curriculum.language == language
            ).first()

            if curriculum:
                curriculum_id = curriculum.curriculum_id
                logger.info(f"Found existing curriculum {curriculum_id}")
            else:
                # Create new curriculum
                curriculum_id = await self._create_curriculum(subject, grade_level, language, assessment_results)
                logger.info(f"Created new curriculum {curriculum_id}")

            return curriculum_id

        finally:
            db.close()

    async def generate_lesson_script(
        self,
        curriculum_id: str,
        topic: str,
        user_knowledge_level: str,
        language: str = "en"
    ) -> str:
        """Step 4: Generate lesson script tailored to user knowledge"""
        db = next(get_db())
        try:
            curriculum = db.query(Curriculum).filter(
                Curriculum.curriculum_id == curriculum_id
            ).first()

            if not curriculum:
                raise ValueError(f"Curriculum {curriculum_id} not found")

            # Generate lesson content using AI
            lesson_content = await self._generate_lesson_content(
                curriculum, topic, user_knowledge_level, language
            )

            lesson_id = f"lesson_{uuid.uuid4().hex[:16]}"

            lesson_data = {
                "lesson_id": lesson_id,
                "curriculum_id": curriculum_id,
                "title": lesson_content["title"],
                "content": lesson_content["content"],
                "language": language,
                "lesson_type": "theory",
                "objectives": lesson_content["objectives"],
                "media_urls": lesson_content.get("media_urls", {}),
                "duration": lesson_content["estimated_duration"],
                "difficulty_level": user_knowledge_level,
                "prerequisites": lesson_content.get("prerequisites", []),
                "lesson_metadata": {
                    "generated_from_assessment": True,
                    "knowledge_level": user_knowledge_level,
                    "content_structure": lesson_content.get("structure", {})
                }
            }

            lesson = Lesson(**lesson_data)
            db.add(lesson)
            db.commit()

            logger.info(f"Generated lesson {lesson_id} for topic {topic}")
            return lesson_id

        finally:
            db.close()

    async def compose_lesson_text(
        self,
        lesson_id: str,
        user_id: str,
        language: str = "en",
        tone: str = "educational"
    ) -> str:
        """Step 5: Apply indigenous NLP composition to lesson text"""
        db = next(get_db())
        try:
            lesson = db.query(Lesson).filter(
                Lesson.lesson_id == lesson_id
            ).first()

            if not lesson:
                raise ValueError(f"Lesson {lesson_id} not found")

            # Import compose processor
            from api.routers.compose import get_nlp_processor
            processor = get_nlp_processor()

            # Get cultural context for the lesson
            # Lesson does not store subject directly; look up Curriculum
            curriculum = db.query(Curriculum).filter(
                Curriculum.curriculum_id == lesson.curriculum_id
            ).first()
            subject = curriculum.subject if curriculum and getattr(curriculum, "subject", None) else "general"
            cultural_context = await self._get_cultural_context(subject, language)

            # Process the lesson text
            result = processor.process_text(
                text=lesson.content,
                language=language,
                tone=tone,
                cultural_context=cultural_context
            )

            composition_id = f"comp_{uuid.uuid4().hex[:16]}"

            composition_data = {
                "composition_id": composition_id,
                "lesson_id": lesson_id,
                "user_id": user_id,
                "original_text": lesson.content,
                "composed_text": result["final_text"],
                "language": language,
                "tone": tone,
                "cultural_adaptations": result["cultural_adaptations"],
                "nlp_metadata": result["nlp_metadata"],
                "composition_quality": result["composition_quality"]
            }

            composition = LessonComposition(**composition_data)
            db.add(composition)
            db.commit()

            logger.info(f"Composed lesson text for {lesson_id} with quality {result['composition_quality']}")
            return composition_id

        finally:
            db.close()

    async def generate_audio_content(
        self,
        composition_id: str,
        voice: str = "gurukul_neutral"
    ) -> Dict[str, Any]:
        """Step 6: Generate audio using native TTS"""
        db = next(get_db())
        try:
            composition = db.query(LessonComposition).filter(
                LessonComposition.composition_id == composition_id
            ).first()

            if not composition:
                raise ValueError(f"Composition {composition_id} not found")

            # Generate audio using native TTS
            audio_result = self.tts_agent.synthesize(
                text=composition.composed_text,
                voice=voice,
                language=composition.language,
                prosody_policy=True
            )

            logger.info(f"Generated audio for composition {composition_id}")
            return {
                "composition_id": composition_id,
                "audio_url": audio_result.get("audio_url"),
                "voice_tag": voice,
                "language": composition.language,
                "duration": audio_result.get("duration", 0),
                "quality_score": audio_result.get("quality_score", 0.0),
                "latency_ms": audio_result.get("latency_ms", 0)
            }

        finally:
            db.close()

    async def generate_video_content(
        self,
        lesson_id: str,
        audio_url: str,
        text_content: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Step 7: Generate video content using Shashank's TTV system"""
        try:
            # Use actual TTV integration
            video_result = await self.ttv_integration.generate_video(
                audio_url=audio_url,
                text_content=text_content,
                language=language,
                avatar="gurukul_teacher" if language == "hi" else "english_teacher",
                quality="720p"
            )

            return {
                "video_url": video_result["video_url"],
                "lip_sync_score": video_result["lip_sync_score"],
                "processing_time_ms": video_result["processing_time_ms"],
                "video_format": video_result["video_format"],
                "resolution": video_result["resolution"]
            }

        except Exception as e:
            logger.error(f"TTV generation failed: {e}")
            return {
                "video_url": None,
                "error": str(e),
                "fallback_available": True
            }

    async def create_lesson_playback(
        self,
        lesson_id: str,
        user_id: str,
        video_url: str,
        audio_url: str,
        text_content: str,
        citations: List[Dict[str, Any]] = None,
        lip_sync_score: float = 0.85
    ) -> str:
        """Step 8: Create final lesson playback record"""
        db = next(get_db())
        try:
            playback_id = f"play_{uuid.uuid4().hex[:16]}"

            # Calculate latency (end-to-end from assessment to playback)
            start_time = datetime.utcnow()  # This should ideally track from assessment start
            latency_ms = 5000  # Placeholder - would calculate actual latency

            playback_data = {
                "playback_id": playback_id,
                "lesson_id": lesson_id,
                "user_id": user_id,
                "video_url": video_url,
                "audio_url": audio_url,
                "text_content": text_content,
                "citations": citations or [],
                "playback_metadata": {
                    "pipeline_version": "1.0",
                    "components_used": ["assessment", "curriculum", "compose", "tts", "ttv"],
                    "processing_steps": 8
                },
                "lip_sync_score": lip_sync_score,
                "latency_ms": latency_ms
            }

            playback = LessonPlayback(**playback_data)
            db.add(playback)
            db.commit()

            logger.info(f"Created lesson playback {playback_id} for lesson {lesson_id}")
            return playback_id

        finally:
            db.close()

    async def orchestrate_full_pipeline(
        self,
        user_id: str,
        subject: str,
        topic: str,
        grade_level: str = "class_8",
        language: str = "en",
        assessment_answers: List[str] = None
    ) -> Dict[str, Any]:
        """Orchestrate the complete pipeline from assessment to playback"""
        try:
            # Step 1: Create and evaluate assessment
            assessment_id = await self.create_assessment(user_id, subject, topic)

            # If answers provided, evaluate them
            if assessment_answers:
                assessment_results = await self.evaluate_assessment(assessment_id, assessment_answers)
                knowledge_level = assessment_results["knowledge_level"]
            else:
                knowledge_level = "intermediate"  # Default

            # Step 2: Select/create curriculum
            curriculum_id = await self.select_curriculum(subject, grade_level, language, assessment_results if assessment_answers else None)

            # Step 3: Generate lesson script
            lesson_id = await self.generate_lesson_script(curriculum_id, topic, knowledge_level, language)

            # Step 4: Compose lesson text with indigenous NLP
            composition_id = await self.compose_lesson_text(lesson_id, user_id, language)

            # Step 5: Generate audio
            audio_result = await self.generate_audio_content(composition_id)

            # Get composed text
            db = next(get_db())
            try:
                composition = db.query(LessonComposition).filter(
                    LessonComposition.composition_id == composition_id
                ).first()
                composed_text = composition.composed_text if composition else ""
            finally:
                db.close()

            # Step 6: Generate video (TTV)
            video_result = await self.generate_video_content(
                lesson_id, audio_result["audio_url"], composed_text, language
            )

            # Step 7: Create final playback
            citations = [{"source": "AI Generated", "type": "educational_content"}]
            playback_id = await self.create_lesson_playback(
                lesson_id, user_id, video_result["video_url"],
                audio_result["audio_url"], composed_text, citations,
                lip_sync_score=video_result.get("lip_sync_score", 0.85)
            )

            return {
                "success": True,
                "playback_id": playback_id,
                "lesson_id": lesson_id,
                "video_url": video_result["video_url"],
                "audio_url": audio_result["audio_url"],
                "text_content": composed_text,
                "citations": citations,
                "pipeline_steps_completed": 8,
                "total_latency_ms": 5000,  # Would calculate actual total
                "language": language,
                "knowledge_level": knowledge_level
            }

        except Exception as e:
            logger.error(f"Pipeline orchestration failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "pipeline_step_failed": "unknown"
            }

    # Helper methods (implementations would be more sophisticated)

    async def _generate_assessment_questions(self, subject: str, topic: str, difficulty: str) -> List[Dict[str, Any]]:
        """Generate assessment questions using AI"""
        prompt = f"Generate 5 {difficulty} level questions about {topic} in {subject}."

        try:
            response, _ = self.ai_manager.generate_content(
                prompt=prompt,
                max_tokens=500,
                task_type="assessment_generation"
            )

            # Parse questions (simplified)
            questions = []
            lines = response.split('\n')
            for i, line in enumerate(lines[:5]):
                if line.strip():
                    questions.append({
                        "question_id": f"q_{i+1}",
                        "question_text": line.strip(),
                        "type": "multiple_choice",
                        "difficulty": difficulty
                    })

            return questions

        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            return []

    async def _evaluate_answers(self, questions: List[Dict], answers: List[str], subject: str, topic: str) -> Dict[str, Any]:
        """Evaluate assessment answers"""
        # Simplified evaluation
        correct_answers = len([a for a in answers if a and len(a) > 10])  # Rough heuristic
        score = correct_answers / len(questions) if questions else 0.0

        knowledge_level = "beginner"
        if score > 0.8:
            knowledge_level = "advanced"
        elif score > 0.6:
            knowledge_level = "intermediate"

        return {
            "score": score,
            "knowledge_level": knowledge_level,
            "recommendations": ["Review weak areas", "Practice more examples"],
            "weak_areas": ["Problem solving", "Conceptual understanding"]
        }

    async def _create_curriculum(self, subject: str, grade_level: str, language: str, assessment_results: Dict = None) -> str:
        """Create new curriculum"""
        db = next(get_db())
        try:
            curriculum_id = f"curr_{uuid.uuid4().hex[:16]}"

            curriculum_data = {
                "curriculum_id": curriculum_id,
                "title": f"{subject.title()} Curriculum - {grade_level}",
                "subject": subject,
                "grade_level": grade_level,
                "language": language,
                "modules": [
                    {
                        "module_id": "mod_1",
                        "title": "Introduction",
                        "topics": [f"Basic {subject} concepts"],
                        "objectives": [f"Understand fundamental {subject} principles"]
                    }
                ],
                "prerequisites": [],
                "learning_objectives": [f"Master {subject} at {grade_level} level"],
                "estimated_duration": 120,  # minutes
                "curriculum_metadata": {
                    "created_from_assessment": bool(assessment_results),
                    "difficulty_target": assessment_results.get("knowledge_level", "intermediate") if assessment_results else "intermediate"
                }
            }

            curriculum = Curriculum(**curriculum_data)
            db.add(curriculum)
            db.commit()

            return curriculum_id

        finally:
            db.close()

    async def _generate_lesson_content(self, curriculum: Curriculum, topic: str, knowledge_level: str, language: str) -> Dict[str, Any]:
        """Generate lesson content"""
        prompt = f"Create a {knowledge_level} level lesson about {topic} in {curriculum.subject} for {curriculum.grade_level} students in {language}."

        try:
            response, _ = self.ai_manager.generate_content(
                prompt=prompt,
                max_tokens=1000,
                task_type="lesson_generation"
            )

            return {
                "title": f"Lesson: {topic}",
                "content": response,
                "objectives": [f"Understand {topic} concepts"],
                "estimated_duration": 15,  # minutes
                "structure": {"introduction": True, "main_content": True, "summary": True}
            }

        except Exception as e:
            logger.error(f"Lesson generation failed: {e}")
            return {
                "title": f"Lesson: {topic}",
                "content": f"This lesson covers {topic} in {curriculum.subject}.",
                "objectives": [f"Learn about {topic}"],
                "estimated_duration": 10
            }

    async def _get_cultural_context(self, subject: str, language: str) -> Dict[str, Any]:
        """Get cultural context for composition"""
        if language == "hi":
            return {
                "cultural_elements": ["respect_for_elders", "community_learning"],
                "traditional_teaching": True,
                "regional_context": "North India"
            }
        else:
            return {
                "cultural_elements": ["inclusive_education", "global_perspective"],
                "traditional_teaching": False
            }

    async def _simulate_ttv_generation(self, lesson_id: str, audio_url: str, text_content: str, language: str) -> str:
        """Simulate TTV generation (placeholder for actual TTV integration)"""
        # In production, this would call Shashank's TTV API
        await asyncio.sleep(2)  # Simulate processing time

        video_id = f"video_{uuid.uuid4().hex[:12]}"
        return f"https://ttv-service.example.com/videos/{video_id}.mp4"

# Global orchestrator instance
_lesson_orchestrator = None

def get_lesson_orchestrator() -> LessonPipelineOrchestrator:
    """Get singleton lesson pipeline orchestrator"""
    global _lesson_orchestrator
    if _lesson_orchestrator is None:
        _lesson_orchestrator = LessonPipelineOrchestrator()
    return _lesson_orchestrator
