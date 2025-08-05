"""
Personalization Agent for Vaani Sentinel X
Reads user profiles and modifies content tone based on preferences
Task 5 Component 2: Personalization Agent
"""

import json
import os
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from core.ai_manager import get_ai_manager

class PersonalizationAgent:
    """
    Personalization agent that adapts content tone based on user preferences
    Uses prompt engineering with LLM to simulate tone variations
    """
    
    def __init__(self):
        self.ai_manager = get_ai_manager()
        self.output_dir = "./data"
        self.config_dir = "./config"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load user profiles
        self.user_profiles = self._load_user_profiles()
        
        # Tone adaptation templates
        self.tone_templates = {
            "formal": {
                "description": "Professional, respectful, structured language",
                "keywords": ["professional", "respectful", "structured", "formal"],
                "style_guide": "Use formal language, avoid contractions, maintain professional tone"
            },
            "casual": {
                "description": "Friendly, conversational, approachable language",
                "keywords": ["friendly", "conversational", "relaxed", "approachable"],
                "style_guide": "Use casual language, contractions are fine, be conversational"
            },
            "devotional": {
                "description": "Spiritual, reverent, peaceful language",
                "keywords": ["spiritual", "reverent", "peaceful", "sacred"],
                "style_guide": "Use reverent language, include spiritual context, maintain peaceful tone"
            },
            "uplifting": {
                "description": "Motivational, positive, energetic language",
                "keywords": ["motivational", "positive", "energetic", "inspiring"],
                "style_guide": "Use inspiring language, focus on positivity, be motivational"
            },
            "neutral": {
                "description": "Balanced, informative, clear language",
                "keywords": ["balanced", "informative", "clear", "objective"],
                "style_guide": "Use clear language, remain objective, provide information"
            }
        }
    
    def _load_user_profiles(self) -> Dict[str, Any]:
        """Load user profiles from JSON file"""

        profiles_path = os.path.join(self.config_dir, "user_profiles.json")

        try:
            if os.path.exists(profiles_path):
                with open(profiles_path, 'r', encoding='utf-8') as f:
                    existing_profiles = json.load(f)

                # Check if it has the expected structure
                if "user_profiles" in existing_profiles:
                    return existing_profiles
                else:
                    # Convert existing structure to expected format
                    converted_profiles = self._convert_profile_structure(existing_profiles)
                    self._save_user_profiles(converted_profiles)
                    return converted_profiles
            else:
                # Create default user profiles if file doesn't exist
                default_profiles = self._create_default_profiles()
                self._save_user_profiles(default_profiles)
                return default_profiles

        except Exception as e:
            print(f"Error loading user profiles: {e}")
            return self._create_default_profiles()

    def _convert_profile_structure(self, existing_profiles: Dict[str, Any]) -> Dict[str, Any]:
        """Convert existing profile structure to expected format"""

        converted = {"user_profiles": {}}

        # Convert profile templates to user profiles
        if "profile_templates" in existing_profiles:
            for template_id, template in existing_profiles["profile_templates"].items():
                converted["user_profiles"][template_id] = {
                    "name": template_id.replace("_", " ").title(),
                    "preferred_tone": self._get_preferred_tone(template.get("tone_preferences", {})),
                    "language_preferences": template.get("preferred_languages", ["en"]),
                    "content_preferences": self._convert_content_interests(template.get("content_interests", [])),
                    "tone_adjustments": self._convert_tone_preferences(template.get("tone_preferences", {}))
                }

        # Add default profiles if none exist
        if not converted["user_profiles"]:
            return self._create_default_profiles()

        return converted

    def _get_preferred_tone(self, tone_preferences: Dict[str, float]) -> str:
        """Get the most preferred tone from preferences"""
        if not tone_preferences:
            return "neutral"

        return max(tone_preferences.items(), key=lambda x: x[1])[0]

    def _convert_content_interests(self, interests: List[str]) -> Dict[str, float]:
        """Convert content interests to preference scores"""

        content_map = {
            "spirituality": "spiritual_content",
            "meditation": "spiritual_content",
            "philosophy": "spiritual_content",
            "business": "educational_content",
            "technology": "educational_content",
            "education": "educational_content",
            "leadership": "motivational_content",
            "entertainment": "motivational_content"
        }

        preferences = {
            "spiritual_content": 0.5,
            "educational_content": 0.5,
            "motivational_content": 0.5
        }

        for interest in interests:
            content_type = content_map.get(interest, "educational_content")
            preferences[content_type] = min(1.0, preferences[content_type] + 0.2)

        return preferences

    def _convert_tone_preferences(self, tone_preferences: Dict[str, float]) -> Dict[str, float]:
        """Convert tone preferences to adjustment values"""

        # Calculate formality level based on formal vs casual preferences
        formal_score = tone_preferences.get("formal", 0.5)
        casual_score = tone_preferences.get("casual", 0.5)
        formality_level = formal_score / (formal_score + casual_score) if (formal_score + casual_score) > 0 else 0.5

        # Calculate spiritual context based on devotional preferences
        spiritual_context = tone_preferences.get("devotional", 0.5)

        return {
            "formality_level": formality_level,
            "spiritual_context": spiritual_context,
            "cultural_sensitivity": 0.6  # Default value
        }
    
    def _create_default_profiles(self) -> Dict[str, Any]:
        """Create default user profiles"""
        
        return {
            "user_profiles": {
                "spiritual_seeker": {
                    "name": "Spiritual Seeker",
                    "preferred_tone": "devotional",
                    "language_preferences": ["hi", "sa", "en"],
                    "content_preferences": {
                        "spiritual_content": 0.9,
                        "motivational_content": 0.7,
                        "educational_content": 0.6
                    },
                    "tone_adjustments": {
                        "formality_level": 0.7,
                        "spiritual_context": 0.9,
                        "cultural_sensitivity": 0.8
                    }
                },
                "professional": {
                    "name": "Professional",
                    "preferred_tone": "formal",
                    "language_preferences": ["en", "hi"],
                    "content_preferences": {
                        "educational_content": 0.9,
                        "motivational_content": 0.8,
                        "spiritual_content": 0.3
                    },
                    "tone_adjustments": {
                        "formality_level": 0.9,
                        "spiritual_context": 0.2,
                        "cultural_sensitivity": 0.6
                    }
                },
                "youth": {
                    "name": "Youth",
                    "preferred_tone": "casual",
                    "language_preferences": ["en", "hi"],
                    "content_preferences": {
                        "motivational_content": 0.9,
                        "educational_content": 0.7,
                        "spiritual_content": 0.4
                    },
                    "tone_adjustments": {
                        "formality_level": 0.3,
                        "spiritual_context": 0.4,
                        "cultural_sensitivity": 0.5
                    }
                },
                "general": {
                    "name": "General Audience",
                    "preferred_tone": "neutral",
                    "language_preferences": ["en", "hi"],
                    "content_preferences": {
                        "educational_content": 0.7,
                        "motivational_content": 0.7,
                        "spiritual_content": 0.5
                    },
                    "tone_adjustments": {
                        "formality_level": 0.5,
                        "spiritual_context": 0.5,
                        "cultural_sensitivity": 0.6
                    }
                }
            }
        }
    
    def _save_user_profiles(self, profiles: Dict[str, Any]):
        """Save user profiles to JSON file"""
        
        profiles_path = os.path.join(self.config_dir, "user_profiles.json")
        
        try:
            with open(profiles_path, 'w', encoding='utf-8') as f:
                json.dump(profiles, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving user profiles: {e}")
    
    def personalize_content(
        self,
        content_text: str,
        user_profile_id: str = "general",
        target_tone: str = None,
        content_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Personalize content based on user profile and preferences
        
        Args:
            content_text: Original content text
            user_profile_id: User profile identifier
            target_tone: Override tone (optional)
            content_metadata: Additional content metadata
            
        Returns:
            Personalized content with tone variations
        """
        
        personalization_id = str(uuid.uuid4())
        
        # Get user profile
        user_profiles_dict = self.user_profiles.get("user_profiles", {})
        user_profile = user_profiles_dict.get(user_profile_id, {})

        if not user_profile:
            # Try to get a default profile or create one
            if "general" in user_profiles_dict:
                user_profile = user_profiles_dict["general"]
            elif user_profiles_dict:
                # Use the first available profile as fallback
                user_profile = list(user_profiles_dict.values())[0]
            else:
                # Create a minimal default profile
                user_profile = {
                    "name": "Default User",
                    "preferred_tone": target_tone or "neutral",
                    "language_preferences": ["en"],
                    "content_preferences": {"educational_content": 0.7},
                    "tone_adjustments": {"formality_level": 0.5, "spiritual_context": 0.5, "cultural_sensitivity": 0.6}
                }
        
        # Determine target tone
        if target_tone is None:
            target_tone = user_profile.get("preferred_tone", "neutral")
        
        # Generate personalized content
        personalized_result = {
            "personalization_id": personalization_id,
            "original_content": content_text,
            "user_profile_id": user_profile_id,
            "user_profile": user_profile,
            "target_tone": target_tone,
            "personalized_content": {},
            "metadata": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "agent": "personalization_agent",
                "version": "1.0",
                "content_metadata": content_metadata or {}
            }
        }
        
        try:
            # Generate tone-adapted content
            adapted_content = self._adapt_content_tone(
                content_text, target_tone, user_profile, content_metadata
            )
            
            personalized_result["personalized_content"] = adapted_content
            personalized_result["status"] = "success"
            
        except Exception as e:
            personalized_result["personalized_content"] = {
                "adapted_text": content_text,  # Fallback to original
                "tone_confidence": 0.0,
                "adaptation_notes": [],
                "error": str(e)
            }
            personalized_result["status"] = "error"
        
        # Save personalization results
        self._save_personalization_results(personalized_result)
        
        return personalized_result
    
    def _adapt_content_tone(
        self,
        content_text: str,
        target_tone: str,
        user_profile: Dict[str, Any],
        content_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Adapt content tone using LLM prompt engineering"""
        
        tone_template = self.tone_templates.get(target_tone, self.tone_templates["neutral"])
        tone_adjustments = user_profile.get("tone_adjustments", {})
        
        # Build personalization prompt
        prompt = f"""
        Adapt the following content to match the specified tone and user preferences.
        
        Original content: {content_text}
        
        Target tone: {target_tone}
        Tone description: {tone_template['description']}
        Style guide: {tone_template['style_guide']}
        
        User preferences:
        - Formality level: {tone_adjustments.get('formality_level', 0.5)} (0=very casual, 1=very formal)
        - Spiritual context: {tone_adjustments.get('spiritual_context', 0.5)} (0=secular, 1=highly spiritual)
        - Cultural sensitivity: {tone_adjustments.get('cultural_sensitivity', 0.5)} (0=universal, 1=culturally specific)
        
        Content type: {content_metadata.get('content_type', 'general') if content_metadata else 'general'}
        
        Requirements:
        1. Maintain the core message and meaning
        2. Adapt the tone to match {target_tone} style
        3. Consider user's formality preferences
        4. Adjust spiritual/cultural context as needed
        5. Keep the content engaging and authentic
        6. Preserve any important keywords or concepts
        
        Provide ONLY the adapted content, no explanations.
        """
        
        try:
            # Use AI manager for tone adaptation
            adapted_text, provider_used = self.ai_manager.generate_content(
                prompt=prompt,
                max_tokens=800,
                temperature=0.7,  # Moderate creativity for tone adaptation
                task_type="content_generation"
            )
            
            # Calculate tone confidence
            tone_confidence = self._calculate_tone_confidence(
                content_text, adapted_text, target_tone, user_profile
            )
            
            # Generate adaptation notes
            adaptation_notes = self._generate_adaptation_notes(
                content_text, adapted_text, target_tone, tone_confidence
            )
            
            return {
                "adapted_text": adapted_text.strip(),
                "tone_confidence": tone_confidence,
                "adaptation_notes": adaptation_notes,
                "provider_used": provider_used,
                "target_tone": target_tone,
                "user_preferences_applied": tone_adjustments
            }
            
        except Exception as e:
            raise Exception(f"Tone adaptation failed: {e}")
    
    def _calculate_tone_confidence(
        self,
        original_text: str,
        adapted_text: str,
        target_tone: str,
        user_profile: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for tone adaptation"""
        
        confidence = 0.6  # Base confidence
        
        # Check if content was actually adapted
        if adapted_text != original_text:
            confidence += 0.2
        
        # Check length appropriateness
        length_ratio = len(adapted_text) / len(original_text) if len(original_text) > 0 else 1.0
        if 0.7 <= length_ratio <= 1.5:
            confidence += 0.1
        
        # Tone-specific checks
        tone_keywords = self.tone_templates.get(target_tone, {}).get("keywords", [])
        adapted_lower = adapted_text.lower()
        
        keyword_matches = sum(1 for keyword in tone_keywords if keyword in adapted_lower)
        if keyword_matches > 0:
            confidence += min(0.1, keyword_matches * 0.02)
        
        # Ensure confidence is between 0 and 1
        return max(0.0, min(1.0, confidence))
    
    def _generate_adaptation_notes(
        self,
        original_text: str,
        adapted_text: str,
        target_tone: str,
        confidence: float
    ) -> List[str]:
        """Generate notes about the adaptation process"""
        
        notes = []
        
        if confidence >= 0.8:
            notes.append(f"High-quality {target_tone} tone adaptation achieved")
        elif confidence >= 0.6:
            notes.append(f"Good {target_tone} tone adaptation with minor adjustments")
        else:
            notes.append(f"Basic {target_tone} tone adaptation - may need manual review")
        
        # Length comparison
        length_change = len(adapted_text) - len(original_text)
        if abs(length_change) > len(original_text) * 0.3:
            notes.append(f"Significant length change: {length_change:+d} characters")
        
        return notes
    
    def _save_personalization_results(self, results: Dict[str, Any]):
        """Save personalization results to JSON file"""
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"personalized_content_{results['personalization_id']}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"Personalization results saved to: {filepath}")
            
        except Exception as e:
            print(f"Error saving personalization results: {e}")
    
    def get_user_profiles(self) -> Dict[str, Any]:
        """Get all user profiles"""
        return self.user_profiles.copy()
    
    def get_available_tones(self) -> Dict[str, str]:
        """Get available tone options"""
        return {tone: template["description"] for tone, template in self.tone_templates.items()}

# Global personalization agent instance
personalization_agent = PersonalizationAgent()

def get_personalization_agent() -> PersonalizationAgent:
    """Get the global personalization agent instance"""
    return personalization_agent
