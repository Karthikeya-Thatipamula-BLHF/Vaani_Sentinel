"""
Agent B: AI Writer & Voice Synth Generator
Uses Gemini/Groq APIs to generate platform-specific content and TTS
"""

import os
import uuid
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from gtts import gTTS
import tempfile
from core.config import settings, PLATFORM_CONFIGS, TONE_CONFIGS
from core.ai_manager import get_ai_manager

# Using only FREE TTS solutions - no paid services
# ElevenLabs removed as per user requirement for FREE-only solutions
ELEVENLABS_AVAILABLE = False

class AIWriterVoiceGen:
    """Agent B: AI Writer & Voice Synth Generator"""
    
    def __init__(self):
        # Initialize AI manager
        self.ai_manager = get_ai_manager()

        # Using only FREE TTS solutions (gTTS)
        # No paid services as per user requirement
        self.elevenlabs_enabled = False

        # Content versioning
        self.version_counter = 1

        # Output directory
        self.output_dir = "./content/content_ready"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Platform-specific prompts
        self.platform_prompts = {
            "twitter": "Create a concise, engaging tweet (max 280 characters) that captures the essence of this content. Include 1-2 relevant hashtags.",
            "instagram": "Create an engaging Instagram post (1-2 paragraphs) with a compelling hook, valuable content, and 3-4 relevant hashtags.",
            "linkedin": "Create a professional LinkedIn post with a strong opening, valuable insights, and a call to action. Keep it professional yet engaging.",
            "voice_script": "Create a 20-30 second voice script that's natural to speak, engaging, and captures the key message. Use conversational tone."
        }
    
    def generate_content_for_platforms(
        self, 
        content_text: str, 
        content_id: str,
        platforms: List[str] = None,
        tone: str = "neutral",
        language: str = "en"
    ) -> Dict[str, Any]:
        """Generate content for multiple platforms"""
        
        if platforms is None:
            platforms = ["twitter", "instagram", "linkedin", "voice_script"]
        
        generated_content = {}
        voice_scripts = {}
        
        try:
            for platform in platforms:
                if platform == "voice_script":
                    # Generate voice script
                    script = self._generate_voice_script(content_text, tone, language)
                    voice_scripts[language] = script
                    generated_content[platform] = script
                else:
                    # Generate platform-specific content
                    platform_content = self._generate_platform_content(
                        content_text, platform, tone, language
                    )
                    generated_content[platform] = platform_content
            
            # Generate TTS for voice scripts
            tts_outputs = self._generate_tts_outputs(voice_scripts, content_id, tone)
            
            # Save versioned content
            version_data = {
                "content_id": content_id,
                "version": self.version_counter,
                "generated_content": generated_content,
                "voice_scripts": voice_scripts,
                "tts_outputs": tts_outputs,
                "metadata": {
                    "tone": tone,
                    "language": language,
                    "platforms": platforms,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            }
            
            self._save_versioned_content(version_data)
            self.version_counter += 1
            
            return version_data
            
        except Exception as e:
            raise Exception(f"Error generating content: {e}")
    
    def _generate_platform_content(
        self, 
        content_text: str, 
        platform: str, 
        tone: str,
        language: str
    ) -> str:
        """Generate content for specific platform"""
        
        platform_config = PLATFORM_CONFIGS.get(platform, {})
        tone_config = TONE_CONFIGS.get(tone, {})
        
        prompt = f"""
        {self.platform_prompts.get(platform, '')}
        
        Original content: {content_text}
        
        Platform: {platform}
        Tone: {tone} - {tone_config.get('description', '')}
        Language: {language}
        Max length: {platform_config.get('max_length', 500)} characters
        Max hashtags: {platform_config.get('hashtag_limit', 3)}
        
        Generate content that:
        1. Fits the platform's style and constraints
        2. Maintains the {tone} tone
        3. Is engaging and valuable
        4. Includes appropriate hashtags
        5. Is in {language} language
        
        Return only the generated content, no explanations.
        """
        
        try:
            # Use AI manager for optimal model selection
            generated_text, provider_used = self.ai_manager.generate_content(
                prompt=prompt,
                max_tokens=500,
                temperature=0.7,
                task_type="social_media"
            )
            return generated_text
        except Exception as e:
            raise Exception(f"AI content generation failed: {e}")
    
    def _generate_voice_script(
        self, 
        content_text: str, 
        tone: str,
        language: str
    ) -> str:
        """Generate voice script"""
        
        tone_config = TONE_CONFIGS.get(tone, {})
        
        prompt = f"""
        Create a natural, conversational voice script (20-30 seconds when spoken) based on this content:
        
        Content: {content_text}
        
        Requirements:
        - Tone: {tone} - {tone_config.get('description', '')}
        - Language: {language}
        - Natural speaking rhythm
        - Engaging and clear
        - 20-30 seconds duration when spoken
        - Easy to pronounce
        
        Return only the voice script, no explanations.
        """
        
        try:
            # Use AI manager for optimal model selection
            generated_text, provider_used = self.ai_manager.generate_content(
                prompt=prompt,
                max_tokens=300,
                temperature=0.8,
                task_type="voice_script"
            )
            return generated_text
        except Exception as e:
            raise Exception(f"Voice script generation failed: {e}")
    
    def _generate_tts_outputs(
        self, 
        voice_scripts: Dict[str, str], 
        content_id: str,
        tone: str
    ) -> List[Dict[str, Any]]:
        """Generate TTS outputs (simulation for now)"""
        
        tts_outputs = []
        
        for language, script in voice_scripts.items():
            # For now, simulate TTS generation
            # In production, integrate with actual TTS services
            
            voice_tag = self._get_voice_tag(language, tone)
            audio_filename = f"{content_id}_{language}_{tone}_{uuid.uuid4().hex[:8]}.mp3"
            audio_path = os.path.join(self.output_dir, "audio", audio_filename)
            
            # Create audio directory
            os.makedirs(os.path.dirname(audio_path), exist_ok=True)
            
            try:
                # Use FREE gTTS for all languages (no paid services)
                tts = gTTS(text=script, lang=language[:2] if len(language) > 2 else language, slow=False)
                tts.save(audio_path)

                # Calculate approximate duration
                word_count = len(script.split())
                duration = word_count / 2.5  # Approximate words per second
                
                tts_output = {
                    "content_id": content_id,
                    "language": language,
                    "voice_tag": voice_tag,
                    "tone": tone,
                    "audio_path": audio_path,
                    "duration": duration,
                    "script": script,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                
                tts_outputs.append(tts_output)
                
            except Exception as e:
                # If TTS fails, create simulation entry
                tts_output = {
                    "content_id": content_id,
                    "language": language,
                    "voice_tag": voice_tag,
                    "tone": tone,
                    "audio_path": f"simulated://{audio_filename}",
                    "duration": len(script.split()) / 2.5,
                    "script": script,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "error": str(e)
                }
                tts_outputs.append(tts_output)
        
        return tts_outputs
    
    def _get_voice_tag(self, language: str, tone: str) -> str:
        """Get appropriate voice tag for language and tone"""
        
        # Voice tag mapping based on language and tone
        voice_mapping = {
            "en": {
                "formal": "en_us_male_professional",
                "casual": "en_us_female_conversational",
                "devotional": "en_us_female_calm",
                "neutral": "en_us_neutral",
                "uplifting": "en_us_female_energetic"
            },
            "hi": {
                "formal": "hi_in_male_professional",
                "casual": "hi_in_female_conversational",
                "devotional": "hi_in_female_devotional",
                "neutral": "hi_in_neutral",
                "uplifting": "hi_in_female_energetic"
            },
            "sa": {
                "devotional": "sa_in_male_devotional",
                "formal": "sa_in_male_formal",
                "neutral": "sa_in_neutral"
            }
        }
        
        # Default fallback
        default_voice = f"{language}_neutral"
        
        return voice_mapping.get(language, {}).get(tone, default_voice)
    
    def _save_versioned_content(self, version_data: Dict[str, Any]):
        """Save versioned content to file"""
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"content_v{version_data['version']}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(version_data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def get_content_versions(self, content_id: str) -> List[Dict[str, Any]]:
        """Get all versions of content"""
        versions = []
        
        for filename in os.listdir(self.output_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.output_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if data.get('content_id') == content_id:
                            versions.append(data)
                except Exception:
                    continue
        
        return sorted(versions, key=lambda x: x.get('version', 0))

# Global AI writer instance
ai_writer = AIWriterVoiceGen()

def get_ai_writer() -> AIWriterVoiceGen:
    """Get the global AI writer instance"""
    return ai_writer
