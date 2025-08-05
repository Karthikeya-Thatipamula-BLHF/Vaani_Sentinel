"""
Agent F: Multilingual Content Pipeline
Handles language detection, routing, and multilingual processing
"""

from langdetect import detect, detect_langs
import uuid
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from core.config import settings, LANGUAGE_CONFIGS
from core.ai_manager import get_ai_manager

class LanguageDetector:
    """Language detection and routing"""
    
    def __init__(self):
        self.supported_languages = list(LANGUAGE_CONFIGS.keys())
        
        # Language family mappings for better routing
        self.language_families = {
            "indo_european": ["en", "hi", "sa", "mr", "gu", "de", "fr", "es", "it", "pt", "ru"],
            "dravidian": ["ta", "te", "kn", "ml"],
            "sino_tibetan": ["zh"],
            "japonic": ["ja"],
            "koreanic": ["ko"],
            "afroasiatic": ["ar"],
            "bengali": ["bn"]
        }
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """Detect language of text with confidence score"""
        try:
            # Use langdetect for primary detection
            detected_langs = detect_langs(text)
            
            if detected_langs:
                primary_lang = detected_langs[0]
                lang_code = primary_lang.lang
                confidence = primary_lang.prob
                
                # Map to supported languages
                mapped_lang = self._map_to_supported_language(lang_code)
                
                return mapped_lang, confidence
            else:
                return "en", 0.5  # Default fallback
                
        except Exception as e:
            print(f"Language detection error: {e}")
            return "en", 0.5  # Default fallback
    
    def _map_to_supported_language(self, detected_lang: str) -> str:
        """Map detected language to supported language"""
        
        # Direct mapping
        if detected_lang in self.supported_languages:
            return detected_lang
        
        # Common mappings
        language_mappings = {
            "hi": "hi",  # Hindi
            "sa": "sa",  # Sanskrit (might be detected as Hindi)
            "mr": "mr",  # Marathi
            "gu": "gu",  # Gujarati
            "ta": "ta",  # Tamil
            "te": "te",  # Telugu
            "kn": "kn",  # Kannada
            "ml": "ml",  # Malayalam
            "bn": "bn",  # Bengali
            "en": "en",  # English
            "de": "de",  # German
            "fr": "fr",  # French
            "es": "es",  # Spanish
            "it": "it",  # Italian
            "pt": "pt",  # Portuguese
            "ru": "ru",  # Russian
            "ja": "ja",  # Japanese
            "ko": "ko",  # Korean
            "zh": "zh",  # Chinese
            "ar": "ar",  # Arabic
        }
        
        return language_mappings.get(detected_lang, "en")
    
    def route_content_by_language(self, content: str, detected_lang: str) -> Dict[str, Any]:
        """Route content based on detected language"""
        
        language_config = LANGUAGE_CONFIGS.get(detected_lang, LANGUAGE_CONFIGS["en"])
        
        # Determine processing pipeline based on language family
        pipeline_type = "standard"
        
        if detected_lang in ["hi", "sa", "mr", "gu", "bn"]:
            pipeline_type = "indic"
        elif detected_lang in ["ta", "te", "kn", "ml"]:
            pipeline_type = "dravidian"
        elif detected_lang in ["zh", "ja", "ko"]:
            pipeline_type = "cjk"
        elif detected_lang == "ar":
            pipeline_type = "rtl"
        
        return {
            "language": detected_lang,
            "language_config": language_config,
            "pipeline_type": pipeline_type,
            "processing_notes": self._get_processing_notes(detected_lang),
            "content": content
        }
    
    def _get_processing_notes(self, language: str) -> List[str]:
        """Get language-specific processing notes"""
        
        notes = []
        
        if language in ["hi", "sa", "mr", "gu", "bn"]:
            notes.append("Devanagari script processing required")
            notes.append("Consider cultural context for religious content")
        
        if language in ["ta", "te", "kn", "ml"]:
            notes.append("Dravidian language family - unique script")
            notes.append("Regional cultural considerations")
        
        if language == "sa":
            notes.append("Sanskrit - classical language")
            notes.append("Spiritual/devotional context preferred")
        
        if language == "ar":
            notes.append("Right-to-left text direction")
            notes.append("Arabic script processing")
        
        if language in ["zh", "ja", "ko"]:
            notes.append("CJK character processing")
            notes.append("Cultural context important")
        
        return notes

