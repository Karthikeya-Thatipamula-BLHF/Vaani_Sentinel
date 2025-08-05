"""
Agent K: Feedback & Analytics Collector
Task 3 Agent K: Feedback & Analytics Collector

Generates dummy engagement stats for simulated posts:
- Views, Likes, Shares, Comments (randomized but realistic)
- Stores metrics in analytics_db.json linked to original content ID
- Creates feedback signals: "High-performing topics", "Underperforming formats"
"""

import json
import os
import uuid
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

class EngagementType(Enum):
    VIEW = "view"
    LIKE = "like"
    SHARE = "share"
    COMMENT = "comment"
    CLICK = "click"
    SAVE = "save"

@dataclass
class EngagementMetrics:
    post_id: str
    platform: str
    views: int
    likes: int
    shares: int
    comments: int
    clicks: int
    saves: int
    engagement_rate: float
    reach: int
    impressions: int
    created_at: datetime

class AnalyticsCollector:
    """Agent K: Feedback & Analytics Collector"""
    
    def __init__(self):
        self.analytics_db_path = "./analytics_db"
        os.makedirs(self.analytics_db_path, exist_ok=True)
        
        # Platform-specific engagement patterns
        self.platform_patterns = {
            "twitter": {
                "avg_engagement_rate": 0.045,  # 4.5%
                "view_to_like_ratio": 0.03,
                "like_to_share_ratio": 0.15,
                "like_to_comment_ratio": 0.08,
                "peak_hours": [9, 12, 15, 18, 21]
            },
            "instagram": {
                "avg_engagement_rate": 0.067,  # 6.7%
                "view_to_like_ratio": 0.08,
                "like_to_share_ratio": 0.05,
                "like_to_comment_ratio": 0.12,
                "peak_hours": [11, 13, 17, 19, 20]
            },
            "linkedin": {
                "avg_engagement_rate": 0.054,  # 5.4%
                "view_to_like_ratio": 0.04,
                "like_to_share_ratio": 0.08,
                "like_to_comment_ratio": 0.15,
                "peak_hours": [8, 9, 12, 17, 18]
            },
            "spotify": {
                "avg_engagement_rate": 0.025,  # 2.5%
                "view_to_like_ratio": 0.02,
                "like_to_share_ratio": 0.03,
                "like_to_comment_ratio": 0.05,
                "peak_hours": [7, 8, 16, 17, 22]
            }
        }
        
        # Content type performance modifiers
        self.content_type_modifiers = {
            "devotional": {"engagement_boost": 1.2, "share_boost": 1.5},
            "educational": {"engagement_boost": 1.1, "comment_boost": 1.3},
            "inspirational": {"engagement_boost": 1.3, "like_boost": 1.4},
            "news": {"engagement_boost": 0.9, "share_boost": 1.2},
            "entertainment": {"engagement_boost": 1.4, "like_boost": 1.6}
        }
    
    def generate_engagement_metrics(
        self,
        post_id: str,
        platform: str,
        content_type: str = "general",
        language: str = "en",
        posting_time: datetime = None
    ) -> EngagementMetrics:
        """Generate realistic engagement metrics for a post"""
        
        if posting_time is None:
            posting_time = datetime.utcnow()
        
        # Get platform patterns
        platform_pattern = self.platform_patterns.get(platform, self.platform_patterns["twitter"])
        
        # Base metrics calculation
        base_reach = random.randint(500, 5000)
        base_impressions = int(base_reach * random.uniform(1.2, 3.0))
        
        # Time-based modifier
        hour = posting_time.hour
        time_modifier = 1.2 if hour in platform_pattern["peak_hours"] else random.uniform(0.7, 1.0)
        
        # Content type modifier
        content_modifier = self.content_type_modifiers.get(content_type, {"engagement_boost": 1.0})
        engagement_boost = content_modifier.get("engagement_boost", 1.0)
        
        # Language modifier (some languages may have different engagement patterns)
        language_modifier = self._get_language_modifier(language)
        
        # Calculate final reach and impressions
        final_reach = int(base_reach * time_modifier * language_modifier)
        final_impressions = int(base_impressions * time_modifier * language_modifier)
        
        # Calculate engagement metrics
        views = final_impressions
        likes = int(views * platform_pattern["view_to_like_ratio"] * engagement_boost * random.uniform(0.8, 1.2))
        shares = int(likes * platform_pattern["like_to_share_ratio"] * content_modifier.get("share_boost", 1.0) * random.uniform(0.7, 1.3))
        comments = int(likes * platform_pattern["like_to_comment_ratio"] * content_modifier.get("comment_boost", 1.0) * random.uniform(0.6, 1.4))
        clicks = int(views * random.uniform(0.01, 0.05))
        saves = int(likes * random.uniform(0.1, 0.3))
        
        # Calculate engagement rate
        total_engagements = likes + shares + comments + clicks + saves
        engagement_rate = total_engagements / views if views > 0 else 0
        
        return EngagementMetrics(
            post_id=post_id,
            platform=platform,
            views=views,
            likes=likes,
            shares=shares,
            comments=comments,
            clicks=clicks,
            saves=saves,
            engagement_rate=engagement_rate,
            reach=final_reach,
            impressions=final_impressions,
            created_at=posting_time
        )
    
    def _get_language_modifier(self, language: str) -> float:
        """Get engagement modifier based on language"""
        
        # Language-based engagement patterns
        language_modifiers = {
            "en": 1.0,      # Baseline
            "hi": 1.1,      # Higher engagement in Hindi
            "sa": 0.8,      # Lower reach but higher quality engagement
            "mr": 0.9,
            "gu": 0.9,
            "ta": 0.95,
            "te": 0.95,
            "kn": 0.9,
            "ml": 0.9,
            "bn": 1.05,
            "de": 0.85,
            "fr": 0.9,
            "es": 1.05,
            "it": 0.9,
            "pt": 0.95,
            "ru": 0.8,
            "ja": 0.85,
            "ko": 0.9,
            "zh": 0.95,
            "ar": 1.0
        }
        
        return language_modifiers.get(language, 1.0)
    
    def store_analytics(self, metrics: EngagementMetrics) -> str:
        """Store analytics data"""
        
        # Create analytics entry
        analytics_data = {
            "analytics_id": str(uuid.uuid4()),
            "post_id": metrics.post_id,
            "platform": metrics.platform,
            "metrics": {
                "views": metrics.views,
                "likes": metrics.likes,
                "shares": metrics.shares,
                "comments": metrics.comments,
                "clicks": metrics.clicks,
                "saves": metrics.saves,
                "engagement_rate": metrics.engagement_rate,
                "reach": metrics.reach,
                "impressions": metrics.impressions
            },
            "created_at": metrics.created_at.isoformat(),
            "stored_at": datetime.utcnow().isoformat()
        }
        
        # Store in daily file
        date_str = metrics.created_at.strftime("%Y%m%d")
        filename = f"analytics_{date_str}.json"
        filepath = os.path.join(self.analytics_db_path, filename)
        
        # Load existing data or create new
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                daily_analytics = json.load(f)
        else:
            daily_analytics = []
        
        daily_analytics.append(analytics_data)
        
        # Save updated data
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(daily_analytics, f, indent=2, ensure_ascii=False)
        
        return analytics_data["analytics_id"]
    
    def get_performance_insights(self, days: int = 7) -> Dict[str, Any]:
        """Get performance insights for the last N days"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        all_analytics = []
        
        # Load analytics data for the date range
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y%m%d")
            filename = f"analytics_{date_str}.json"
            filepath = os.path.join(self.analytics_db_path, filename)
            
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    daily_data = json.load(f)
                    all_analytics.extend(daily_data)
            
            current_date += timedelta(days=1)
        
        if not all_analytics:
            return {"message": "No analytics data found for the specified period"}
        
        # Calculate insights
        insights = self._calculate_insights(all_analytics)
        
        return insights
    
    def _calculate_insights(self, analytics_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance insights from analytics data"""
        
        # Initialize counters
        total_posts = len(analytics_data)
        platform_stats = {}
        top_performers = []
        underperformers = []
        
        # Process each analytics entry
        for entry in analytics_data:
            platform = entry["platform"]
            metrics = entry["metrics"]
            
            # Initialize platform stats
            if platform not in platform_stats:
                platform_stats[platform] = {
                    "posts": 0,
                    "total_views": 0,
                    "total_likes": 0,
                    "total_shares": 0,
                    "total_comments": 0,
                    "total_engagement_rate": 0
                }
            
            # Update platform stats
            platform_stats[platform]["posts"] += 1
            platform_stats[platform]["total_views"] += metrics["views"]
            platform_stats[platform]["total_likes"] += metrics["likes"]
            platform_stats[platform]["total_shares"] += metrics["shares"]
            platform_stats[platform]["total_comments"] += metrics["comments"]
            platform_stats[platform]["total_engagement_rate"] += metrics["engagement_rate"]
            
            # Identify top performers and underperformers
            if metrics["engagement_rate"] > 0.08:  # 8% engagement rate
                top_performers.append({
                    "post_id": entry["post_id"],
                    "platform": platform,
                    "engagement_rate": metrics["engagement_rate"],
                    "views": metrics["views"],
                    "likes": metrics["likes"]
                })
            elif metrics["engagement_rate"] < 0.02:  # 2% engagement rate
                underperformers.append({
                    "post_id": entry["post_id"],
                    "platform": platform,
                    "engagement_rate": metrics["engagement_rate"],
                    "views": metrics["views"],
                    "likes": metrics["likes"]
                })
        
        # Calculate averages for each platform
        for platform in platform_stats:
            stats = platform_stats[platform]
            posts_count = stats["posts"]
            if posts_count > 0:
                stats["avg_views"] = stats["total_views"] / posts_count
                stats["avg_likes"] = stats["total_likes"] / posts_count
                stats["avg_shares"] = stats["total_shares"] / posts_count
                stats["avg_comments"] = stats["total_comments"] / posts_count
                stats["avg_engagement_rate"] = stats["total_engagement_rate"] / posts_count
        
        # Sort performers
        top_performers = sorted(top_performers, key=lambda x: x["engagement_rate"], reverse=True)[:5]
        underperformers = sorted(underperformers, key=lambda x: x["engagement_rate"])[:5]
        
        return {
            "period_summary": {
                "total_posts": total_posts,
                "date_range": f"Last {len(analytics_data)} posts analyzed",
                "platforms_analyzed": list(platform_stats.keys())
            },
            "platform_performance": platform_stats,
            "top_performers": top_performers,
            "underperformers": underperformers,
            "recommendations": self._generate_recommendations(platform_stats, top_performers, underperformers)
        }
    
    def _generate_recommendations(
        self,
        platform_stats: Dict[str, Any],
        top_performers: List[Dict[str, Any]],
        underperformers: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate performance recommendations"""
        
        recommendations = []
        
        # Platform-specific recommendations
        best_platform = max(platform_stats.keys(), key=lambda p: platform_stats[p].get("avg_engagement_rate", 0))
        recommendations.append(f"Focus more content on {best_platform} - highest average engagement rate")
        
        # Content type recommendations based on top performers
        if top_performers:
            recommendations.append("Replicate successful content patterns from top-performing posts")
            recommendations.append("Analyze timing and content type of high-engagement posts")
        
        # Improvement recommendations based on underperformers
        if underperformers:
            recommendations.append("Review and improve content strategy for low-performing posts")
            recommendations.append("Consider different posting times or content formats")
        
        # General recommendations
        recommendations.append("Maintain consistent posting schedule during peak hours")
        recommendations.append("Engage with audience through comments and responses")
        recommendations.append("Use relevant hashtags and optimize content for each platform")
        
        return recommendations
    
    def generate_weekly_strategy(self) -> Dict[str, Any]:
        """Generate weekly strategy recommendations"""
        
        # Get insights for the last week
        insights = self.get_performance_insights(days=7)
        
        if "message" in insights:
            return insights
        
        # Extract strategy elements
        top_performers = insights.get("top_performers", [])
        platform_performance = insights.get("platform_performance", {})
        
        # Determine best performing content characteristics
        best_platforms = sorted(
            platform_performance.items(),
            key=lambda x: x[1].get("avg_engagement_rate", 0),
            reverse=True
        )[:3]
        
        strategy = {
            "week_start": (datetime.utcnow() - timedelta(days=7)).isoformat(),
            "top_performers": top_performers,
            "underperformers": insights.get("underperformers", []),
            "recommendations": [
                f"Prioritize content for {platform}" for platform, _ in best_platforms
            ],
            "suggested_tones": ["devotional", "inspirational", "educational"],  # Based on performance
            "suggested_languages": ["en", "hi", "sa"],  # Based on engagement patterns
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "analysis_period": "7 days",
                "total_posts_analyzed": insights.get("period_summary", {}).get("total_posts", 0)
            }
        }
        
        return strategy

    def generate_task3_engagement_stats(
        self,
        content_id: str,
        platform: str,
        content_text: str,
        language: str = "en",
        voice_tag: str = "neutral",
        tone: str = "neutral"
    ) -> Dict[str, Any]:
        """
        Task 3 Agent K: Generate dummy engagement stats for simulated posts

        Args:
            content_id: Original content ID to link metrics
            platform: Platform where content was posted
            content_text: The actual content text
            language: Content language
            voice_tag: Voice used for TTS
            tone: Content tone

        Returns:
            Realistic dummy engagement statistics
        """

        # Generate realistic but randomized engagement stats
        base_metrics = self._generate_realistic_base_metrics(platform, content_text, language, tone)

        # Add voice-specific bonuses
        voice_multiplier = self._calculate_voice_engagement_multiplier(voice_tag, platform)

        # Apply multipliers
        final_metrics = {
            "views": int(base_metrics["views"] * voice_multiplier),
            "likes": int(base_metrics["likes"] * voice_multiplier),
            "shares": int(base_metrics["shares"] * voice_multiplier),
            "comments": int(base_metrics["comments"] * voice_multiplier),
            "clicks": int(base_metrics["clicks"] * voice_multiplier),
            "saves": int(base_metrics["saves"] * voice_multiplier)
        }

        # Calculate engagement rate
        total_engagements = final_metrics["likes"] + final_metrics["shares"] + final_metrics["comments"]
        engagement_rate = total_engagements / final_metrics["views"] if final_metrics["views"] > 0 else 0

        engagement_data = {
            "content_id": content_id,
            "platform": platform,
            "language": language,
            "voice_tag": voice_tag,
            "tone": tone,
            "content_preview": content_text[:100] + "..." if len(content_text) > 100 else content_text,
            "metrics": final_metrics,
            "engagement_rate": round(engagement_rate, 4),
            "performance_category": self._categorize_performance(engagement_rate, platform),
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "voice_multiplier": voice_multiplier,
                "base_metrics": base_metrics,
                "is_simulation": True,
                "task": "task3_agent_k"
            }
        }

        # Store in analytics_db.json
        self._store_in_analytics_db(engagement_data)

        return engagement_data

    def _generate_realistic_base_metrics(
        self,
        platform: str,
        content_text: str,
        language: str,
        tone: str
    ) -> Dict[str, int]:
        """Generate realistic base metrics before applying multipliers"""

        # Platform-specific base ranges
        platform_ranges = {
            "instagram": {"views": (800, 3000), "likes": (40, 200), "shares": (5, 30), "comments": (2, 15), "clicks": (10, 50), "saves": (5, 25)},
            "twitter": {"views": (500, 2000), "likes": (20, 150), "shares": (3, 25), "comments": (1, 10), "clicks": (15, 60), "saves": (2, 12)},
            "linkedin": {"views": (300, 1200), "likes": (15, 80), "shares": (2, 15), "comments": (1, 8), "clicks": (20, 70), "saves": (3, 18)}
        }

        ranges = platform_ranges.get(platform, platform_ranges["twitter"])

        # Content quality multipliers
        content_multiplier = 1.0
        if len(content_text.split()) > 20:  # Longer content
            content_multiplier *= 1.1
        if tone in ["devotional", "inspirational"]:  # Engaging tones
            content_multiplier *= 1.2
        if language in ["hi", "sa"]:  # Indian languages might have different engagement
            content_multiplier *= 1.15

        base_metrics = {}
        for metric, (min_val, max_val) in ranges.items():
            base_value = random.randint(min_val, max_val)
            base_metrics[metric] = int(base_value * content_multiplier)

        return base_metrics

    def _calculate_voice_engagement_multiplier(self, voice_tag: str, platform: str) -> float:
        """Calculate engagement multiplier based on voice characteristics"""

        multiplier = 1.0

        # Voice type bonuses
        if "devotional" in voice_tag:
            multiplier *= 1.25  # Devotional voices perform well
        elif "energetic" in voice_tag:
            multiplier *= 1.15  # Energetic voices are engaging
        elif "professional" in voice_tag and platform == "linkedin":
            multiplier *= 1.3   # Professional voices excel on LinkedIn
        elif "conversational" in voice_tag and platform in ["instagram", "twitter"]:
            multiplier *= 1.2   # Conversational voices work well on social platforms

        # Gender-based slight variations (realistic but not biased)
        if "female" in voice_tag:
            multiplier *= random.uniform(1.05, 1.15)
        elif "male" in voice_tag:
            multiplier *= random.uniform(1.0, 1.1)

        # Add some randomness to simulate real-world variability
        multiplier *= random.uniform(0.9, 1.1)

        return round(multiplier, 3)

    def _categorize_performance(self, engagement_rate: float, platform: str) -> str:
        """Categorize performance based on engagement rate"""

        # Platform-specific thresholds
        thresholds = {
            "instagram": {"high": 0.06, "medium": 0.03},
            "twitter": {"high": 0.05, "medium": 0.025},
            "linkedin": {"high": 0.04, "medium": 0.02}
        }

        platform_thresholds = thresholds.get(platform, thresholds["twitter"])

        if engagement_rate >= platform_thresholds["high"]:
            return "high_performing"
        elif engagement_rate >= platform_thresholds["medium"]:
            return "medium_performing"
        else:
            return "underperforming"

    def _store_in_analytics_db(self, engagement_data: Dict[str, Any]):
        """Store engagement data in analytics_db.json"""

        analytics_db_file = os.path.join(self.analytics_db_path, "post_metrics.json")

        # Load existing data
        if os.path.exists(analytics_db_file):
            try:
                with open(analytics_db_file, 'r', encoding='utf-8') as f:
                    analytics_db = json.load(f)
            except Exception:
                analytics_db = {"posts": [], "metadata": {"created_at": datetime.utcnow().isoformat()}}
        else:
            analytics_db = {"posts": [], "metadata": {"created_at": datetime.utcnow().isoformat()}}

        # Add new engagement data
        analytics_db["posts"].append(engagement_data)
        analytics_db["metadata"]["last_updated"] = datetime.utcnow().isoformat()
        analytics_db["metadata"]["total_posts"] = len(analytics_db["posts"])

        # Save updated data
        try:
            with open(analytics_db_file, 'w', encoding='utf-8') as f:
                json.dump(analytics_db, f, indent=2, ensure_ascii=False)

            print(f"Engagement data stored in analytics_db: {engagement_data['content_id']}")

        except Exception as e:
            print(f"Error storing engagement data: {e}")

    def create_feedback_signals(self, days_back: int = 7) -> Dict[str, Any]:
        """
        Task 3 Agent K: Create feedback signals for high/underperforming content

        Args:
            days_back: Number of days to analyze

        Returns:
            Feedback signals with high-performing topics and underperforming formats
        """

        analytics_db_file = os.path.join(self.analytics_db_path, "post_metrics.json")

        if not os.path.exists(analytics_db_file):
            return {"error": "No analytics data available"}

        try:
            with open(analytics_db_file, 'r', encoding='utf-8') as f:
                analytics_db = json.load(f)
        except Exception as e:
            return {"error": f"Failed to load analytics data: {e}"}

        posts = analytics_db.get("posts", [])

        # Filter posts from last N days
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        recent_posts = [
            post for post in posts
            if datetime.fromisoformat(post["timestamp"]) >= cutoff_date
        ]

        if not recent_posts:
            return {"error": "No recent posts to analyze"}

        # Analyze high performers
        high_performers = [post for post in recent_posts if post["performance_category"] == "high_performing"]
        underperformers = [post for post in recent_posts if post["performance_category"] == "underperforming"]

        # Extract patterns
        high_performing_topics = self._extract_topic_patterns(high_performers)
        underperforming_formats = self._extract_format_patterns(underperformers)

        feedback_signals = {
            "analysis_period": f"Last {days_back} days",
            "total_posts_analyzed": len(recent_posts),
            "high_performers_count": len(high_performers),
            "underperformers_count": len(underperformers),
            "high_performing_topics": high_performing_topics,
            "underperforming_formats": underperforming_formats,
            "recommendations": self._generate_content_recommendations(high_performers, underperformers),
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "agent": "task3_agent_k_feedback",
                "analysis_type": "feedback_signals"
            }
        }

        return feedback_signals

    def _extract_topic_patterns(self, high_performers: List[Dict]) -> List[Dict[str, Any]]:
        """Extract patterns from high-performing content"""

        if not high_performers:
            return []

        # Group by various attributes
        language_performance = {}
        tone_performance = {}
        voice_performance = {}
        platform_performance = {}

        for post in high_performers:
            # Language patterns
            lang = post.get("language", "unknown")
            if lang not in language_performance:
                language_performance[lang] = {"count": 0, "avg_engagement": 0, "total_engagement": 0}
            language_performance[lang]["count"] += 1
            language_performance[lang]["total_engagement"] += post.get("engagement_rate", 0)
            language_performance[lang]["avg_engagement"] = language_performance[lang]["total_engagement"] / language_performance[lang]["count"]

            # Similar for tone, voice, platform
            tone = post.get("tone", "unknown")
            if tone not in tone_performance:
                tone_performance[tone] = {"count": 0, "avg_engagement": 0, "total_engagement": 0}
            tone_performance[tone]["count"] += 1
            tone_performance[tone]["total_engagement"] += post.get("engagement_rate", 0)
            tone_performance[tone]["avg_engagement"] = tone_performance[tone]["total_engagement"] / tone_performance[tone]["count"]

        # Convert to sorted lists
        top_languages = sorted(language_performance.items(), key=lambda x: x[1]["avg_engagement"], reverse=True)[:3]
        top_tones = sorted(tone_performance.items(), key=lambda x: x[1]["avg_engagement"], reverse=True)[:3]

        return [
            {
                "pattern_type": "language",
                "top_performers": [{"language": lang, "avg_engagement": data["avg_engagement"], "post_count": data["count"]} for lang, data in top_languages]
            },
            {
                "pattern_type": "tone",
                "top_performers": [{"tone": tone, "avg_engagement": data["avg_engagement"], "post_count": data["count"]} for tone, data in top_tones]
            }
        ]

    def _extract_format_patterns(self, underperformers: List[Dict]) -> List[Dict[str, Any]]:
        """Extract patterns from underperforming content"""

        if not underperformers:
            return []

        # Group underperformers by platform and voice characteristics
        platform_issues = {}
        voice_issues = {}

        for post in underperformers:
            platform = post.get("platform", "unknown")
            if platform not in platform_issues:
                platform_issues[platform] = {"count": 0, "avg_engagement": 0, "total_engagement": 0}
            platform_issues[platform]["count"] += 1
            platform_issues[platform]["total_engagement"] += post.get("engagement_rate", 0)
            platform_issues[platform]["avg_engagement"] = platform_issues[platform]["total_engagement"] / platform_issues[platform]["count"]

        # Sort by worst performance
        worst_platforms = sorted(platform_issues.items(), key=lambda x: x[1]["avg_engagement"])[:3]

        return [
            {
                "issue_type": "platform_format",
                "problematic_formats": [{"platform": platform, "avg_engagement": data["avg_engagement"], "post_count": data["count"]} for platform, data in worst_platforms]
            }
        ]

    def _generate_content_recommendations(self, high_performers: List[Dict], underperformers: List[Dict]) -> List[str]:
        """Generate actionable content recommendations"""

        recommendations = []

        if high_performers:
            # Find most common characteristics of high performers
            common_languages = {}
            common_tones = {}

            for post in high_performers:
                lang = post.get("language", "en")
                tone = post.get("tone", "neutral")
                common_languages[lang] = common_languages.get(lang, 0) + 1
                common_tones[tone] = common_tones.get(tone, 0) + 1

            if common_languages:
                top_lang = max(common_languages.items(), key=lambda x: x[1])[0]
                recommendations.append(f"Focus more content in {top_lang} language - shows high engagement")

            if common_tones:
                top_tone = max(common_tones.items(), key=lambda x: x[1])[0]
                recommendations.append(f"Use {top_tone} tone more frequently - performs well")

        if underperformers:
            # Find common issues
            problem_platforms = {}
            for post in underperformers:
                platform = post.get("platform", "unknown")
                problem_platforms[platform] = problem_platforms.get(platform, 0) + 1

            if problem_platforms:
                worst_platform = max(problem_platforms.items(), key=lambda x: x[1])[0]
                recommendations.append(f"Review content strategy for {worst_platform} - needs improvement")

        # Default recommendations if no clear patterns
        if not recommendations:
            recommendations = [
                "Continue experimenting with different content formats",
                "Test voice variations for better engagement",
                "Monitor platform-specific performance trends"
            ]

        return recommendations

# Global analytics collector instance
analytics_collector = AnalyticsCollector()

def get_analytics_collector() -> AnalyticsCollector:
    """Get the global analytics collector instance"""
    return analytics_collector
