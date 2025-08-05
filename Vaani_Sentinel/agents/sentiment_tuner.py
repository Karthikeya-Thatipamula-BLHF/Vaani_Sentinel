"""
Agent H: Sentiment Tuner
Task 2 Requirement: Micro-agent that adjusts sentiment and emotional tone

Capabilities:
- Adjust emotional tone (uplifting, neutral, devotional) before final generation
- Runtime sentiment tuning via CLI or API parameters
- Sentiment analysis and emotional adjustment
"""

import json
import os
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from enum import Enum

class SentimentType(Enum):
    UPLIFTING = "uplifting"
    NEUTRAL = "neutral"
    DEVOTIONAL = "devotional"
    CALMING = "calming"
    ENERGETIC = "energetic"
    PROFESSIONAL = "professional"
    INSPIRATIONAL = "inspirational"

class EmotionalIntensity(Enum):
    SUBTLE = "subtle"
    MODERATE = "moderate"
    STRONG = "strong"

class SentimentTuner:
    """
    Agent H: Sentiment Tuner
    Task 2 micro-agent for runtime emotional tone adjustment
    """
    
    def __init__(self):
        self.output_dir = "./data"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Sentiment adjustment templates
        self.sentiment_templates = {
            SentimentType.UPLIFTING: {
                "keywords": ["inspiring", "motivating", "positive", "encouraging", "hopeful"],
                "phrases": ["You can achieve", "Believe in yourself", "Every step forward", "Embrace the journey"],
                "tone_modifiers": ["✨", "🌟", "💫", "🚀", "💪"],
                "emotional_weight": 0.8
            },
            SentimentType.NEUTRAL: {
                "keywords": ["balanced", "informative", "clear", "factual", "objective"],
                "phrases": ["Consider this", "It's important to note", "Research shows", "Evidence suggests"],
                "tone_modifiers": [],
                "emotional_weight": 0.0
            },
            SentimentType.DEVOTIONAL: {
                "keywords": ["peaceful", "spiritual", "sacred", "divine", "blessed"],
                "phrases": ["Find inner peace", "Connect with the divine", "Sacred wisdom", "Spiritual journey"],
                "tone_modifiers": ["🕉️", "🙏", "✨", "🌸", "💫"],
                "emotional_weight": 0.7
            },
            SentimentType.CALMING: {
                "keywords": ["serene", "tranquil", "gentle", "soothing", "peaceful"],
                "phrases": ["Take a deep breath", "Find your center", "Gentle reminder", "Peaceful moment"],
                "tone_modifiers": ["🌸", "🍃", "💙", "🌊", "☁️"],
                "emotional_weight": 0.5
            },
            SentimentType.ENERGETIC: {
                "keywords": ["dynamic", "vibrant", "exciting", "powerful", "bold"],
                "phrases": ["Let's go!", "Take action", "Seize the moment", "Make it happen"],
                "tone_modifiers": ["⚡", "🔥", "💥", "🎯", "🚀"],
                "emotional_weight": 0.9
            },
            SentimentType.PROFESSIONAL: {
                "keywords": ["strategic", "efficient", "results-driven", "professional", "focused"],
                "phrases": ["Key insights", "Strategic approach", "Professional development", "Best practices"],
                "tone_modifiers": ["📊", "💼", "🎯", "📈", "⭐"],
                "emotional_weight": 0.3
            },
            SentimentType.INSPIRATIONAL: {
                "keywords": ["transformative", "empowering", "breakthrough", "visionary", "remarkable"],
                "phrases": ["Transform your life", "Unlock your potential", "Create your destiny", "Rise above"],
                "tone_modifiers": ["🌟", "✨", "🦋", "🌅", "💎"],
                "emotional_weight": 0.8
            }
        }
        
        # Language-specific sentiment patterns
        self.language_patterns = {
            "en": {"multiplier": 1.0, "cultural_context": "direct"},
            "hi": {"multiplier": 1.2, "cultural_context": "respectful"},
            "sa": {"multiplier": 1.5, "cultural_context": "reverent"},
            "es": {"multiplier": 1.1, "cultural_context": "warm"},
            "fr": {"multiplier": 0.9, "cultural_context": "elegant"},
            "de": {"multiplier": 0.8, "cultural_context": "precise"},
            "ja": {"multiplier": 0.7, "cultural_context": "humble"},
            "ar": {"multiplier": 1.3, "cultural_context": "formal"}
        }
    
    def analyze_current_sentiment(self, content_text: str) -> Dict[str, Any]:
        """Analyze the current sentiment of content"""
        
        content_lower = content_text.lower()
        
        # Simple keyword-based sentiment analysis
        sentiment_scores = {}
        
        for sentiment_type, template in self.sentiment_templates.items():
            score = 0
            keyword_matches = 0
            
            # Check for sentiment keywords
            for keyword in template["keywords"]:
                if keyword in content_lower:
                    score += 1
                    keyword_matches += 1
            
            # Check for sentiment phrases
            for phrase in template["phrases"]:
                if phrase.lower() in content_lower:
                    score += 2
            
            # Check for tone modifiers (emojis)
            for modifier in template["tone_modifiers"]:
                if modifier in content_text:
                    score += 0.5
            
            sentiment_scores[sentiment_type.value] = {
                "score": score,
                "keyword_matches": keyword_matches,
                "confidence": min(score / 5.0, 1.0)  # Normalize to 0-1
            }
        
        # Determine dominant sentiment
        dominant_sentiment = max(sentiment_scores.items(), key=lambda x: x[1]["score"])
        
        return {
            "content_text": content_text,
            "sentiment_scores": sentiment_scores,
            "dominant_sentiment": dominant_sentiment[0],
            "dominant_confidence": dominant_sentiment[1]["confidence"],
            "analysis_timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def adjust_sentiment(
        self,
        content_text: str,
        target_sentiment: str,
        intensity: str = "moderate",
        language: str = "en",
        preserve_meaning: bool = True
    ) -> Dict[str, Any]:
        """
        Adjust content sentiment to target emotional tone
        
        Args:
            content_text: Original content
            target_sentiment: Desired sentiment (uplifting, neutral, devotional, etc.)
            intensity: Adjustment intensity (subtle, moderate, strong)
            language: Content language for cultural adaptation
            preserve_meaning: Whether to preserve original meaning
        """
        
        adjustment_id = str(uuid.uuid4())
        
        # Validate target sentiment
        try:
            target_sentiment_enum = SentimentType(target_sentiment)
        except ValueError:
            return {"error": f"Invalid sentiment type: {target_sentiment}"}
        
        try:
            intensity_enum = EmotionalIntensity(intensity)
        except ValueError:
            return {"error": f"Invalid intensity: {intensity}"}
        
        # Analyze current sentiment
        current_analysis = self.analyze_current_sentiment(content_text)
        
        # Get target sentiment template
        target_template = self.sentiment_templates[target_sentiment_enum]
        
        # Get language pattern
        language_pattern = self.language_patterns.get(language, self.language_patterns["en"])
        
        # Perform sentiment adjustment
        adjusted_content = self._apply_sentiment_adjustment(
            content_text,
            target_template,
            intensity_enum,
            language_pattern,
            preserve_meaning
        )
        
        # Verify adjustment
        adjusted_analysis = self.analyze_current_sentiment(adjusted_content)
        
        adjustment_result = {
            "adjustment_id": adjustment_id,
            "original_content": content_text,
            "adjusted_content": adjusted_content,
            "target_sentiment": target_sentiment,
            "intensity": intensity,
            "language": language,
            "preserve_meaning": preserve_meaning,
            "original_analysis": current_analysis,
            "adjusted_analysis": adjusted_analysis,
            "adjustment_success": adjusted_analysis["dominant_sentiment"] == target_sentiment,
            "improvement_score": self._calculate_improvement_score(current_analysis, adjusted_analysis, target_sentiment),
            "metadata": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "agent": "sentiment_tuner",
                "version": "1.0"
            }
        }
        
        # Save adjustment result
        self._save_adjustment_result(adjustment_result)
        
        return adjustment_result
    
    def _apply_sentiment_adjustment(
        self,
        content: str,
        target_template: Dict,
        intensity: EmotionalIntensity,
        language_pattern: Dict,
        preserve_meaning: bool
    ) -> str:
        """Apply sentiment adjustment to content"""
        
        adjusted_content = content
        
        # Intensity multipliers
        intensity_multipliers = {
            EmotionalIntensity.SUBTLE: 0.3,
            EmotionalIntensity.MODERATE: 0.6,
            EmotionalIntensity.STRONG: 1.0
        }
        
        intensity_factor = intensity_multipliers[intensity]
        cultural_factor = language_pattern["multiplier"]
        
        # Add tone modifiers based on intensity
        if intensity != EmotionalIntensity.SUBTLE and target_template["tone_modifiers"]:
            modifier_count = max(1, int(intensity_factor * 2))
            selected_modifiers = target_template["tone_modifiers"][:modifier_count]
            
            if selected_modifiers:
                adjusted_content += " " + " ".join(selected_modifiers)
        
        # Add sentiment phrases for stronger adjustments
        if intensity == EmotionalIntensity.STRONG and target_template["phrases"]:
            # Add a sentiment phrase at the beginning or end
            sentiment_phrase = target_template["phrases"][0]
            
            if preserve_meaning:
                adjusted_content = f"{sentiment_phrase}. {adjusted_content}"
            else:
                # More aggressive adjustment
                adjusted_content = f"{sentiment_phrase}: {adjusted_content}"
        
        # Apply cultural context adjustments
        if language_pattern["cultural_context"] == "respectful" and not preserve_meaning:
            adjusted_content = self._add_respectful_tone(adjusted_content)
        elif language_pattern["cultural_context"] == "reverent" and not preserve_meaning:
            adjusted_content = self._add_reverent_tone(adjusted_content)
        
        return adjusted_content
    
    def _add_respectful_tone(self, content: str) -> str:
        """Add respectful tone for Hindi/Indian languages"""
        respectful_prefixes = ["आदरणीय", "सम्मानित", "प्रिय"]
        if not any(prefix in content for prefix in respectful_prefixes):
            return f"आदरणीय मित्रों, {content}"
        return content
    
    def _add_reverent_tone(self, content: str) -> str:
        """Add reverent tone for Sanskrit/spiritual content"""
        reverent_prefixes = ["श्रद्धेय", "पूज्य", "दिव्य"]
        if not any(prefix in content for prefix in reverent_prefixes):
            return f"🕉️ {content}"
        return content
    
    def _calculate_improvement_score(
        self,
        original_analysis: Dict,
        adjusted_analysis: Dict,
        target_sentiment: str
    ) -> float:
        """Calculate how much the adjustment improved sentiment alignment"""
        
        original_score = original_analysis["sentiment_scores"].get(target_sentiment, {}).get("confidence", 0)
        adjusted_score = adjusted_analysis["sentiment_scores"].get(target_sentiment, {}).get("confidence", 0)
        
        improvement = adjusted_score - original_score
        return round(improvement, 3)
    
    def _save_adjustment_result(self, result: Dict[str, Any]):
        """Save sentiment adjustment result"""
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"sentiment_adjustment_{result['adjustment_id']}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"Sentiment adjustment saved to: {filepath}")
            
        except Exception as e:
            print(f"Error saving sentiment adjustment: {e}")
    
    def batch_sentiment_adjustment(
        self,
        content_list: List[Dict[str, Any]],
        target_sentiment: str,
        intensity: str = "moderate"
    ) -> Dict[str, Any]:
        """Adjust sentiment for multiple content pieces"""
        
        batch_id = str(uuid.uuid4())
        batch_results = []
        
        for i, content_item in enumerate(content_list):
            content_text = content_item.get("text", "")
            language = content_item.get("language", "en")
            
            if content_text:
                result = self.adjust_sentiment(
                    content_text=content_text,
                    target_sentiment=target_sentiment,
                    intensity=intensity,
                    language=language
                )
                
                result["batch_index"] = i
                batch_results.append(result)
        
        batch_summary = {
            "batch_id": batch_id,
            "total_items": len(content_list),
            "processed_items": len(batch_results),
            "target_sentiment": target_sentiment,
            "intensity": intensity,
            "results": batch_results,
            "batch_statistics": self._calculate_batch_statistics(batch_results),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        return batch_summary
    
    def _calculate_batch_statistics(self, results: List[Dict]) -> Dict[str, Any]:
        """Calculate statistics for batch processing"""
        
        if not results:
            return {}
        
        successful_adjustments = sum(1 for r in results if r.get("adjustment_success", False))
        total_improvement = sum(r.get("improvement_score", 0) for r in results)
        
        return {
            "success_rate": successful_adjustments / len(results),
            "average_improvement": total_improvement / len(results),
            "total_processed": len(results),
            "successful_adjustments": successful_adjustments
        }
    
    def get_available_sentiments(self) -> List[Dict[str, Any]]:
        """Get list of available sentiment types"""
        
        return [
            {
                "sentiment": sentiment.value,
                "description": f"Emotional tone: {sentiment.value}",
                "keywords": template["keywords"][:3],  # Show first 3 keywords
                "emotional_weight": template["emotional_weight"]
            }
            for sentiment, template in self.sentiment_templates.items()
        ]

# Global sentiment tuner instance
sentiment_tuner = SentimentTuner()

def get_sentiment_tuner() -> SentimentTuner:
    """Get the global sentiment tuner instance"""
    return sentiment_tuner
