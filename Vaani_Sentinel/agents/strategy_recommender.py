"""
Strategy Recommender for Vaani Sentinel X
Task 3 Loop Hook: Adaptive Improvement Trigger

Creates adjust_future_content_strategy() function that:
- Reads top 3 performers of the week
- Suggests content formats (e.g., more devotional tone on LinkedIn)
- Connects to future reinforcement learning in Task 5
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from agents.analytics_collector import get_analytics_collector

class StrategyRecommender:
    """
    Task 3 Loop Hook: Adaptive Improvement Trigger
    
    Analyzes performance data and suggests content strategy adjustments
    to create an adaptive loop for the Sanatan AI Engine
    """
    
    def __init__(self):
        self.analytics_collector = get_analytics_collector()
        self.output_dir = "./data"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Strategy templates for different scenarios
        self.strategy_templates = {
            "high_engagement_devotional": {
                "recommendation": "Increase devotional content",
                "platforms": ["instagram", "linkedin"],
                "voice_preferences": ["devotional", "calm"],
                "languages": ["hi", "sa", "en"],
                "content_types": ["spiritual", "inspirational"]
            },
            "professional_linkedin_success": {
                "recommendation": "Focus on professional content for LinkedIn",
                "platforms": ["linkedin"],
                "voice_preferences": ["professional", "authoritative"],
                "languages": ["en", "hi"],
                "content_types": ["educational", "leadership"]
            },
            "social_media_viral": {
                "recommendation": "Optimize for social media virality",
                "platforms": ["twitter", "instagram"],
                "voice_preferences": ["energetic", "conversational"],
                "languages": ["en", "hi"],
                "content_types": ["motivational", "trending"]
            }
        }
    
    def adjust_future_content_strategy(self, analysis_days: int = 7) -> Dict[str, Any]:
        """
        Task 3 Loop Hook: Main function to adjust future content strategy
        
        Args:
            analysis_days: Number of days to analyze for strategy adjustment
            
        Returns:
            Strategy recommendations for future content creation
        """
        
        strategy_id = f"strategy_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Step 1: Read top 3 performers of the week
        top_performers = self._get_top_performers(analysis_days)
        
        # Step 2: Analyze performance patterns
        performance_patterns = self._analyze_performance_patterns(top_performers)
        
        # Step 3: Generate strategy recommendations
        strategy_recommendations = self._generate_strategy_recommendations(performance_patterns)
        
        # Step 4: Create adaptive strategy output
        adaptive_strategy = {
            "strategy_id": strategy_id,
            "analysis_period": f"Last {analysis_days} days",
            "top_performers": top_performers,
            "performance_patterns": performance_patterns,
            "strategy_recommendations": strategy_recommendations,
            "adaptive_adjustments": self._create_adaptive_adjustments(performance_patterns),
            "future_content_guidance": self._generate_future_content_guidance(strategy_recommendations),
            "reinforcement_learning_signals": self._prepare_rl_signals(performance_patterns),
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "agent": "task3_strategy_recommender",
                "version": "1.0",
                "connects_to": "task5_reinforcement_learning"
            }
        }
        
        # Save strategy recommendations
        self._save_strategy_recommendations(adaptive_strategy)
        
        return adaptive_strategy
    
    def _get_top_performers(self, days: int) -> List[Dict[str, Any]]:
        """Get top 3 performing posts from the specified period"""
        
        analytics_db_file = os.path.join(self.analytics_collector.analytics_db_path, "post_metrics.json")
        
        if not os.path.exists(analytics_db_file):
            return []
        
        try:
            with open(analytics_db_file, 'r', encoding='utf-8') as f:
                analytics_db = json.load(f)
        except Exception:
            return []
        
        posts = analytics_db.get("posts", [])
        
        # Filter posts from last N days
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_posts = [
            post for post in posts 
            if datetime.fromisoformat(post["timestamp"]) >= cutoff_date
        ]
        
        # Sort by engagement rate and get top 3
        top_performers = sorted(
            recent_posts,
            key=lambda x: x.get("engagement_rate", 0),
            reverse=True
        )[:3]
        
        return top_performers
    
    def _analyze_performance_patterns(self, top_performers: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in top-performing content"""
        
        if not top_performers:
            return {"error": "No top performers to analyze"}
        
        patterns = {
            "successful_platforms": {},
            "successful_languages": {},
            "successful_tones": {},
            "successful_voice_tags": {},
            "content_characteristics": {},
            "engagement_trends": []
        }
        
        for post in top_performers:
            # Platform patterns
            platform = post.get("platform", "unknown")
            patterns["successful_platforms"][platform] = patterns["successful_platforms"].get(platform, 0) + 1
            
            # Language patterns
            language = post.get("language", "unknown")
            patterns["successful_languages"][language] = patterns["successful_languages"].get(language, 0) + 1
            
            # Tone patterns
            tone = post.get("tone", "unknown")
            patterns["successful_tones"][tone] = patterns["successful_tones"].get(tone, 0) + 1
            
            # Voice patterns
            voice_tag = post.get("voice_tag", "unknown")
            patterns["successful_voice_tags"][voice_tag] = patterns["successful_voice_tags"].get(voice_tag, 0) + 1
            
            # Engagement trends
            patterns["engagement_trends"].append({
                "content_id": post.get("content_id"),
                "engagement_rate": post.get("engagement_rate", 0),
                "platform": platform,
                "language": language,
                "tone": tone
            })
        
        # Calculate success rates
        total_posts = len(top_performers)
        patterns["success_rates"] = {
            "platforms": {k: v/total_posts for k, v in patterns["successful_platforms"].items()},
            "languages": {k: v/total_posts for k, v in patterns["successful_languages"].items()},
            "tones": {k: v/total_posts for k, v in patterns["successful_tones"].items()}
        }
        
        return patterns
    
    def _generate_strategy_recommendations(self, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific strategy recommendations based on patterns"""
        
        recommendations = []
        
        if "error" in patterns:
            return [{"type": "default", "recommendation": "Continue current strategy and gather more data"}]
        
        success_rates = patterns.get("success_rates", {})
        
        # Platform recommendations
        if success_rates.get("platforms"):
            best_platform = max(success_rates["platforms"].items(), key=lambda x: x[1])
            recommendations.append({
                "type": "platform_focus",
                "recommendation": f"Increase content allocation to {best_platform[0]}",
                "confidence": best_platform[1],
                "details": f"{best_platform[0]} shows {best_platform[1]:.1%} success rate in top performers"
            })
        
        # Language recommendations
        if success_rates.get("languages"):
            best_language = max(success_rates["languages"].items(), key=lambda x: x[1])
            recommendations.append({
                "type": "language_optimization",
                "recommendation": f"Prioritize content in {best_language[0]} language",
                "confidence": best_language[1],
                "details": f"{best_language[0]} language content performs well"
            })
        
        # Tone recommendations
        if success_rates.get("tones"):
            best_tone = max(success_rates["tones"].items(), key=lambda x: x[1])
            recommendations.append({
                "type": "tone_adjustment",
                "recommendation": f"Use {best_tone[0]} tone more frequently",
                "confidence": best_tone[1],
                "details": f"{best_tone[0]} tone shows strong engagement"
            })
        
        # Cross-platform strategy
        platform_success = success_rates.get("platforms", {})
        if "linkedin" in platform_success and platform_success["linkedin"] > 0.5:
            recommendations.append({
                "type": "platform_specific",
                "recommendation": "Develop LinkedIn-specific professional content strategy",
                "confidence": platform_success["linkedin"],
                "details": "LinkedIn shows strong performance - focus on professional, educational content"
            })
        
        return recommendations
    
    def _create_adaptive_adjustments(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Create specific adaptive adjustments for content creation"""
        
        adjustments = {
            "content_distribution": {},
            "voice_selection": {},
            "platform_optimization": {},
            "language_prioritization": {}
        }
        
        if "error" in patterns:
            return adjustments
        
        success_rates = patterns.get("success_rates", {})
        
        # Adjust content distribution based on platform success
        if success_rates.get("platforms"):
            total_allocation = 100
            platform_allocations = {}
            
            for platform, rate in success_rates["platforms"].items():
                # Allocate more resources to successful platforms
                allocation = max(20, int(rate * 60))  # Minimum 20%, up to 60% based on success
                platform_allocations[platform] = allocation
            
            adjustments["content_distribution"] = platform_allocations
        
        # Voice selection adjustments
        successful_voices = patterns.get("successful_voice_tags", {})
        if successful_voices:
            adjustments["voice_selection"] = {
                "prioritize": list(successful_voices.keys()),
                "recommendation": "Use these voice tags more frequently in future content"
            }
        
        return adjustments
    
    def _generate_future_content_guidance(self, recommendations: List[Dict]) -> Dict[str, Any]:
        """Generate specific guidance for future content creation"""
        
        guidance = {
            "immediate_actions": [],
            "weekly_focus": [],
            "monthly_strategy": [],
            "experimental_areas": []
        }
        
        for rec in recommendations:
            rec_type = rec.get("type", "general")
            recommendation = rec.get("recommendation", "")
            confidence = rec.get("confidence", 0)
            
            if confidence > 0.7:  # High confidence recommendations
                guidance["immediate_actions"].append({
                    "action": recommendation,
                    "priority": "high",
                    "confidence": confidence
                })
            elif confidence > 0.4:  # Medium confidence recommendations
                guidance["weekly_focus"].append({
                    "focus_area": recommendation,
                    "priority": "medium",
                    "confidence": confidence
                })
            else:  # Lower confidence - experimental
                guidance["experimental_areas"].append({
                    "experiment": recommendation,
                    "priority": "low",
                    "confidence": confidence
                })
        
        # Add general monthly strategy
        guidance["monthly_strategy"] = [
            "Review and adjust content calendar based on performance data",
            "Experiment with new voice combinations and tones",
            "Analyze cross-platform content performance trends",
            "Optimize content timing and frequency"
        ]
        
        return guidance
    
    def _prepare_rl_signals(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare signals for future reinforcement learning integration (Task 5)"""
        
        rl_signals = {
            "reward_signals": {},
            "state_features": {},
            "action_preferences": {},
            "exploration_areas": []
        }
        
        if "error" not in patterns:
            # Reward signals based on successful patterns
            rl_signals["reward_signals"] = {
                "high_reward_platforms": list(patterns.get("successful_platforms", {}).keys()),
                "high_reward_tones": list(patterns.get("successful_tones", {}).keys()),
                "high_reward_languages": list(patterns.get("successful_languages", {}).keys())
            }
            
            # State features for RL model
            rl_signals["state_features"] = {
                "platform_performance_history": patterns.get("engagement_trends", []),
                "content_characteristics": patterns.get("content_characteristics", {}),
                "temporal_patterns": "weekly_analysis"
            }
            
            # Action preferences
            success_rates = patterns.get("success_rates", {})
            rl_signals["action_preferences"] = {
                "platform_weights": success_rates.get("platforms", {}),
                "tone_weights": success_rates.get("tones", {}),
                "language_weights": success_rates.get("languages", {})
            }
        
        # Areas for exploration
        rl_signals["exploration_areas"] = [
            "voice_tone_combinations",
            "cross_platform_content_adaptation",
            "temporal_posting_optimization",
            "audience_segment_targeting"
        ]
        
        return rl_signals
    
    def _save_strategy_recommendations(self, strategy: Dict[str, Any]):
        """Save strategy recommendations to JSON file"""
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"strategy_recommendations_{strategy['strategy_id']}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(strategy, f, indent=2, ensure_ascii=False)
            
            print(f"Strategy recommendations saved to: {filepath}")
            
        except Exception as e:
            print(f"Error saving strategy recommendations: {e}")

# Global strategy recommender instance
strategy_recommender = StrategyRecommender()

def get_strategy_recommender() -> StrategyRecommender:
    """Get the global strategy recommender instance"""
    return strategy_recommender
