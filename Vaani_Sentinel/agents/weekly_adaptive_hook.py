"""
Weekly Adaptive Hook for Vaani Sentinel X
Reads engagement signals and adjusts tone/language suggestions for next batch
Task 5 Component 6: Weekly Adaptive Hook Prototype
"""

import json
import os
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
from collections import defaultdict

class WeeklyAdaptiveHook:
    """
    Weekly strategy recommendation system that analyzes engagement signals
    and adjusts tone/language suggestions based on top performing posts
    """
    
    def __init__(self):
        self.output_dir = "./data"
        self.analytics_dir = "./content/analytics_ready"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Performance thresholds
        self.performance_thresholds = {
            "high_performance": 0.8,
            "medium_performance": 0.5,
            "low_performance": 0.2
        }
        
        # Adaptation weights
        self.adaptation_weights = {
            "engagement_rate": 0.4,
            "reach": 0.3,
            "sentiment": 0.2,
            "completion_rate": 0.1
        }
    
    def analyze_weekly_performance(
        self,
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """
        Analyze weekly performance and generate strategy recommendations
        
        Args:
            start_date: Start date for analysis (YYYY-MM-DD)
            end_date: End date for analysis (YYYY-MM-DD)
            
        Returns:
            Weekly strategy recommendations
        """
        
        analysis_id = str(uuid.uuid4())
        
        # Set default date range (last 7 days)
        if end_date is None:
            end_date = datetime.now(timezone.utc).date()
        else:
            end_date = datetime.fromisoformat(end_date).date()
        
        if start_date is None:
            start_date = end_date - timedelta(days=7)
        else:
            start_date = datetime.fromisoformat(start_date).date()
        
        # Load engagement data
        engagement_data = self._load_engagement_data(start_date, end_date)
        
        # Analyze performance patterns
        performance_analysis = self._analyze_performance_patterns(engagement_data)
        
        # Generate recommendations
        recommendations = self._generate_strategy_recommendations(performance_analysis)
        
        # Create weekly strategy output
        weekly_strategy = {
            "analysis_id": analysis_id,
            "analysis_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "duration_days": (end_date - start_date).days
            },
            "performance_summary": performance_analysis["summary"],
            "top_performing_posts": performance_analysis["top_posts"],
            "performance_patterns": performance_analysis["patterns"],
            "strategy_recommendations": recommendations,
            "metadata": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "agent": "weekly_adaptive_hook",
                "version": "1.0",
                "total_posts_analyzed": len(engagement_data)
            }
        }
        
        # Save strategy recommendations
        self._save_weekly_strategy(weekly_strategy)
        
        return weekly_strategy
    
    def _load_engagement_data(
        self,
        start_date: datetime.date,
        end_date: datetime.date
    ) -> List[Dict[str, Any]]:
        """Load engagement data from analytics files"""
        
        engagement_data = []
        
        try:
            # Look for analytics files in the analytics directory
            if os.path.exists(self.analytics_dir):
                for filename in os.listdir(self.analytics_dir):
                    if filename.endswith('.json') and 'analytics' in filename:
                        filepath = os.path.join(self.analytics_dir, filename)
                        
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                
                            # Check if data is within date range
                            if self._is_within_date_range(data, start_date, end_date):
                                engagement_data.append(data)
                                
                        except Exception as e:
                            print(f"Error loading analytics file {filename}: {e}")
            
            # If no real data, generate sample data for demonstration
            if not engagement_data:
                engagement_data = self._generate_sample_engagement_data(start_date, end_date)
                
        except Exception as e:
            print(f"Error loading engagement data: {e}")
            engagement_data = self._generate_sample_engagement_data(start_date, end_date)
        
        return engagement_data
    
    def _is_within_date_range(
        self,
        data: Dict[str, Any],
        start_date: datetime.date,
        end_date: datetime.date
    ) -> bool:
        """Check if data is within the specified date range"""
        
        try:
            # Try to extract date from various possible fields
            date_fields = ['created_at', 'posting_time', 'timestamp', 'date']
            
            for field in date_fields:
                if field in data:
                    data_date = datetime.fromisoformat(data[field].replace('Z', '+00:00')).date()
                    return start_date <= data_date <= end_date
            
            return False
            
        except Exception:
            return False
    
    def _generate_sample_engagement_data(
        self,
        start_date: datetime.date,
        end_date: datetime.date
    ) -> List[Dict[str, Any]]:
        """Generate sample engagement data for demonstration"""
        
        import random
        
        sample_data = []
        current_date = start_date
        
        languages = ["en", "hi", "sa", "mr", "es", "fr"]
        tones = ["formal", "casual", "devotional", "uplifting", "neutral"]
        platforms = ["twitter", "instagram", "linkedin"]
        content_types = ["inspirational", "educational", "spiritual", "motivational"]
        
        while current_date <= end_date:
            # Generate 2-5 posts per day
            posts_per_day = random.randint(2, 5)
            
            for _ in range(posts_per_day):
                post_data = {
                    "post_id": str(uuid.uuid4()),
                    "created_at": current_date.isoformat(),
                    "language": random.choice(languages),
                    "tone": random.choice(tones),
                    "platform": random.choice(platforms),
                    "content_type": random.choice(content_types),
                    "engagement_metrics": {
                        "views": random.randint(100, 5000),
                        "likes": random.randint(10, 500),
                        "shares": random.randint(1, 100),
                        "comments": random.randint(0, 50),
                        "clicks": random.randint(5, 200),
                        "saves": random.randint(0, 80)
                    },
                    "performance_score": random.uniform(0.1, 0.95)
                }
                
                sample_data.append(post_data)
            
            current_date += timedelta(days=1)
        
        return sample_data
    
    def _analyze_performance_patterns(
        self,
        engagement_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze performance patterns from engagement data"""
        
        # Group data by various dimensions
        language_performance = defaultdict(list)
        tone_performance = defaultdict(list)
        platform_performance = defaultdict(list)
        content_type_performance = defaultdict(list)
        
        total_performance = []
        
        for post in engagement_data:
            performance_score = post.get("performance_score", 0.0)
            total_performance.append(performance_score)
            
            language = post.get("language", "unknown")
            tone = post.get("tone", "unknown")
            platform = post.get("platform", "unknown")
            content_type = post.get("content_type", "unknown")
            
            language_performance[language].append(performance_score)
            tone_performance[tone].append(performance_score)
            platform_performance[platform].append(performance_score)
            content_type_performance[content_type].append(performance_score)
        
        # Calculate averages
        def calculate_avg_performance(performance_dict):
            return {
                key: {
                    "average_score": sum(scores) / len(scores),
                    "post_count": len(scores),
                    "max_score": max(scores),
                    "min_score": min(scores)
                }
                for key, scores in performance_dict.items()
            }
        
        # Find top performing posts
        sorted_posts = sorted(engagement_data, 
                            key=lambda x: x.get("performance_score", 0.0), 
                            reverse=True)
        top_posts = sorted_posts[:3]  # Top 3 posts
        
        # Calculate overall performance
        avg_performance = sum(total_performance) / len(total_performance) if total_performance else 0.0
        
        return {
            "summary": {
                "total_posts": len(engagement_data),
                "average_performance": avg_performance,
                "high_performers": len([p for p in total_performance if p >= self.performance_thresholds["high_performance"]]),
                "medium_performers": len([p for p in total_performance if self.performance_thresholds["medium_performance"] <= p < self.performance_thresholds["high_performance"]]),
                "low_performers": len([p for p in total_performance if p < self.performance_thresholds["medium_performance"]])
            },
            "top_posts": top_posts,
            "patterns": {
                "language_performance": calculate_avg_performance(language_performance),
                "tone_performance": calculate_avg_performance(tone_performance),
                "platform_performance": calculate_avg_performance(platform_performance),
                "content_type_performance": calculate_avg_performance(content_type_performance)
            }
        }
    
    def _generate_strategy_recommendations(
        self,
        performance_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate strategy recommendations based on performance analysis"""
        
        patterns = performance_analysis["patterns"]
        
        # Find top performing dimensions
        top_languages = self._get_top_performers(patterns["language_performance"])
        top_tones = self._get_top_performers(patterns["tone_performance"])
        top_platforms = self._get_top_performers(patterns["platform_performance"])
        top_content_types = self._get_top_performers(patterns["content_type_performance"])
        
        recommendations = {
            "priority_languages": {
                "recommended": top_languages[:3],
                "reasoning": "Focus on languages with highest engagement rates",
                "suggested_allocation": "60% of content in top 3 languages"
            },
            "priority_tones": {
                "recommended": top_tones[:3],
                "reasoning": "Emphasize tones that resonate best with audience",
                "suggested_allocation": "70% of content using top 3 tones"
            },
            "priority_platforms": {
                "recommended": top_platforms[:2],
                "reasoning": "Concentrate efforts on best-performing platforms",
                "suggested_allocation": "80% of publishing efforts on top 2 platforms"
            },
            "content_strategy": {
                "recommended_types": top_content_types[:2],
                "content_mix": "Focus on proven content types while testing new formats",
                "posting_frequency": self._recommend_posting_frequency(performance_analysis)
            },
            "optimization_suggestions": self._generate_optimization_suggestions(performance_analysis),
            "next_week_focus": {
                "primary_language": top_languages[0] if top_languages else "en",
                "primary_tone": top_tones[0] if top_tones else "neutral",
                "primary_platform": top_platforms[0] if top_platforms else "twitter",
                "content_experiments": self._suggest_content_experiments(patterns)
            }
        }
        
        return recommendations
    
    def _get_top_performers(self, performance_dict: Dict[str, Dict[str, float]]) -> List[str]:
        """Get top performers sorted by average score"""
        
        sorted_items = sorted(
            performance_dict.items(),
            key=lambda x: x[1]["average_score"],
            reverse=True
        )
        
        return [item[0] for item in sorted_items]
    
    def _recommend_posting_frequency(self, performance_analysis: Dict[str, Any]) -> str:
        """Recommend posting frequency based on performance"""
        
        avg_performance = performance_analysis["summary"]["average_performance"]
        
        if avg_performance >= 0.7:
            return "Maintain current frequency - high engagement"
        elif avg_performance >= 0.5:
            return "Slight increase in frequency for top-performing content types"
        else:
            return "Focus on quality over quantity - reduce frequency, improve content"
    
    def _generate_optimization_suggestions(self, performance_analysis: Dict[str, Any]) -> List[str]:
        """Generate specific optimization suggestions"""
        
        suggestions = []
        
        avg_performance = performance_analysis["summary"]["average_performance"]
        
        if avg_performance < 0.5:
            suggestions.append("Consider A/B testing different content formats")
            suggestions.append("Review and optimize posting times")
        
        if performance_analysis["summary"]["low_performers"] > performance_analysis["summary"]["high_performers"]:
            suggestions.append("Analyze low-performing content for common patterns to avoid")
            suggestions.append("Increase focus on proven high-performing content types")
        
        suggestions.append("Monitor engagement patterns for seasonal trends")
        suggestions.append("Test new tone combinations based on top performers")
        
        return suggestions
    
    def _suggest_content_experiments(self, patterns: Dict[str, Any]) -> List[str]:
        """Suggest content experiments for next week"""
        
        experiments = []
        
        # Find underperforming areas that might have potential
        tone_performance = patterns["tone_performance"]
        language_performance = patterns["language_performance"]
        
        experiments.append("Test hybrid tone combinations (e.g., casual-devotional)")
        experiments.append("Experiment with cross-language content adaptation")
        experiments.append("Try different content lengths for top-performing tones")
        
        return experiments
    
    def _save_weekly_strategy(self, strategy: Dict[str, Any]):
        """Save weekly strategy recommendations to JSON file"""
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"weekly_strategy_recommendation_{strategy['analysis_id']}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(strategy, f, indent=2, ensure_ascii=False)
            
            print(f"Weekly strategy recommendations saved to: {filepath}")
            
        except Exception as e:
            print(f"Error saving weekly strategy: {e}")

# Global weekly adaptive hook instance
weekly_adaptive_hook = WeeklyAdaptiveHook()

def get_weekly_adaptive_hook() -> WeeklyAdaptiveHook:
    """Get the global weekly adaptive hook instance"""
    return weekly_adaptive_hook
