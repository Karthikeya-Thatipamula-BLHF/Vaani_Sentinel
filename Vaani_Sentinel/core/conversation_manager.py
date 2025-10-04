"""
Conversation Manager for Vaani-Converse dialogue system
Handles multi-turn conversations with memory, context switching, and Hindi/English support
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import uuid
import hashlib

from core.database import get_db, Conversation, ConversationTurn, DatabaseManager
from core.ai_manager import get_ai_manager
from agents.vaani_native_tts import get_native_tts
import sqlalchemy.orm as orm

logger = logging.getLogger(__name__)

class ConversationManager:
    """Manages conversational dialogue with memory and context"""

    def __init__(self):
        self.ai_manager = get_ai_manager()
        self.tts_agent = get_native_tts()
        self.max_context_length = 10  # Maximum conversation turns to keep in context
        self.session_timeout = timedelta(hours=2)  # Conversation session timeout

    def start_conversation(
        self,
        user_id: str,
        conversation_type: str = "general_chat",
        language: str = "en",
        initial_context: Dict[str, Any] = None
    ) -> str:
        """Start a new conversation session"""
        db = next(get_db())
        try:
            conversation_id = f"conv_{uuid.uuid4().hex[:16]}"
            session_id = f"session_{uuid.uuid4().hex[:8]}"

            conversation_data = {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "session_id": session_id,
                "conversation_type": conversation_type,
                "language": language,
                "context_memory": initial_context or {},
                "current_topic": "",
                "emotional_state": "neutral",
                "conversation_metadata": {
                    "started_by": "user",
                    "initial_language": language,
                    "conversation_type": conversation_type
                }
            }

            conversation = Conversation(**conversation_data)
            db.add(conversation)
            db.commit()

            logger.info(f"Started conversation {conversation_id} for user {user_id}")
            return conversation_id

        finally:
            db.close()

    def process_turn(
        self,
        conversation_id: str,
        user_input: str,
        input_type: str = "text",
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a single conversation turn"""
        start_time = datetime.utcnow()

        db = next(get_db())
        try:
            # Get conversation
            conversation = db.query(Conversation).filter(
                Conversation.conversation_id == conversation_id
            ).first()

            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")

            # Update conversation activity
            conversation.last_activity = datetime.utcnow()
            conversation.is_active = True

            # Detect language if not provided
            detected_language = language or self._detect_language(user_input)
            if detected_language != conversation.language:
                conversation.language = detected_language

            # Get conversation history
            recent_turns = db.query(ConversationTurn).filter(
                ConversationTurn.conversation_id == conversation_id
            ).order_by(ConversationTurn.turn_number.desc()).limit(self.max_context_length).all()

            conversation_history = []
            for turn in reversed(recent_turns):
                conversation_history.append({
                    "user": turn.user_input,
                    "assistant": turn.system_response
                })

            # Generate response using AI
            response_text, nlp_metadata = self._generate_response(
                user_input=user_input,
                conversation_history=conversation_history,
                language=detected_language,
                context_memory=conversation.context_memory,
                conversation_type=conversation.conversation_type
            )

            # Generate audio response using native TTS
            audio_result = self.tts_agent.synthesize(
                text=response_text,
                voice="gurukul_neutral",
                language=detected_language,
                prosody_policy=True
            )

            # Update context memory
            updated_memory = self._update_context_memory(
                conversation.context_memory,
                user_input,
                response_text,
                nlp_metadata
            )
            conversation.context_memory = updated_memory

            # Determine emotional response
            emotional_response = self._analyze_emotional_response(response_text, nlp_metadata)

            # Create conversation turn record
            turn_number = len(recent_turns) + 1
            turn_data = {
                "conversation_id": conversation_id,
                "turn_number": turn_number,
                "user_input": user_input,
                "user_input_type": input_type,
                "system_response": response_text,
                "response_audio_url": audio_result.get("audio_url"),
                "nlp_processing": nlp_metadata,
                "emotional_response": emotional_response,
                "latency_ms": int((datetime.utcnow() - start_time).total_seconds() * 1000)
            }

            turn = ConversationTurn(**turn_data)
            db.add(turn)

            # Update conversation metadata
            conversation.current_topic = nlp_metadata.get("topic", "")
            conversation.emotional_state = emotional_response

            db.commit()

            logger.info(f"Processed turn {turn_number} for conversation {conversation_id}")

            return {
                "conversation_id": conversation_id,
                "turn_number": turn_number,
                "response": response_text,
                "audio_url": audio_result.get("audio_url"),
                "language": detected_language,
                "emotional_response": emotional_response,
                "latency_ms": turn_data["latency_ms"],
                "context_memory": updated_memory
            }

        finally:
            db.close()

    def _detect_language(self, text: str) -> str:
        """Simple language detection for Hindi/English"""
        # Count Devanagari characters (Hindi)
        hindi_chars = sum(1 for char in text if '\u0900' <= char <= '\u097F')

        # If more than 20% of characters are Hindi, classify as Hindi
        if hindi_chars / len(text.replace(' ', '')) > 0.2:
            return "hi"
        return "en"

    def _generate_response(
        self,
        user_input: str,
        conversation_history: List[Dict[str, str]],
        language: str,
        context_memory: Dict[str, Any],
        conversation_type: str
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate conversational response using AI"""

        # Build conversation context
        context_str = ""
        if conversation_history:
            context_str = "\n".join([
                f"User: {turn['user']}\nAssistant: {turn['assistant']}"
                for turn in conversation_history[-3:]  # Last 3 turns
            ])

        # Create system prompt based on language and type
        if language == "hi":
            system_prompt = self._get_hindi_conversation_prompt(conversation_type, context_memory)
        else:
            system_prompt = self._get_english_conversation_prompt(conversation_type, context_memory)

        # Add conversation history
        if context_str:
            system_prompt += f"\n\nConversation history:\n{context_str}"

        system_prompt += f"\n\nCurrent user input: {user_input}"
        system_prompt += "\n\nYou are a helpful conversational AI assistant. Respond in the user's language and keep responses conversational and engaging."

        try:
            response_text, provider = self.ai_manager.generate_content(
                prompt=system_prompt,
                max_tokens=300,
                task_type="conversation"
            )

            # Extract metadata from response
            nlp_metadata = {
                "provider": provider,
                "topic": self._extract_topic(user_input, response_text),
                "sentiment": self._analyze_sentiment(response_text),
                "language": language,
                "conversation_type": conversation_type
            }

            return response_text.strip(), nlp_metadata

        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            fallback_response = "I'm sorry, I encountered an error. Could you please try again?" if language == "en" else "क्षमा करें, मुझे एक त्रुटि हुई। कृपया पुनः प्रयास करें।"

            return fallback_response, {"error": str(e), "fallback": True}

    def _get_english_conversation_prompt(self, conversation_type: str, context_memory: Dict[str, Any]) -> str:
        """Get English conversation prompt"""
        base_prompt = "You are a helpful AI assistant having a natural conversation."

        if conversation_type == "lesson":
            base_prompt += " You are helping with educational content and learning."
        elif conversation_type == "assessment":
            base_prompt += " You are conducting an assessment or quiz."

        return base_prompt

    def _get_hindi_conversation_prompt(self, conversation_type: str, context_memory: Dict[str, Any]) -> str:
        """Get Hindi conversation prompt"""
        base_prompt = "आप एक सहायक AI असिस्टेंट हैं जो हिंदी में बातचीत कर रहे हैं। अपनी प्रतिक्रियाओं को स्वाभाविक और सहायक रखें।"

        if conversation_type == "lesson":
            base_prompt += " आप शैक्षिक सामग्री और सीखने में मदद कर रहे हैं।"
        elif conversation_type == "assessment":
            base_prompt += " आप मूल्यांकन या प्रश्नोत्तरी कर रहे हैं।"

        return base_prompt

    def _extract_topic(self, user_input: str, response: str) -> str:
        """Extract conversation topic"""
        # Simple topic extraction - in production, use NLP
        keywords = ["math", "science", "history", "lesson", "question", "help", "गणित", "विज्ञान", "इतिहास"]
        for keyword in keywords:
            if keyword.lower() in user_input.lower() or keyword in response.lower():
                return keyword
        return "general"

    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis"""
        positive_words = ["good", "great", "excellent", "wonderful", "helpful", "अच्छा", "बढ़िया", "सहायक"]
        negative_words = ["bad", "terrible", "awful", "sorry", "problem", "खराब", "बुरा", "समस्या"]

        positive_count = sum(1 for word in positive_words if word in text.lower())
        negative_count = sum(1 for word in negative_words if word in text.lower())

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _update_context_memory(
        self,
        current_memory: Dict[str, Any],
        user_input: str,
        response: str,
        nlp_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update conversation context memory"""
        updated_memory = current_memory.copy()

        # Update topic tracking
        current_topic = nlp_metadata.get("topic", "general")
        if "topics_discussed" not in updated_memory:
            updated_memory["topics_discussed"] = []
        if current_topic not in updated_memory["topics_discussed"]:
            updated_memory["topics_discussed"].append(current_topic)

        # Update language preference
        language = nlp_metadata.get("language", "en")
        updated_memory["preferred_language"] = language

        # Track conversation style
        updated_memory["turn_count"] = updated_memory.get("turn_count", 0) + 1

        # Keep memory size manageable
        if len(updated_memory.get("topics_discussed", [])) > 5:
            updated_memory["topics_discussed"] = updated_memory["topics_discussed"][-5:]

        return updated_memory

    def _analyze_emotional_response(self, response_text: str, nlp_metadata: Dict[str, Any]) -> str:
        """Analyze emotional tone of response"""
        sentiment = nlp_metadata.get("sentiment", "neutral")

        # Add more sophisticated emotional analysis based on content
        if any(word in response_text.lower() for word in ["excited", "wonderful", "amazing", "उत्साहित", "अद्भुत"]):
            return "enthusiastic"
        elif any(word in response_text.lower() for word in ["sorry", "apologize", "क्षमा", "माफी"]):
            return "apologetic"
        elif sentiment == "positive":
            return "positive"
        elif sentiment == "negative":
            return "concerned"
        else:
            return "neutral"

    def get_conversation_status(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation status and metadata"""
        db = next(get_db())
        try:
            conversation = db.query(Conversation).filter(
                Conversation.conversation_id == conversation_id
            ).first()

            if not conversation:
                return {"error": "Conversation not found"}

            turn_count = db.query(ConversationTurn).filter(
                ConversationTurn.conversation_id == conversation_id
            ).count()

            return {
                "conversation_id": conversation_id,
                "status": "active" if conversation.is_active else "inactive",
                "turn_count": turn_count,
                "language": conversation.language,
                "conversation_type": conversation.conversation_type,
                "current_topic": conversation.current_topic,
                "emotional_state": conversation.emotional_state,
                "started_at": conversation.started_at,
                "last_activity": conversation.last_activity
            }

        finally:
            db.close()

    def end_conversation(self, conversation_id: str) -> bool:
        """End a conversation session"""
        db = next(get_db())
        try:
            conversation = db.query(Conversation).filter(
                Conversation.conversation_id == conversation_id
            ).first()

            if conversation:
                conversation.is_active = False
                conversation.last_activity = datetime.utcnow()
                db.commit()
                return True
            return False

        finally:
            db.close()

# Global conversation manager instance
_conversation_manager = None

def get_conversation_manager() -> ConversationManager:
    """Get singleton conversation manager instance"""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager
