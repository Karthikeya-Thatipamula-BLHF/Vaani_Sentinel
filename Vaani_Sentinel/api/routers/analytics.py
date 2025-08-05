"""
Analytics router for Vaani Sentinel X
Handles analytics collection, performance tracking, and insights
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from core.database import get_db, DatabaseManager
from api.models import AnalyticsResponse, WeeklyStrategyResponse, StatusResponse
from api.routers.auth import get_current_user
from agents.analytics_collector import AnalyticsCollector

router = APIRouter()

# Request Models
class EngagementGenerationRequest(BaseModel):
    post_id: str
    platform: str
    content_type: str = "general"
    language: str = "en"
    posting_time: Optional[datetime] = None

class PerformanceInsightsRequest(BaseModel):
    days: int = 7
    platforms: Optional[List[str]] = None

# Response Models
class EngagementMetricsResponse(BaseModel):
    analytics_id: str
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

class PerformanceInsightsResponse(BaseModel):
    period_summary: Dict[str, Any]
    platform_performance: Dict[str, Any]
    top_performers: List[Dict[str, Any]]
    underperformers: List[Dict[str, Any]]
    recommendations: List[str]

@router.post("/generate-engagement", response_model=EngagementMetricsResponse)
async def generate_engagement_metrics(
    request: EngagementGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate engagement metrics for a post"""
    try:
        analytics_collector = AnalyticsCollector()
        
        # Generate metrics
        metrics = analytics_collector.generate_engagement_metrics(
            post_id=request.post_id,
            platform=request.platform,
            content_type=request.content_type,
            language=request.language,
            posting_time=request.posting_time or datetime.utcnow()
        )
        
        # Store analytics
        analytics_id = analytics_collector.store_analytics(metrics)
        
        return EngagementMetricsResponse(
            analytics_id=analytics_id,
            post_id=metrics.post_id,
            platform=metrics.platform,
            views=metrics.views,
            likes=metrics.likes,
            shares=metrics.shares,
            comments=metrics.comments,
            clicks=metrics.clicks,
            saves=metrics.saves,
            engagement_rate=metrics.engagement_rate,
            reach=metrics.reach,
            impressions=metrics.impressions,
            created_at=metrics.created_at
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating engagement metrics: {str(e)}"
        )