class MultilingualContentPipeline:
    """Agent F: Multilingual Content Pipeline"""
    
    def __init__(self):
        # Initialize AI manager
        self.ai_manager = get_ai_manager()

        # Initialize language detector
        self.language_detector = LanguageDetector()
        
        # Output directory
        self.output_dir = "./content/multilingual_ready"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def process_multilingual_content(
        self,
        content: str,
        content_id: str,
        target_languages: List[str] = None,
        auto_detect: bool = True
    ) -> Dict[str, Any]:
        """Process content for multiple languages"""
        
        # Detect source language if auto_detect is enabled
        if auto_detect:
            source_lang, confidence = self.language_detector.detect_language(content)
        else:
            source_lang = "en"
            confidence = 1.0
        
        # Route content based on detected language
        routing_info = self.language_detector.route_content_by_language(content, source_lang)
        
        # Set target languages if not provided
        if target_languages is None:
            target_languages = ["en", "hi", "sa"]  # Default set
        
        # Process content for each target language
        processed_content = {
            "content_id": content_id,
            "source_language": source_lang,
            "source_confidence": confidence,
            "routing_info": routing_info,
            "target_languages": target_languages,
            "processed_languages": {},
            "metadata": {
                "processed_at": datetime.utcnow().isoformat(),
                "pipeline_version": "1.0"
            }
        }
        
        for target_lang in target_languages:
            try:
                lang_result = self._process_for_language(
                    content, 
                    source_lang, 
                    target_lang,
                    routing_info
                )
                processed_content["processed_languages"][target_lang] = lang_result
                
            except Exception as e:
                processed_content["processed_languages"][target_lang] = {
                    "error": str(e),
                    "status": "failed"
                }
        
        # Save processed content
        self._save_multilingual_content(processed_content)
        
        return processed_content
    
    def _process_for_language(
        self,
        content: str,
        source_lang: str,
        target_lang: str,
        routing_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process content for specific target language"""
        
        if source_lang == target_lang:
            # Same language - just format appropriately
            return {
                "content": content,
                "translation_needed": False,
                "cultural_adaptation": self._get_cultural_adaptation(content, target_lang),
                "processing_notes": routing_info["processing_notes"],
                "status": "processed"
            }
        else:
            # Different language - translate and adapt
            translated_content = self._translate_content(content, source_lang, target_lang)
            cultural_adaptation = self._get_cultural_adaptation(translated_content, target_lang)
            
            return {
                "content": translated_content,
                "translation_needed": True,
                "cultural_adaptation": cultural_adaptation,
                "processing_notes": routing_info["processing_notes"],
                "status": "processed"
            }
    
    def _translate_content(self, content: str, source_lang: str, target_lang: str) -> str:
        """Translate content between languages"""
        
        source_config = LANGUAGE_CONFIGS.get(source_lang, {})
        target_config = LANGUAGE_CONFIGS.get(target_lang, {})
        
        prompt = f"""
        Translate the following content from {source_config.get('name', source_lang)} to {target_config.get('name', target_lang)}.
        
        Source content: {content}
        
        Requirements:
        1. Maintain the original meaning and tone
        2. Adapt cultural references appropriately for {target_config.get('name', target_lang)} audience
        3. Keep the same emotional impact
        4. Use natural, fluent language
        5. Preserve any spiritual or devotional context if present
        
        Return only the translated content, no explanations.
        """
        
        try:
            # Use AI manager for optimal model selection
            translated_text, provider_used = self.ai_manager.generate_content(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.3,  # Lower temperature for more accurate translations
                task_type="translation"
            )
            return translated_text
        except Exception as e:
            raise Exception(f"Translation failed: {e}")
    
    def _get_cultural_adaptation(self, content: str, language: str) -> Dict[str, Any]:
        """Get cultural adaptation suggestions for content"""
        
        adaptations = {
            "suggestions": [],
            "cultural_notes": [],
            "tone_adjustments": []
        }
        
        if language in ["hi", "sa", "mr", "gu", "bn"]:
            adaptations["cultural_notes"].append("Consider Hindu/Indian cultural context")
            adaptations["suggestions"].append("Use respectful language for spiritual content")
            
            if language == "sa":
                adaptations["tone_adjustments"].append("Use classical, devotional tone")
                adaptations["suggestions"].append("Include traditional Sanskrit expressions")
        
        elif language in ["ta", "te", "kn", "ml"]:
            adaptations["cultural_notes"].append("South Indian cultural context")
            adaptations["suggestions"].append("Consider regional traditions and customs")
        
        elif language == "ar":
            adaptations["cultural_notes"].append("Islamic cultural context")
            adaptations["suggestions"].append("Use appropriate Islamic expressions")
            adaptations["tone_adjustments"].append("Respectful, formal tone")
        
        elif language in ["zh", "ja", "ko"]:
            adaptations["cultural_notes"].append("East Asian cultural context")
            adaptations["suggestions"].append("Consider hierarchical social structures")
            adaptations["tone_adjustments"].append("Respectful, harmonious tone")
        
        return adaptations
    
    def _save_multilingual_content(self, processed_content: Dict[str, Any]):
        """Save multilingual processed content"""
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"multilingual_{processed_content['content_id']}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(processed_content, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def get_supported_languages(self) -> Dict[str, Any]:
        """Get list of supported languages with details"""
        
        return {
            "supported_languages": list(LANGUAGE_CONFIGS.keys()),
            "language_details": LANGUAGE_CONFIGS,
            "total_count": len(LANGUAGE_CONFIGS),
            "language_families": self.language_detector.language_families
        }
    
    def get_language_statistics(self) -> Dict[str, Any]:
        """Get language processing statistics"""
        
        stats = {
            "total_processed": 0,
            "by_language": {},
            "by_pipeline_type": {},
            "recent_processing": []
        }
        
        # Read processed files to generate statistics
        if os.path.exists(self.output_dir):
            for filename in os.listdir(self.output_dir):
                if filename.endswith('.json'):
                    try:
                        filepath = os.path.join(self.output_dir, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        stats["total_processed"] += 1
                        
                        # Count by language
                        for lang in data.get("processed_languages", {}):
                            stats["by_language"][lang] = stats["by_language"].get(lang, 0) + 1
                        
                        # Count by pipeline type
                        pipeline_type = data.get("routing_info", {}).get("pipeline_type", "unknown")
                        stats["by_pipeline_type"][pipeline_type] = stats["by_pipeline_type"].get(pipeline_type, 0) + 1
                        
                        # Add to recent processing
                        stats["recent_processing"].append({
                            "content_id": data.get("content_id"),
                            "source_language": data.get("source_language"),
                            "target_languages": data.get("target_languages"),
                            "processed_at": data.get("metadata", {}).get("processed_at")
                        })
                        
                    except Exception:
                        continue
        
        # Sort recent processing by date
        stats["recent_processing"] = sorted(
            stats["recent_processing"][-20:],  # Last 20 items
            key=lambda x: x.get("processed_at", ""),
            reverse=True
        )
        
        return stats

# Global multilingual pipeline instance
multilingual_pipeline = MultilingualContentPipeline()

def get_multilingual_pipeline() -> MultilingualContentPipeline:
    """Get the global multilingual pipeline instance"""
    return multilingual_pipeline
