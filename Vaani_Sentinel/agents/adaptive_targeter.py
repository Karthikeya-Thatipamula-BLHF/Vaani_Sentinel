"""
Agent I: Context-Aware Platform Targeter
Task 2 Requirement: Context-aware platform targeting with intelligent formatting

Capabilities:
- Tailor hashtags, post formats, and audio lengths according to platform
- Instagram: Emojis + 3-4 hashtags
- Twitter: 1-2 hashtags
- Spotify: 30-sec TTS audio intro + outro
- Context analysis for optimal content adaptation
"""

import json
import os
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import random

class PlatformTargeter:
    """
    Agent I: Context-Aware Platform Targeter
    Task 2 requirement for intelligent platform-specific content adaptation
    """
    
    def __init__(self):
        self.output_dir = "./data"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Platform-specific configurations
        self.platform_configs = {
            "instagram": {
                "character_limit": 2200,
                "hashtag_count": {"min": 3, "max": 4},
                "emoji_usage": "high",
                "content_style": "visual_storytelling",
                "audio_length": {"min": 15, "max": 60},
                "optimal_times": ["12:00", "17:00", "20:00"],
                "audience_type": "visual_consumers",
                "engagement_features": ["stories", "reels", "carousel"]
            },
            "twitter": {
                "character_limit": 280,
                "hashtag_count": {"min": 1, "max": 2},
                "emoji_usage": "moderate",
                "content_style": "conversational",
                "audio_length": {"min": 10, "max": 30},
                "optimal_times": ["09:00", "12:00", "15:00"],
                "audience_type": "news_consumers",
                "engagement_features": ["threads", "polls", "spaces"]
            },
            "linkedin": {
                "character_limit": 3000,
                "hashtag_count": {"min": 2, "max": 5},
                "emoji_usage": "low",
                "content_style": "professional",
                "audio_length": {"min": 30, "max": 120},
                "optimal_times": ["08:00", "12:00", "17:00"],
                "audience_type": "professionals",
                "engagement_features": ["articles", "polls", "events"]
            },
            "spotify": {
                "character_limit": 500,
                "hashtag_count": {"min": 0, "max": 2},
                "emoji_usage": "minimal",
                "content_style": "audio_focused",
                "audio_length": {"min": 30, "max": 180},
                "optimal_times": ["07:00", "18:00", "22:00"],
                "audience_type": "audio_consumers",
                "engagement_features": ["playlists", "podcasts", "audio_stories"]
            }
        }
        
        # Context-aware hashtag libraries
        self.hashtag_libraries = {
            "spiritual": {
                "instagram": ["#Mindfulness", "#Spirituality", "#InnerPeace", "#Meditation"],
                "twitter": ["#Mindfulness", "#Peace"],
                "linkedin": ["#PersonalDevelopment", "#Mindfulness", "#Leadership"],
                "spotify": ["#Meditation", "#Calm"]
            },
            "motivational": {
                "instagram": ["#Motivation", "#Success", "#Inspiration", "#Goals"],
                "twitter": ["#Motivation", "#Success"],
                "linkedin": ["#Leadership", "#Success", "#Growth", "#Motivation"],
                "spotify": ["#Motivation", "#Success"]
            },
            "educational": {
                "instagram": ["#Learning", "#Knowledge", "#Education", "#Growth"],
                "twitter": ["#Learning", "#Knowledge"],
                "linkedin": ["#Education", "#ProfessionalDevelopment", "#Learning"],
                "spotify": ["#Learning", "#Knowledge"]
            },
            "cultural": {
                "instagram": ["#Culture", "#Heritage", "#Tradition", "#Wisdom"],
                "twitter": ["#Culture", "#Heritage"],
                "linkedin": ["#CulturalAwareness", "#Diversity", "#Heritage"],
                "spotify": ["#Culture", "#Tradition"]
            }
        }
        
        # Emoji libraries by platform and context
        self.emoji_libraries = {
            "instagram": {
                "spiritual": ["🕉️", "🙏", "✨", "🌸", "💫", "🧘‍♀️"],
                "motivational": ["💪", "🚀", "⭐", "🔥", "💯", "🎯"],
                "educational": ["📚", "🧠", "💡", "📖", "🎓", "✏️"],
                "cultural": ["🏛️", "🎭", "🌍", "📿", "🎨", "🏺"]
            },
            "twitter": {
                "spiritual": ["🕉️", "🙏", "✨"],
                "motivational": ["💪", "🚀", "⭐"],
                "educational": ["📚", "💡", "🧠"],
                "cultural": ["🌍", "🎭", "📿"]
            },
            "linkedin": {
                "spiritual": ["🧘‍♀️", "✨"],
                "motivational": ["🚀", "📈", "💼"],
                "educational": ["📚", "🎓", "💡"],
                "cultural": ["🌍", "🤝", "📊"]
            },
            "spotify": {
                "spiritual": ["🎵", "🧘‍♀️"],
                "motivational": ["🎵", "🚀"],
                "educational": ["🎵", "📚"],
                "cultural": ["🎵", "🌍"]
            }
        }
    
    def analyze_content_context(self, content_text: str, language: str = "en") -> Dict[str, Any]:
        """Analyze content to determine optimal platform targeting context"""
        
        content_lower = content_text.lower()
        
        # Context detection keywords
        context_keywords = {
            "spiritual": ["peace", "meditation", "spiritual", "divine", "sacred", "soul", "mindfulness"],
            "motivational": ["success", "achieve", "goal", "motivation", "inspire", "dream", "overcome"],
            "educational": ["learn", "knowledge", "understand", "study", "research", "fact", "information"],
            "cultural": ["tradition", "culture", "heritage", "history", "ancient", "wisdom", "custom"],
            "professional": ["business", "career", "leadership", "strategy", "professional", "work"],
            "personal": ["life", "personal", "experience", "journey", "growth", "development"]
        }
        
        # Calculate context scores
        context_scores = {}
        for context, keywords in context_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            context_scores[context] = score
        
        # Determine primary context
        primary_context = max(context_scores.items(), key=lambda x: x[1])[0] if any(context_scores.values()) else "general"
        
        # Analyze content characteristics
        word_count = len(content_text.split())
        sentence_count = content_text.count('.') + content_text.count('!') + content_text.count('?')
        
        return {
            "content_text": content_text,
            "language": language,
            "primary_context": primary_context,
            "context_scores": context_scores,
            "content_characteristics": {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "character_count": len(content_text),
                "complexity": "simple" if word_count < 20 else "moderate" if word_count < 50 else "complex"
            },
            "analysis_timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def target_platform_content(
        self,
        content_text: str,
        platform: str,
        context: Optional[str] = None,
        language: str = "en",
        tone: str = "neutral"
    ) -> Dict[str, Any]:
        """
        Generate platform-targeted content with context-aware formatting
        
        Args:
            content_text: Original content
            platform: Target platform (instagram, twitter, linkedin, spotify)
            context: Content context (spiritual, motivational, etc.)
            language: Content language
            tone: Content tone
        """
        
        targeting_id = str(uuid.uuid4())
        
        # Validate platform
        if platform not in self.platform_configs:
            return {"error": f"Unsupported platform: {platform}"}
        
        # Analyze content context if not provided
        if not context:
            context_analysis = self.analyze_content_context(content_text, language)
            context = context_analysis["primary_context"]
        else:
            context_analysis = self.analyze_content_context(content_text, language)
        
        platform_config = self.platform_configs[platform]
        
        # Generate platform-specific content
        targeted_content = self._generate_platform_content(
            content_text, platform, context, platform_config, tone
        )
        
        # Generate hashtags
        hashtags = self._generate_context_hashtags(platform, context, platform_config)
        
        # Generate emojis
        emojis = self._generate_context_emojis(platform, context, platform_config)
        
        # Generate audio specifications (for audio platforms)
        audio_specs = self._generate_audio_specifications(platform, content_text, platform_config)
        
        # Format final content
        final_content = self._format_final_content(
            targeted_content, hashtags, emojis, platform_config
        )
        
        targeting_result = {
            "targeting_id": targeting_id,
            "original_content": content_text,
            "platform": platform,
            "context": context,
            "language": language,
            "tone": tone,
            "context_analysis": context_analysis,
            "targeted_content": targeted_content,
            "hashtags": hashtags,
            "emojis": emojis,
            "final_content": final_content,
            "audio_specifications": audio_specs,
            "platform_compliance": self._check_platform_compliance(final_content, platform_config),
            "optimization_suggestions": self._generate_optimization_suggestions(platform, context, final_content),
            "metadata": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "agent": "context_aware_platform_targeter",
                "version": "1.0"
            }
        }
        
        # Save targeting result
        self._save_targeting_result(targeting_result)
        
        return targeting_result
    
    def _generate_platform_content(
        self, content: str, platform: str, context: str, config: Dict, tone: str
    ) -> str:
        """Generate platform-optimized content"""
        
        # Platform-specific content adaptations
        if platform == "instagram":
            # Visual storytelling approach
            if config["content_style"] == "visual_storytelling":
                return self._adapt_for_visual_storytelling(content, context)
        
        elif platform == "twitter":
            # Conversational and concise
            if len(content) > 200:  # Leave room for hashtags
                return self._create_twitter_thread_preview(content)
            return content
        
        elif platform == "linkedin":
            # Professional formatting
            return self._adapt_for_professional_context(content, context)
        
        elif platform == "spotify":
            # Audio-focused content
            return self._adapt_for_audio_content(content, context)
        
        return content
    
    def _adapt_for_visual_storytelling(self, content: str, context: str) -> str:
        """Adapt content for Instagram's visual storytelling format"""
        
        # Add visual cues and storytelling elements
        if context == "spiritual":
            return f"✨ {content}\n\nTake a moment to reflect on this wisdom..."
        elif context == "motivational":
            return f"💪 {content}\n\nWhat's your next step towards this goal?"
        else:
            return f"📸 {content}\n\nShare your thoughts below!"
    
    def _create_twitter_thread_preview(self, content: str) -> str:
        """Create Twitter thread preview for long content"""
        
        # Truncate and add thread indicator
        truncated = content[:200] + "..."
        return f"{truncated}\n\n🧵 Thread (1/n)"
    
    def _adapt_for_professional_context(self, content: str, context: str) -> str:
        """Adapt content for LinkedIn's professional context"""
        
        if context == "motivational":
            return f"Professional Insight:\n\n{content}\n\nWhat's your experience with this approach?"
        elif context == "educational":
            return f"Key Learning:\n\n{content}\n\nHow do you apply this in your field?"
        else:
            return f"Thought Leadership:\n\n{content}\n\nI'd love to hear your perspective."
    
    def _adapt_for_audio_content(self, content: str, context: str) -> str:
        """Adapt content for Spotify's audio-focused format"""
        
        # Add audio intro/outro cues
        intro = "🎵 Listen to this inspiring message:"
        outro = "🎧 Perfect for your daily reflection playlist."
        
        return f"{intro}\n\n{content}\n\n{outro}"
    
    def _generate_context_hashtags(self, platform: str, context: str, config: Dict) -> List[str]:
        """Generate context-appropriate hashtags for platform"""
        
        hashtag_count = random.randint(config["hashtag_count"]["min"], config["hashtag_count"]["max"])
        
        # Get context-specific hashtags
        context_hashtags = self.hashtag_libraries.get(context, {}).get(platform, [])
        
        # Add general hashtags if needed
        general_hashtags = ["#Content", "#Inspiration", "#Wisdom", "#Growth", "#Life"]
        
        available_hashtags = context_hashtags + general_hashtags
        selected_hashtags = random.sample(available_hashtags, min(hashtag_count, len(available_hashtags)))
        
        return selected_hashtags
    
    def _generate_context_emojis(self, platform: str, context: str, config: Dict) -> List[str]:
        """Generate context-appropriate emojis for platform"""
        
        emoji_usage = config["emoji_usage"]
        
        if emoji_usage == "minimal":
            emoji_count = random.randint(0, 1)
        elif emoji_usage == "low":
            emoji_count = random.randint(1, 2)
        elif emoji_usage == "moderate":
            emoji_count = random.randint(2, 3)
        else:  # high
            emoji_count = random.randint(3, 5)
        
        context_emojis = self.emoji_libraries.get(platform, {}).get(context, ["✨"])
        
        if emoji_count == 0:
            return []
        
        selected_emojis = random.sample(context_emojis, min(emoji_count, len(context_emojis)))
        return selected_emojis
    
    def _generate_audio_specifications(self, platform: str, content: str, config: Dict) -> Dict[str, Any]:
        """Generate audio specifications for audio-capable platforms"""
        
        if platform not in ["spotify", "instagram", "twitter"]:
            return {}
        
        word_count = len(content.split())
        estimated_duration = word_count / 2.5  # Approximate words per second for TTS
        
        min_duration = config["audio_length"]["min"]
        max_duration = config["audio_length"]["max"]
        
        # Adjust duration to platform requirements
        target_duration = max(min_duration, min(estimated_duration, max_duration))
        
        audio_specs = {
            "estimated_duration": round(estimated_duration, 1),
            "target_duration": round(target_duration, 1),
            "within_limits": min_duration <= estimated_duration <= max_duration,
            "format": "mp3",
            "quality": "high" if platform == "spotify" else "standard"
        }
        
        if platform == "spotify":
            # Add Spotify-specific audio requirements
            audio_specs.update({
                "intro_duration": 3,
                "outro_duration": 2,
                "total_with_intro_outro": target_duration + 5,
                "recommended_voice": "professional" if target_duration > 60 else "conversational"
            })
        
        return audio_specs
    
    def _format_final_content(
        self, content: str, hashtags: List[str], emojis: List[str], config: Dict
    ) -> str:
        """Format final content with hashtags and emojis"""
        
        # Add emojis to content
        if emojis:
            emoji_string = " ".join(emojis)
            content = f"{emoji_string} {content}"
        
        # Add hashtags
        if hashtags:
            hashtag_string = " ".join(hashtags)
            content = f"{content}\n\n{hashtag_string}"
        
        return content
    
    def _check_platform_compliance(self, content: str, config: Dict) -> Dict[str, Any]:
        """Check if content complies with platform requirements"""
        
        character_count = len(content)
        character_limit = config["character_limit"]
        
        return {
            "character_count": character_count,
            "character_limit": character_limit,
            "within_limit": character_count <= character_limit,
            "utilization_percentage": round((character_count / character_limit) * 100, 1),
            "characters_remaining": character_limit - character_count
        }
    
    def _generate_optimization_suggestions(
        self, platform: str, context: str, content: str
    ) -> List[str]:
        """Generate optimization suggestions for better engagement"""
        
        suggestions = []
        
        # Platform-specific suggestions
        if platform == "instagram":
            suggestions.append("Consider adding a call-to-action in your caption")
            suggestions.append("Use Instagram Stories for behind-the-scenes content")
        
        elif platform == "twitter":
            suggestions.append("Engage with replies to boost visibility")
            suggestions.append("Consider creating a thread for detailed explanations")
        
        elif platform == "linkedin":
            suggestions.append("Ask a question to encourage professional discussion")
            suggestions.append("Share relevant industry insights")
        
        elif platform == "spotify":
            suggestions.append("Create a consistent audio series for better discovery")
            suggestions.append("Use clear audio quality for better listener experience")
        
        # Context-specific suggestions
        if context == "spiritual":
            suggestions.append("Include meditation or reflection prompts")
        elif context == "motivational":
            suggestions.append("Add actionable steps or challenges")
        elif context == "educational":
            suggestions.append("Provide sources or additional reading materials")
        
        return suggestions
    
    def _save_targeting_result(self, result: Dict[str, Any]):
        """Save platform targeting result"""
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"platform_targeting_{result['targeting_id']}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"Platform targeting result saved to: {filepath}")
            
        except Exception as e:
            print(f"Error saving platform targeting result: {e}")
    
    def get_platform_capabilities(self) -> Dict[str, Any]:
        """Get capabilities and configurations for all platforms"""
        
        return {
            "supported_platforms": list(self.platform_configs.keys()),
            "platform_configs": self.platform_configs,
            "available_contexts": list(self.hashtag_libraries.keys()),
            "emoji_support": {platform: list(emojis.keys()) for platform, emojis in self.emoji_libraries.items()}
        }

# Global platform targeter instance
platform_targeter = PlatformTargeter()

def get_platform_targeter() -> PlatformTargeter:
    """Get the global platform targeter instance"""
    return platform_targeter
