"""
TTS Simulator for Vaani Sentinel X
Creates TTS simulation output with language, tone, voice_tag, and dummy audio paths
Task 5 Component 4: TTS Simulation Layer
"""

import json
import os
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

class TTSSimulator:
    """
    TTS Simulation Layer that creates simulation output JSON
    Does not generate actual audio yet, but provides complete metadata
    """
    
    def __init__(self):
        self.output_dir = "./data"
        self.config_dir = "./config"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load voice mapping configuration
        self.voice_mapping = self._load_voice_mapping()
        
        # Audio format configurations
        self.audio_formats = {
            "mp3": {"extension": ".mp3", "quality": "standard"},
            "wav": {"extension": ".wav", "quality": "high"},
            "ogg": {"extension": ".ogg", "quality": "compressed"}
        }
        
        # Default audio settings
        self.default_settings = {
            "sample_rate": 22050,
            "bit_rate": 128,
            "format": "mp3",
            "duration_estimate_wps": 2.5  # words per second
        }
    
    def _load_voice_mapping(self) -> Dict[str, Any]:
        """Load voice mapping configuration"""
        
        voice_map_path = os.path.join(self.config_dir, "language_voice_map.json")
        
        try:
            if os.path.exists(voice_map_path):
                with open(voice_map_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._create_default_voice_mapping()
                
        except Exception as e:
            print(f"Error loading voice mapping: {e}")
            return self._create_default_voice_mapping()
    
    def _create_default_voice_mapping(self) -> Dict[str, Any]:
        """Create default voice mapping if file doesn't exist"""
        
        return {
            "language_voice_mapping": {
                "en": {
                    "formal": {"voice_tag": "en_us_male_professional"},
                    "casual": {"voice_tag": "en_us_female_conversational"},
                    "devotional": {"voice_tag": "en_us_female_calm"},
                    "neutral": {"voice_tag": "en_us_neutral"},
                    "uplifting": {"voice_tag": "en_us_female_energetic"}
                },
                "hi": {
                    "formal": {"voice_tag": "hi_in_male_professional"},
                    "casual": {"voice_tag": "hi_in_female_conversational"},
                    "devotional": {"voice_tag": "hi_in_female_devotional"},
                    "neutral": {"voice_tag": "hi_in_neutral"},
                    "uplifting": {"voice_tag": "hi_in_female_energetic"}
                }
            },
            "fallback_voices": {
                "default_male": "en_us_male_professional",
                "default_female": "en_us_female_conversational",
                "default_neutral": "en_us_neutral"
            }
        }
    
    def simulate_tts_generation(
        self,
        content_text: str,
        language: str = "en",
        tone: str = "neutral",
        content_id: str = None,
        voice_tag_override: str = None
    ) -> Dict[str, Any]:
        """
        Simulate TTS generation and create simulation output JSON
        
        Args:
            content_text: Text to convert to speech
            language: Language code
            tone: Tone/style for voice selection
            content_id: Content identifier
            voice_tag_override: Override automatic voice selection
            
        Returns:
            TTS simulation output with metadata
        """
        
        simulation_id = str(uuid.uuid4())
        if content_id is None:
            content_id = simulation_id
        
        # Select appropriate voice tag
        voice_tag = self._select_voice_tag(language, tone, voice_tag_override)
        
        # Generate dummy audio path
        audio_path = self._generate_dummy_audio_path(content_id, language, tone, voice_tag)
        
        # Calculate estimated duration
        estimated_duration = self._estimate_audio_duration(content_text)
        
        # Create simulation output
        tts_simulation = {
            "simulation_id": simulation_id,
            "content_id": content_id,
            "language": language,
            "tone": tone,
            "voice_tag": voice_tag,
            "content_text": content_text,
            "audio_output": {
                "dummy_audio_url": f"https://api.vaani-sentinel.com/audio/{audio_path}",
                "dummy_audio_path": f"./audio/{audio_path}",
                "file_format": self.default_settings["format"],
                "estimated_duration": estimated_duration,
                "estimated_file_size": self._estimate_file_size(estimated_duration),
                "sample_rate": self.default_settings["sample_rate"],
                "bit_rate": self.default_settings["bit_rate"]
            },
            "voice_metadata": {
                "voice_tag": voice_tag,
                "language": language,
                "tone": tone,
                "voice_description": self._get_voice_description(voice_tag, language, tone),
                "fallback_used": voice_tag_override is None and self._is_fallback_voice(voice_tag)
            },
            "simulation_metadata": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "agent": "tts_simulator",
                "version": "1.0",
                "simulation_mode": True,
                "actual_audio_generated": False
            }
        }
        
        # Save simulation output
        self._save_tts_simulation_output(tts_simulation)
        
        return tts_simulation
    
    def _select_voice_tag(
        self,
        language: str,
        tone: str,
        voice_tag_override: str = None
    ) -> str:
        """Select appropriate voice tag based on language and tone"""
        
        if voice_tag_override:
            return voice_tag_override
        
        # Get language voice mapping
        language_voices = self.voice_mapping.get("language_voice_mapping", {}).get(language, {})
        
        # Try to get tone-specific voice
        tone_voice = language_voices.get(tone, {})
        if tone_voice and "voice_tag" in tone_voice:
            return tone_voice["voice_tag"]
        
        # Fallback to neutral tone for the language
        neutral_voice = language_voices.get("neutral", {})
        if neutral_voice and "voice_tag" in neutral_voice:
            return neutral_voice["voice_tag"]
        
        # Fallback to default voices
        fallback_voices = self.voice_mapping.get("fallback_voices", {})
        
        if tone == "formal":
            return fallback_voices.get("default_male", "en_us_male_professional")
        elif tone in ["casual", "uplifting"]:
            return fallback_voices.get("default_female", "en_us_female_conversational")
        else:
            return fallback_voices.get("default_neutral", "en_us_neutral")
    
    def _generate_dummy_audio_path(
        self,
        content_id: str,
        language: str,
        tone: str,
        voice_tag: str
    ) -> str:
        """Generate dummy audio file path"""
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        file_extension = self.audio_formats[self.default_settings["format"]]["extension"]
        
        filename = f"{content_id}_{language}_{tone}_{voice_tag}_{timestamp}{file_extension}"
        return filename
    
    def _estimate_audio_duration(self, content_text: str) -> float:
        """Estimate audio duration based on text length"""
        
        word_count = len(content_text.split())
        duration = word_count / self.default_settings["duration_estimate_wps"]
        
        # Add some padding for natural speech patterns
        duration *= 1.1
        
        return round(duration, 2)
    
    def _estimate_file_size(self, duration: float) -> int:
        """Estimate audio file size in bytes"""
        
        # Rough calculation based on bit rate and duration
        bit_rate = self.default_settings["bit_rate"]  # kbps
        file_size_kb = (bit_rate * duration) / 8  # Convert to KB
        file_size_bytes = int(file_size_kb * 1024)  # Convert to bytes
        
        return file_size_bytes
    
    def _get_voice_description(self, voice_tag: str, language: str, tone: str) -> str:
        """Get description for the selected voice"""
        
        language_voices = self.voice_mapping.get("language_voice_mapping", {}).get(language, {})
        tone_voice = language_voices.get(tone, {})
        
        if "description" in tone_voice:
            return tone_voice["description"]
        
        # Generate default description
        lang_name = {"en": "English", "hi": "Hindi", "sa": "Sanskrit"}.get(language, language.upper())
        return f"{lang_name} {tone} voice ({voice_tag})"
    
    def _is_fallback_voice(self, voice_tag: str) -> bool:
        """Check if the selected voice is a fallback voice"""
        
        fallback_voices = self.voice_mapping.get("fallback_voices", {})
        return voice_tag in fallback_voices.values()
    
    def _save_tts_simulation_output(self, simulation_output: Dict[str, Any]):
        """Save TTS simulation output to JSON file"""
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"tts_simulation_output_{simulation_output['simulation_id']}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(simulation_output, f, indent=2, ensure_ascii=False)
            
            print(f"TTS simulation output saved to: {filepath}")
            
        except Exception as e:
            print(f"Error saving TTS simulation output: {e}")
    
    def batch_simulate_tts(
        self,
        content_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Batch simulate TTS for multiple content items"""
        
        results = []
        
        for content_item in content_list:
            content_text = content_item.get("text", "")
            language = content_item.get("language", "en")
            tone = content_item.get("tone", "neutral")
            content_id = content_item.get("content_id")
            
            if content_text:
                simulation_result = self.simulate_tts_generation(
                    content_text=content_text,
                    language=language,
                    tone=tone,
                    content_id=content_id
                )
                results.append(simulation_result)
        
        return results
    
    def get_available_voices(self, language: str = None) -> Dict[str, Any]:
        """Get available voices for a language or all languages"""
        
        if language:
            return self.voice_mapping.get("language_voice_mapping", {}).get(language, {})
        else:
            return self.voice_mapping.get("language_voice_mapping", {})
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        
        return list(self.voice_mapping.get("language_voice_mapping", {}).keys())

# Global TTS simulator instance
tts_simulator = TTSSimulator()

def get_tts_simulator() -> TTSSimulator:
    """Get the global TTS simulator instance"""
    return tts_simulator
