"""
Platform Publisher for Vaani Sentinel X
Task 3 Agent J: Platform Publisher - Simulate posting to 3 platforms
Task 4 Component 3: Simulated Multilingual Preview Generator
Extended to show how posts would appear in different languages
"""

import json
import os
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from utils.language_mapper import get_language_mapper
from utils.simulate_translation import get_simulated_translator

class MultilingualPublisherSimulator:
    """
    Task 3 Agent J: Platform Publisher
    Task 4 Component 3: Simulated Multilingual Preview Generator

    Simulates posting to 3 platforms:
    - Instagram (Text + Voice thumbnail)
    - Twitter (Short text + TTS snippet)
    - LinkedIn (Formatted post with title + summary + TTS)

    Supports preview mode and auto-picks language + voice based on content metadata
    """
    
    def __init__(self):
        self.language_mapper = get_language_mapper()
        self.simulated_translator = get_simulated_translator()
        self.output_dir = "./data"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Platform configurations
        self.platform_configs = {
            "twitter": {
                "max_length": 280,
                "supports_images": True,
                "supports_audio": False,
                "hashtag_limit": 3,
                "format_style": "concise"
            },
            "instagram": {
                "max_length": 2200,
                "supports_images": True,
                "supports_audio": True,
                "hashtag_limit": 30,
                "format_style": "visual_storytelling"
            },
            "linkedin": {
                "max_length": 3000,
                "supports_images": True,
                "supports_audio": False,
                "hashtag_limit": 5,
                "format_style": "professional"
            },
            "spotify": {
                "max_length": 500,
                "supports_images": True,
                "supports_audio": True,
                "hashtag_limit": 0,
                "format_style": "audio_focused"
            }
        }
    
    def generate_multilingual_post_preview(
        self,
        original_post_id: str,
        content_text: str,
        target_languages: List[str],
        platforms: List[str],
        user_profile_id: str = "general",
        tone: str = "neutral"
    ) -> Dict[str, Any]:
        """
        Task 4 Component 4: Post Output Preview JSON
        Generate preview showing original post ID, selected language, voice, platform preview
        """
        
        preview_id = str(uuid.uuid4())
        
        # Generate previews for each language-platform combination
        language_platform_previews = {}
        
        for language in target_languages:
            # Get language metadata
            language_info = self.language_mapper.detect_user_language_preference(
                user_profile_id, content_text, platforms[0] if platforms else "twitter"
            )
            
            # Override detected language with target language
            language_info["content_language"] = language
            language_info["voice_tag"] = self.language_mapper._get_voice_tag_for_language(language, tone)
            
            language_platform_previews[language] = {
                "language": language,
                "language_name": self.language_mapper.supported_languages.get(language, language),
                "voice_tag": language_info["voice_tag"],
                "platforms": {}
            }
            
            # Generate platform-specific previews
            for platform in platforms:
                platform_preview = self._generate_platform_preview(
                    content_text, language, platform, language_info, original_post_id
                )
                language_platform_previews[language]["platforms"][platform] = platform_preview
        
        # Create comprehensive preview output
        preview_output = {
            "preview_id": preview_id,
            "original_post_id": original_post_id,
            "source_content": content_text,
            "user_profile_id": user_profile_id,
            "tone": tone,
            "target_languages": target_languages,
            "target_platforms": platforms,
            "language_platform_previews": language_platform_previews,
            "metadata": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "agent": "multilingual_publisher_simulator",
                "version": "task4_implementation",
                "total_combinations": len(target_languages) * len(platforms),
                "simulation_note": "Task 4 preview with dummy translations"
            }
        }
        
        # Save preview output
        self._save_preview_output(preview_output)
        
        return preview_output
    
    def _generate_platform_preview(
        self,
        content_text: str,
        language: str,
        platform: str,
        language_info: Dict[str, Any],
        original_post_id: str
    ) -> Dict[str, Any]:
        """Generate preview for specific platform and language"""
        
        # Get simulated translation
        translation_result = self.simulated_translator.simulate_translation(
            content_text, language, "en"
        )
        
        # Get platform configuration
        platform_config = self.platform_configs.get(platform, self.platform_configs["twitter"])
        
        # Format content for platform
        formatted_content = self._format_content_for_platform(
            translation_result["translated_text"], platform, language
        )
        
        # Generate platform-specific metadata
        platform_metadata = self._generate_platform_metadata(
            platform, language, language_info, formatted_content
        )
        
        return {
            "original_post_id": original_post_id,
            "platform": platform,
            "language": language,
            "voice_tag": language_info["voice_tag"],
            "original_text": content_text,
            "translated_text": translation_result["translated_text"],
            "formatted_content": formatted_content,
            "platform_metadata": platform_metadata,
            "content_stats": {
                "character_count": len(formatted_content),
                "max_allowed": platform_config["max_length"],
                "within_limits": len(formatted_content) <= platform_config["max_length"],
                "word_count": len(formatted_content.split()),
                "hashtag_count": formatted_content.count("#")
            },
            "translation_info": {
                "confidence": translation_result["confidence"],
                "method": translation_result["translation_method"],
                "is_simulation": translation_result["is_simulation"]
            },
            "preview_url": f"https://preview.vaani-sentinel.com/{platform}/{language}/{original_post_id}",
            "estimated_engagement": self._estimate_engagement(platform, language, formatted_content)
        }
    
    def _format_content_for_platform(self, content: str, platform: str, language: str) -> str:
        """Format content according to platform requirements"""
        
        if platform == "twitter":
            return self._format_twitter_content(content, language)
        elif platform == "instagram":
            return self._format_instagram_content(content, language)
        elif platform == "linkedin":
            return self._format_linkedin_content(content, language)
        elif platform == "spotify":
            return self._format_spotify_content(content, language)
        else:
            return content
    
    def _format_twitter_content(self, content: str, language: str) -> str:
        """Format content for Twitter"""
        hashtags = self._get_hashtags_for_language(language, "twitter")
        formatted = f"{content} {hashtags}"
        
        if len(formatted) > 280:
            # Trim content to fit
            available_chars = 280 - len(hashtags) - 1
            trimmed_content = content[:available_chars-3] + "..."
            formatted = f"{trimmed_content} {hashtags}"
        
        return formatted
    
    def _format_instagram_content(self, content: str, language: str) -> str:
        """Format content for Instagram"""
        hashtags = self._get_hashtags_for_language(language, "instagram")
        call_to_action = self._get_call_to_action(language)
        
        formatted = f"{content}\n\n{hashtags}\n\n{call_to_action}"
        
        if len(formatted) > 2200:
            # Trim if necessary
            available_chars = 2200 - len(hashtags) - len(call_to_action) - 6  # 6 for newlines
            trimmed_content = content[:available_chars-3] + "..."
            formatted = f"{trimmed_content}\n\n{hashtags}\n\n{call_to_action}"
        
        return formatted
    
    def _format_linkedin_content(self, content: str, language: str) -> str:
        """Format content for LinkedIn"""
        hashtags = self._get_hashtags_for_language(language, "linkedin")
        professional_note = self._get_professional_note(language)
        
        formatted = f"{content}\n\n{professional_note}\n\n{hashtags}"
        
        if len(formatted) > 3000:
            # Trim if necessary
            available_chars = 3000 - len(hashtags) - len(professional_note) - 6
            trimmed_content = content[:available_chars-3] + "..."
            formatted = f"{trimmed_content}\n\n{professional_note}\n\n{hashtags}"
        
        return formatted
    
    def _format_spotify_content(self, content: str, language: str) -> str:
        """Format content for Spotify (audio-focused)"""
        # Spotify format focuses on audio description
        audio_description = self._get_audio_description(language)
        formatted = f"{content}\n\n{audio_description}"
        
        if len(formatted) > 500:
            available_chars = 500 - len(audio_description) - 2
            trimmed_content = content[:available_chars-3] + "..."
            formatted = f"{trimmed_content}\n\n{audio_description}"
        
        return formatted
    
    def _get_hashtags_for_language(self, language: str, platform: str) -> str:
        """Get appropriate hashtags for language and platform"""
        
        hashtag_sets = {
            "en": {
                "twitter": "#Mindfulness #Wisdom #Peace",
                "instagram": "#Mindfulness #Wisdom #Peace #Meditation #InnerPeace #Spirituality #Growth #Inspiration",
                "linkedin": "#PersonalDevelopment #Mindfulness #Leadership #Growth #Wisdom"
            },
            "hi": {
                "twitter": "#मानसिकशांति #ज्ञान #शांति",
                "instagram": "#मानसिकशांति #ज्ञान #शांति #ध्यान #आध्यात्म #प्रेरणा #विकास #जीवन",
                "linkedin": "#व्यक्तित्वविकास #नेतृत्व #ज्ञान #प्रेरणा #सफलता"
            },
            "sa": {
                "twitter": "#ध्यान #ज्ञान #शान्ति",
                "instagram": "#ध्यान #ज्ञान #शान्ति #योग #आध्यात्म #मन्त्र #संस्कृत #धर्म",
                "linkedin": "#आध्यात्म #ज्ञान #योग #संस्कृत #धर्म"
            }
        }
        
        return hashtag_sets.get(language, hashtag_sets["en"]).get(platform, hashtag_sets["en"]["twitter"])
    
    def _get_call_to_action(self, language: str) -> str:
        """Get call to action for language"""
        cta_texts = {
            "en": "Share your thoughts! 💭✨",
            "hi": "अपने विचार साझा करें! 💭✨",
            "sa": "अपने विचारान् साझां कुर्वन्तु! 💭✨"
        }
        return cta_texts.get(language, cta_texts["en"])
    
    def _get_professional_note(self, language: str) -> str:
        """Get professional note for LinkedIn"""
        notes = {
            "en": "What are your thoughts on this? Let's discuss.",
            "hi": "इस पर आपके क्या विचार हैं? आइए चर्चा करते हैं।",
            "sa": "अस्मिन् विषये भवतां किं मतम्? चर्चां कुर्मः।"
        }
        return notes.get(language, notes["en"])
    
    def _get_audio_description(self, language: str) -> str:
        """Get audio description for Spotify"""
        descriptions = {
            "en": "🎧 Listen to this inspiring message",
            "hi": "🎧 इस प्रेरणादायक संदेश को सुनें",
            "sa": "🎧 एतत् प्रेरणादायकं सन्देशं श्रृणुत"
        }
        return descriptions.get(language, descriptions["en"])
    
    def _generate_platform_metadata(
        self, 
        platform: str, 
        language: str, 
        language_info: Dict[str, Any], 
        formatted_content: str
    ) -> Dict[str, Any]:
        """Generate platform-specific metadata"""
        
        base_metadata = {
            "platform": platform,
            "language": language,
            "voice_tag": language_info["voice_tag"],
            "content_length": len(formatted_content),
            "estimated_read_time": len(formatted_content.split()) / 200,  # words per minute
            "supports_audio": self.platform_configs[platform]["supports_audio"],
            "supports_images": self.platform_configs[platform]["supports_images"]
        }
        
        if platform == "spotify":
            base_metadata.update({
                "audio_duration_estimate": len(formatted_content.split()) / 2.5,  # words per second
                "voice_preview_url": f"https://voice-preview.vaani-sentinel.com/{language_info['voice_tag']}"
            })
        
        return base_metadata
    
    def _estimate_engagement(self, platform: str, language: str, content: str) -> Dict[str, Any]:
        """Estimate engagement metrics (simulated for Task 4)"""
        
        import random
        
        # Simulate engagement based on platform and language
        base_engagement = {
            "twitter": {"likes": 50, "retweets": 10, "comments": 5},
            "instagram": {"likes": 100, "comments": 15, "shares": 8},
            "linkedin": {"likes": 30, "comments": 8, "shares": 5},
            "spotify": {"plays": 200, "likes": 25, "shares": 3}
        }
        
        platform_base = base_engagement.get(platform, base_engagement["twitter"])
        
        # Add some randomness and language factor
        language_multiplier = 1.2 if language in ["hi", "sa", "mr"] else 1.0
        
        estimated = {}
        for metric, base_value in platform_base.items():
            estimated[metric] = int(base_value * language_multiplier * random.uniform(0.8, 1.5))
        
        estimated["engagement_rate"] = round(random.uniform(0.02, 0.08), 3)
        estimated["is_simulation"] = True
        
        return estimated
    
    def _save_preview_output(self, preview_output: Dict[str, Any]):
        """Save preview output to JSON file"""
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"multilingual_post_preview_{preview_output['preview_id']}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(preview_output, f, indent=2, ensure_ascii=False)
            
            print(f"Multilingual preview saved to: {filepath}")
            
        except Exception as e:
            print(f"Error saving preview output: {e}")

    def simulate_platform_publishing(
        self,
        content_id: str,
        content_text: str,
        platforms: List[str] = ["instagram", "twitter", "linkedin"],
        preview_mode: bool = True,
        user_profile_id: str = "general",
        tone: str = "neutral"
    ) -> Dict[str, Any]:
        """
        Task 3 Agent J: Simulate posting to 3 platforms

        Args:
            content_id: Unique content identifier
            content_text: Content to publish
            platforms: List of platforms to publish to
            preview_mode: If True, generates JSON but doesn't actually post
            user_profile_id: User profile for language/voice selection
            tone: Content tone

        Returns:
            Publishing simulation results
        """

        publishing_id = str(uuid.uuid4())

        # Auto-pick language + voice based on content metadata
        language_info = self.language_mapper.detect_user_language_preference(
            user_profile_id, content_text, platforms[0] if platforms else "twitter"
        )

        content_language = language_info["content_language"]
        voice_tag = language_info["voice_tag"]

        # Generate platform-specific posts
        platform_posts = {}

        for platform in platforms:
            if platform in ["instagram", "twitter", "linkedin"]:  # Task 3 specified platforms
                platform_post = self._generate_task3_platform_post(
                    content_id, content_text, platform, content_language,
                    voice_tag, tone, preview_mode
                )
                platform_posts[platform] = platform_post

        publishing_result = {
            "publishing_id": publishing_id,
            "content_id": content_id,
            "source_content": content_text,
            "auto_selected_language": content_language,
            "auto_selected_voice": voice_tag,
            "user_profile_id": user_profile_id,
            "tone": tone,
            "preview_mode": preview_mode,
            "platforms": platforms,
            "platform_posts": platform_posts,
            "metadata": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "agent": "task3_platform_publisher",
                "version": "1.0",
                "total_platforms": len(platforms),
                "publishing_status": "preview" if preview_mode else "published"
            }
        }

        # Save publishing result
        self._save_publishing_result(publishing_result)

        return publishing_result

    def _generate_task3_platform_post(
        self,
        content_id: str,
        content_text: str,
        platform: str,
        language: str,
        voice_tag: str,
        tone: str,
        preview_mode: bool
    ) -> Dict[str, Any]:
        """Generate Task 3 specific platform post"""

        # Get simulated translation
        translation_result = self.simulated_translator.simulate_translation(
            content_text, language, "en"
        )

        if platform == "instagram":
            return self._generate_instagram_post_task3(
                content_id, translation_result, voice_tag, tone, preview_mode
            )
        elif platform == "twitter":
            return self._generate_twitter_post_task3(
                content_id, translation_result, voice_tag, tone, preview_mode
            )
        elif platform == "linkedin":
            return self._generate_linkedin_post_task3(
                content_id, translation_result, voice_tag, tone, preview_mode
            )
        else:
            return self._generate_generic_post(
                content_id, translation_result, voice_tag, tone, preview_mode
            )

    def _generate_instagram_post_task3(
        self, content_id: str, translation_result: Dict, voice_tag: str,
        tone: str, preview_mode: bool
    ) -> Dict[str, Any]:
        """Task 3: Instagram (Text + Voice thumbnail)"""

        translated_text = translation_result["translated_text"]
        formatted_content = self._format_instagram_content(translated_text, translation_result["target_language"])

        return {
            "platform": "instagram",
            "content_id": content_id,
            "post_type": "text_with_voice_thumbnail",
            "text_content": formatted_content,
            "voice_thumbnail": {
                "voice_tag": voice_tag,
                "thumbnail_url": f"https://voice-thumbnails.vaani-sentinel.com/{voice_tag}/{content_id}.jpg",
                "audio_preview_url": f"https://audio-preview.vaani-sentinel.com/{voice_tag}/{content_id}.mp3",
                "duration_estimate": len(translated_text.split()) / 2.5
            },
            "hashtags": self._get_hashtags_for_language(translation_result["target_language"], "instagram"),
            "call_to_action": self._get_call_to_action(translation_result["target_language"]),
            "character_count": len(formatted_content),
            "within_limits": len(formatted_content) <= 2200,
            "preview_mode": preview_mode,
            "posting_url": f"https://instagram.com/vaani_sentinel/post/{content_id}" if not preview_mode else None,
            "estimated_reach": self._estimate_instagram_reach(formatted_content, voice_tag)
        }

    def _generate_twitter_post_task3(
        self, content_id: str, translation_result: Dict, voice_tag: str,
        tone: str, preview_mode: bool
    ) -> Dict[str, Any]:
        """Task 3: Twitter (Short text + TTS snippet)"""

        translated_text = translation_result["translated_text"]
        formatted_content = self._format_twitter_content(translated_text, translation_result["target_language"])

        return {
            "platform": "twitter",
            "content_id": content_id,
            "post_type": "short_text_with_tts_snippet",
            "text_content": formatted_content,
            "tts_snippet": {
                "voice_tag": voice_tag,
                "snippet_url": f"https://tts-snippets.vaani-sentinel.com/{voice_tag}/{content_id}.mp3",
                "snippet_duration": min(30, len(translated_text.split()) / 2.5),  # Max 30 seconds
                "waveform_image": f"https://waveforms.vaani-sentinel.com/{content_id}.png"
            },
            "hashtags": self._get_hashtags_for_language(translation_result["target_language"], "twitter"),
            "character_count": len(formatted_content),
            "within_limits": len(formatted_content) <= 280,
            "preview_mode": preview_mode,
            "posting_url": f"https://twitter.com/vaani_sentinel/status/{content_id}" if not preview_mode else None,
            "estimated_engagement": self._estimate_twitter_engagement(formatted_content, voice_tag)
        }

    def _generate_linkedin_post_task3(
        self, content_id: str, translation_result: Dict, voice_tag: str,
        tone: str, preview_mode: bool
    ) -> Dict[str, Any]:
        """Task 3: LinkedIn (Formatted post with title + summary + TTS)"""

        translated_text = translation_result["translated_text"]

        # Generate title and summary for LinkedIn
        title = self._generate_linkedin_title(translated_text, translation_result["target_language"])
        summary = self._generate_linkedin_summary(translated_text, translation_result["target_language"])
        formatted_content = self._format_linkedin_content(translated_text, translation_result["target_language"])

        return {
            "platform": "linkedin",
            "content_id": content_id,
            "post_type": "formatted_post_with_title_summary_tts",
            "title": title,
            "summary": summary,
            "text_content": formatted_content,
            "tts_audio": {
                "voice_tag": voice_tag,
                "full_audio_url": f"https://tts-audio.vaani-sentinel.com/{voice_tag}/{content_id}.mp3",
                "audio_duration": len(translated_text.split()) / 2.5,
                "transcript_available": True
            },
            "professional_hashtags": self._get_hashtags_for_language(translation_result["target_language"], "linkedin"),
            "professional_note": self._get_professional_note(translation_result["target_language"]),
            "character_count": len(formatted_content),
            "within_limits": len(formatted_content) <= 3000,
            "preview_mode": preview_mode,
            "posting_url": f"https://linkedin.com/posts/vaani-sentinel-{content_id}" if not preview_mode else None,
            "estimated_professional_reach": self._estimate_linkedin_reach(formatted_content, voice_tag)
        }

    def _generate_linkedin_title(self, content: str, language: str) -> str:
        """Generate LinkedIn-appropriate title"""

        # Extract key concept for title
        words = content.split()
        if len(words) <= 8:
            return content

        # Create title from first part
        title_words = words[:6]
        title = " ".join(title_words)

        if language == "hi":
            return f"💭 {title}..."
        elif language == "sa":
            return f"🕉️ {title}..."
        else:
            return f"💡 {title}..."

    def _generate_linkedin_summary(self, content: str, language: str) -> str:
        """Generate LinkedIn summary"""

        summary_templates = {
            "en": "Key insights on personal growth and wisdom.",
            "hi": "व्यक्तिगत विकास और ज्ञान पर मुख्य अंतर्दृष्टि।",
            "sa": "व्यक्तित्व विकास और ज्ञान विषयक मुख्य दृष्टिकोण।"
        }

        return summary_templates.get(language, summary_templates["en"])

    def _estimate_instagram_reach(self, content: str, voice_tag: str) -> Dict[str, int]:
        """Estimate Instagram reach"""
        import random

        base_reach = random.randint(500, 2000)
        voice_bonus = 1.2 if "devotional" in voice_tag else 1.0

        return {
            "estimated_reach": int(base_reach * voice_bonus),
            "estimated_likes": int(base_reach * 0.05 * voice_bonus),
            "estimated_comments": int(base_reach * 0.01 * voice_bonus),
            "estimated_shares": int(base_reach * 0.005 * voice_bonus)
        }

    def _estimate_twitter_engagement(self, content: str, voice_tag: str) -> Dict[str, int]:
        """Estimate Twitter engagement"""
        import random

        base_engagement = random.randint(100, 800)
        voice_bonus = 1.3 if "energetic" in voice_tag else 1.0

        return {
            "estimated_impressions": int(base_engagement * 10 * voice_bonus),
            "estimated_likes": int(base_engagement * voice_bonus),
            "estimated_retweets": int(base_engagement * 0.1 * voice_bonus),
            "estimated_replies": int(base_engagement * 0.05 * voice_bonus)
        }

    def _estimate_linkedin_reach(self, content: str, voice_tag: str) -> Dict[str, int]:
        """Estimate LinkedIn professional reach"""
        import random

        base_reach = random.randint(200, 1000)
        professional_bonus = 1.4 if "professional" in voice_tag else 1.0

        return {
            "estimated_views": int(base_reach * professional_bonus),
            "estimated_likes": int(base_reach * 0.08 * professional_bonus),
            "estimated_comments": int(base_reach * 0.03 * professional_bonus),
            "estimated_shares": int(base_reach * 0.02 * professional_bonus)
        }

    def _save_publishing_result(self, publishing_result: Dict[str, Any]):
        """Save publishing result to JSON file"""

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"platform_publishing_{publishing_result['publishing_id']}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(publishing_result, f, indent=2, ensure_ascii=False)

            print(f"Platform publishing result saved to: {filepath}")

        except Exception as e:
            print(f"Error saving publishing result: {e}")

# Global multilingual publisher simulator instance
multilingual_publisher_sim = MultilingualPublisherSimulator()

def get_multilingual_publisher_sim() -> MultilingualPublisherSimulator:
    """Get the global multilingual publisher simulator instance"""
    return multilingual_publisher_sim