@router.post("/batch-generate-engagement", response_model=StatusResponse)
async def batch_generate_engagement(
    post_ids: List[str],
    platform: str,
    content_type: str = "general",
    language: str = "en",
    current_user: dict = Depends(get_current_user)
):
    """Generate engagement metrics for multiple posts"""
    try:
        analytics_collector = AnalyticsCollector()
        results = []
        
        for post_id in post_ids:
            try:
                # Generate metrics
                metrics = analytics_collector.generate_engagement_metrics(
                    post_id=post_id,
                    platform=platform,
                    content_type=content_type,
                    language=language,
                    posting_time=datetime.utcnow()
                )
                
                # Store analytics
                analytics_id = analytics_collector.store_analytics(metrics)
                
                results.append({
                    "post_id": post_id,
                    "analytics_id": analytics_id,
                    "engagement_rate": metrics.engagement_rate,
                    "status": "success"
                })
                
            except Exception as e:
                results.append({
                    "post_id": post_id,
                    "error": str(e),
                    "status": "failed"
                })
        
        successful = len([r for r in results if r["status"] == "success"])
        failed = len(results) - successful
        
        return StatusResponse(
            status="completed",
            message=f"Batch engagement generation: {successful} successful, {failed} failed",
            timestamp=datetime.utcnow(),
            data={
                "total_processed": len(post_ids),
                "successful": successful,
                "failed": failed,
                "results": results
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in batch engagement generation: {str(e)}"
        )

@router.get("/performance-insights", response_model=PerformanceInsightsResponse)
async def get_performance_insights(
    days: int = 7,
    current_user: dict = Depends(get_current_user)
):
    """Get performance insights for the specified period"""
    try:
        analytics_collector = AnalyticsCollector()
        insights = analytics_collector.get_performance_insights(days=days)
        
        if "message" in insights:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=insights["message"]
            )
        
        return PerformanceInsightsResponse(
            period_summary=insights["period_summary"],
            platform_performance=insights["platform_performance"],
            top_performers=insights["top_performers"],
            underperformers=insights["underperformers"],
            recommendations=insights["recommendations"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving performance insights: {str(e)}"
        )

@router.get("/weekly-strategy", response_model=WeeklyStrategyResponse)
async def get_weekly_strategy(
    current_user: dict = Depends(get_current_user)
):
    """Get weekly strategy recommendations"""
    try:
        analytics_collector = AnalyticsCollector()
        strategy = analytics_collector.generate_weekly_strategy()
        
        if "message" in strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=strategy["message"]
            )
        
        return WeeklyStrategyResponse(
            week_start=datetime.fromisoformat(strategy["week_start"]),
            top_performers=strategy["top_performers"],
            underperformers=strategy["underperformers"],
            recommendations=strategy["recommendations"],
            suggested_tones=strategy["suggested_tones"],
            suggested_languages=strategy["suggested_languages"],
            metadata=strategy["metadata"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating weekly strategy: {str(e)}"
        )

@router.get("/post-analytics/{post_id}")
async def get_post_analytics(
    post_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get analytics for a specific post"""
    try:
        analytics_collector = AnalyticsCollector()
        
        # Search through analytics files
        analytics_data = []
        analytics_dir = analytics_collector.analytics_db_path
        
        if os.path.exists(analytics_dir):
            for filename in os.listdir(analytics_dir):
                if filename.startswith("analytics_") and filename.endswith(".json"):
                    filepath = os.path.join(analytics_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            daily_data = json.load(f)
                            for entry in daily_data:
                                if entry["post_id"] == post_id:
                                    analytics_data.append(entry)
                    except Exception:
                        continue
        
        if not analytics_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No analytics found for this post"
            )
        
        # Return the most recent analytics entry
        latest_analytics = max(analytics_data, key=lambda x: x["created_at"])
        
        return {
            "post_id": post_id,
            "analytics": latest_analytics,
            "historical_data": analytics_data,
            "total_entries": len(analytics_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving post analytics: {str(e)}"
        )

@router.get("/platform-comparison")
async def get_platform_comparison(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Compare performance across platforms"""
    try:
        analytics_collector = AnalyticsCollector()
        insights = analytics_collector.get_performance_insights(days=days)
        
        if "message" in insights:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=insights["message"]
            )
        
        platform_performance = insights.get("platform_performance", {})
        
        # Calculate platform rankings
        platform_rankings = []
        for platform, stats in platform_performance.items():
            platform_rankings.append({
                "platform": platform,
                "avg_engagement_rate": stats.get("avg_engagement_rate", 0),
                "total_posts": stats.get("posts", 0),
                "avg_views": stats.get("avg_views", 0),
                "avg_likes": stats.get("avg_likes", 0),
                "avg_shares": stats.get("avg_shares", 0),
                "avg_comments": stats.get("avg_comments", 0)
            })
        
        # Sort by engagement rate
        platform_rankings.sort(key=lambda x: x["avg_engagement_rate"], reverse=True)
        
        return {
            "comparison_period": f"{days} days",
            "platform_rankings": platform_rankings,
            "best_platform": platform_rankings[0]["platform"] if platform_rankings else None,
            "total_platforms": len(platform_rankings),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error comparing platforms: {str(e)}"
        )

@router.get("/engagement-trends")
async def get_engagement_trends(
    days: int = 30,
    platform: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get engagement trends over time"""
    try:
        analytics_collector = AnalyticsCollector()
        
        # Load analytics data for the specified period
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        daily_trends = {}
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime("%Y%m%d")
            filename = f"analytics_{date_str}.json"
            filepath = os.path.join(analytics_collector.analytics_db_path, filename)
            
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    daily_data = json.load(f)
                    
                    # Filter by platform if specified
                    if platform:
                        daily_data = [entry for entry in daily_data if entry["platform"] == platform]
                    
                    if daily_data:
                        # Calculate daily averages
                        total_engagement = sum(entry["metrics"]["engagement_rate"] for entry in daily_data)
                        avg_engagement = total_engagement / len(daily_data)
                        
                        daily_trends[date_str] = {
                            "date": current_date.strftime("%Y-%m-%d"),
                            "posts_count": len(daily_data),
                            "avg_engagement_rate": avg_engagement,
                            "total_views": sum(entry["metrics"]["views"] for entry in daily_data),
                            "total_likes": sum(entry["metrics"]["likes"] for entry in daily_data)
                        }
            
            current_date += timedelta(days=1)
        
        # Convert to list and sort by date
        trends_list = list(daily_trends.values())
        trends_list.sort(key=lambda x: x["date"])
        
        return {
            "period": f"{days} days",
            "platform_filter": platform,
            "trends": trends_list,
            "total_days": len(trends_list),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving engagement trends: {str(e)}"
        )
