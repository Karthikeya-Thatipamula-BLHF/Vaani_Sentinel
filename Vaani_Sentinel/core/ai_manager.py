"""
AI Model Manager for Vaani Sentinel X
Handles free model selection, rate limiting, and fallback strategies
"""

import google.generativeai as genai
from groq import Groq
import time
import random
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
from core.config import settings
import json
import os

class AIModelManager:
    """Manages AI model selection and fallback strategies for free tiers"""
    
    def __init__(self):
        # Initialize clients
        genai.configure(api_key=settings.google_gemini_api_key)
        self.gemini_model = genai.GenerativeModel(settings.gemini_model)
        self.groq_client = Groq(api_key=settings.groq_api_key)
        
        # Rate limiting tracking
        self.rate_limits = {
            "groq": {"requests": 0, "reset_time": datetime.now(timezone.utc)},
            "gemini": {"requests": 0, "reset_time": datetime.now(timezone.utc)}
        }
        
        # Free tier limits (conservative estimates)
        self.limits = {
            "groq": {
                "requests_per_minute": 30,  # Conservative limit
                "requests_per_day": 14400,  # 14.4k per day
                "max_tokens": 8000
            },
            "gemini": {
                "requests_per_minute": 15,  # Conservative limit
                "requests_per_day": 1500,   # 1.5k per day for free tier
                "max_tokens": 8192
            }
        }
        
        # Model configurations
        self.model_configs = {
            "groq": {
                "primary": settings.groq_model,
                "fallback": settings.groq_fallback_model,
                "max_tokens": 4000,
                "temperature": 0.7
            },
            "gemini": {
                "model": settings.gemini_model,
                "max_tokens": 4000,
                "temperature": 0.7
            }
        }
    
    def _check_rate_limit(self, provider: str) -> bool:
        """Check if we're within rate limits for a provider"""
        now = datetime.now(timezone.utc)
        limit_info = self.rate_limits[provider]

        # Reset counters if a minute has passed
        if now - limit_info["reset_time"] > timedelta(minutes=1):
            limit_info["requests"] = 0
            limit_info["reset_time"] = now
        
        # Check if we're under the limit
        return limit_info["requests"] < self.limits[provider]["requests_per_minute"]
    
    def _increment_usage(self, provider: str):
        """Increment usage counter for a provider"""
        self.rate_limits[provider]["requests"] += 1
    
    def _get_optimal_provider(self, task_type: str = "general") -> str:
        """Get the optimal provider based on current conditions"""
        
        # Check primary provider availability
        if self._check_rate_limit(settings.primary_ai_provider):
            return settings.primary_ai_provider
        
        # Check fallback provider
        if self._check_rate_limit(settings.fallback_ai_provider):
            return settings.fallback_ai_provider
        
        # If both are rate limited, wait and use primary
        time.sleep(2)  # Brief wait
        return settings.primary_ai_provider
    
    def generate_content(
        self, 
        prompt: str, 
        max_tokens: int = 1000,
        temperature: float = 0.7,
        task_type: str = "general"
    ) -> Tuple[str, str]:
        """
        Generate content using the best available free model
        Returns: (generated_text, provider_used)
        """
        
        provider = self._get_optimal_provider(task_type)
        
        try:
            if provider == "groq":
                return self._generate_with_groq(prompt, max_tokens, temperature)
            else:
                return self._generate_with_gemini(prompt, max_tokens, temperature)
                
        except Exception as e:
            # Try fallback provider
            fallback_provider = "gemini" if provider == "groq" else "groq"
            print(f"Primary provider {provider} failed: {e}")
            print(f"Trying fallback provider: {fallback_provider}")
            
            try:
                if fallback_provider == "groq":
                    return self._generate_with_groq(prompt, max_tokens, temperature)
                else:
                    return self._generate_with_gemini(prompt, max_tokens, temperature)
            except Exception as fallback_error:
                raise Exception(f"Both providers failed. Primary: {e}, Fallback: {fallback_error}")
    
    def _generate_with_groq(
        self, 
        prompt: str, 
        max_tokens: int, 
        temperature: float
    ) -> Tuple[str, str]:
        """Generate content using Groq"""
        
        self._increment_usage("groq")
        
        # Try primary model first
        try:
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_configs["groq"]["primary"],
                max_tokens=min(max_tokens, self.model_configs["groq"]["max_tokens"]),
                temperature=temperature
            )
            return response.choices[0].message.content.strip(), f"groq-{self.model_configs['groq']['primary']}"
            
        except Exception as e:
            # Try fallback model
            print(f"Groq primary model failed: {e}")
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_configs["groq"]["fallback"],
                max_tokens=min(max_tokens, self.model_configs["groq"]["max_tokens"]),
                temperature=temperature
            )
            return response.choices[0].message.content.strip(), f"groq-{self.model_configs['groq']['fallback']}"
    
    def _generate_with_gemini(
        self, 
        prompt: str, 
        max_tokens: int, 
        temperature: float
    ) -> Tuple[str, str]:
        """Generate content using Gemini"""
        
        self._increment_usage("gemini")
        
        # Configure generation
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=min(max_tokens, self.model_configs["gemini"]["max_tokens"]),
            temperature=temperature
        )
        
        response = self.gemini_model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text.strip(), f"gemini-{self.model_configs['gemini']['model']}"
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        return {
            "rate_limits": self.rate_limits,
            "limits": self.limits,
            "current_time": datetime.now(timezone.utc).isoformat(),
            "primary_provider": settings.primary_ai_provider,
            "fallback_provider": settings.fallback_ai_provider
        }
    
    def optimize_for_task(self, task_type: str) -> str:
        """Get the best provider for a specific task type"""
        
        # Task-specific optimizations
        task_preferences = {
            "translation": "groq",  # Groq is faster for translations
            "content_generation": "groq",  # Groq is good for creative content
            "analysis": "gemini",  # Gemini is better for analysis
            "summarization": "groq",  # Groq is efficient for summaries
            "voice_script": "gemini",  # Gemini is good for natural speech
            "social_media": "groq"  # Groq is fast for social media content
        }
        
        preferred = task_preferences.get(task_type, settings.primary_ai_provider)
        
        # Check if preferred provider is available
        if self._check_rate_limit(preferred):
            return preferred
        else:
            # Return the other provider
            return "gemini" if preferred == "groq" else "groq"

# Global AI manager instance
ai_manager = AIModelManager()

def get_ai_manager() -> AIModelManager:
    """Get the global AI manager instance"""
    return ai_manager
