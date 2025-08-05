"""
Agent D: Scheduler & Publisher Simulator
Handles scheduling and simulated publishing to multiple platforms
"""

import uuid
import json
import os
import asyncio
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import random

class PublishStatus(Enum):
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ScheduledPost:
    post_id: str
    content_id: str
    platform: str
    content: str
    scheduled_time: datetime
    status: PublishStatus
    metadata: Dict[str, Any]
    created_at: datetime
    published_at: Optional[datetime] = None
    error_message: Optional[str] = None

class PlatformSimulator:
    """Simulates platform-specific publishing"""
    
    def __init__(self):
        # Mock API endpoints for different platforms
        self.mock_endpoints = {
            "twitter": "https://api.twitter.com/2/tweets",
            "instagram": "https://graph.instagram.com/v12.0/me/media",
            "linkedin": "https://api.linkedin.com/v2/ugcPosts",
            "spotify": "https://api.spotify.com/v1/episodes"
        }
        
        # Platform-specific formatting
        self.platform_formatters = {
            "twitter": self._format_twitter_post,
            "instagram": self._format_instagram_post,
            "linkedin": self._format_linkedin_post,
            "spotify": self._format_spotify_post
        }
    
    async def simulate_publish(self, post: ScheduledPost) -> Dict[str, Any]:
        """Simulate publishing to a platform"""
        try:
            # Format content for platform
            formatter = self.platform_formatters.get(post.platform)
            if not formatter:
                raise Exception(f"Unsupported platform: {post.platform}")
            
            formatted_content = formatter(post.content, post.metadata)
            
            # Simulate API call
            result = await self._mock_api_call(post.platform, formatted_content)
            
            # Simulate success/failure (90% success rate)
            if random.random() < 0.9:
                return {
                    "status": "success",
                    "platform_post_id": f"{post.platform}_{uuid.uuid4().hex[:8]}",
                    "published_at": datetime.utcnow().isoformat(),
                    "platform_url": f"https://{post.platform}.com/post/{uuid.uuid4().hex[:8]}",
                    "formatted_content": formatted_content,
                    "api_response": result
                }
            else:
                return {
                    "status": "failed",
                    "error": "Platform API error (simulated)",
                    "retry_after": 300  # 5 minutes
                }
                
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _mock_api_call(self, platform: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Mock API call to platform"""
        endpoint = self.mock_endpoints.get(platform)
        
        # Simulate network delay
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Mock response
        return {
            "mock_endpoint": endpoint,
            "request_payload": content,
            "response_code": 200,
            "response_time_ms": random.randint(100, 500),
            "rate_limit_remaining": random.randint(100, 1000)
        }
    
    def _format_twitter_post(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Format content for Twitter"""
        # Truncate to 280 characters if needed
        if len(content) > 280:
            content = content[:277] + "..."
        
        return {
            "text": content,
            "media": metadata.get("media_urls", []),
            "reply_settings": "everyone"
        }
    
    def _format_instagram_post(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Format content for Instagram"""
        return {
            "caption": content,
            "media_type": "CAROUSEL_ALBUM" if metadata.get("media_urls") else "TEXT",
            "media_url": metadata.get("media_urls", [None])[0],
            "access_token": "mock_token"
        }
    
    def _format_linkedin_post(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Format content for LinkedIn"""
        return {
            "author": "urn:li:person:mock_user",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
    
    def _format_spotify_post(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Format content for Spotify (podcast episode)"""
        return {
            "name": f"Episode: {content[:50]}...",
            "description": content,
            "audio_preview_url": metadata.get("audio_url"),
            "duration_ms": int(metadata.get("duration", 30) * 1000),
            "language": metadata.get("language", "en")
        }

class SchedulerPublisher:
    """Agent D: Scheduler & Publisher Simulator"""
    
    def __init__(self):
        self.scheduled_posts: Dict[str, ScheduledPost] = {}
        self.platform_simulator = PlatformSimulator()
        self.scheduler_db_path = "./scheduler_db"
        os.makedirs(self.scheduler_db_path, exist_ok=True)
        
        # Load existing scheduled posts
        self._load_scheduled_posts()
    
    def schedule_post(
        self,
        content_id: str,
        platform: str,
        content: str,
        scheduled_time: datetime,
        metadata: Dict[str, Any] = None
    ) -> ScheduledPost:
        """Schedule a post for publishing"""
        
        post_id = str(uuid.uuid4())
        
        scheduled_post = ScheduledPost(
            post_id=post_id,
            content_id=content_id,
            platform=platform,
            content=content,
            scheduled_time=scheduled_time,
            status=PublishStatus.SCHEDULED,
            metadata=metadata or {},
            created_at=datetime.utcnow()
        )
        
        self.scheduled_posts[post_id] = scheduled_post
        self._save_scheduled_posts()
        
        return scheduled_post
    
    async def process_scheduled_posts(self) -> List[Dict[str, Any]]:
        """Process posts that are due for publishing"""
        current_time = datetime.utcnow()
        processed_posts = []
        
        for post_id, post in self.scheduled_posts.items():
            if (post.status == PublishStatus.SCHEDULED and 
                post.scheduled_time <= current_time):
                
                # Attempt to publish
                result = await self.platform_simulator.simulate_publish(post)
                
                if result["status"] == "success":
                    post.status = PublishStatus.PUBLISHED
                    post.published_at = datetime.utcnow()
                    post.metadata.update(result)
                else:
                    post.status = PublishStatus.FAILED
                    post.error_message = result.get("error", "Unknown error")
                
                processed_posts.append({
                    "post_id": post_id,
                    "platform": post.platform,
                    "status": post.status.value,
                    "result": result
                })
        
        self._save_scheduled_posts()
        return processed_posts
    
    def get_scheduled_posts(
        self,
        platform: Optional[str] = None,
        status: Optional[PublishStatus] = None
    ) -> List[Dict[str, Any]]:
        """Get scheduled posts with optional filtering"""
        
        posts = []
        for post in self.scheduled_posts.values():
            if platform and post.platform != platform:
                continue
            if status and post.status != status:
                continue
            
            posts.append({
                "post_id": post.post_id,
                "content_id": post.content_id,
                "platform": post.platform,
                "content": post.content,
                "scheduled_time": post.scheduled_time.isoformat(),
                "status": post.status.value,
                "metadata": post.metadata,
                "created_at": post.created_at.isoformat(),
                "published_at": post.published_at.isoformat() if post.published_at else None,
                "error_message": post.error_message
            })
        
        return sorted(posts, key=lambda x: x["scheduled_time"])
    
    def cancel_scheduled_post(self, post_id: str) -> bool:
        """Cancel a scheduled post"""
        if post_id in self.scheduled_posts:
            post = self.scheduled_posts[post_id]
            if post.status == PublishStatus.SCHEDULED:
                post.status = PublishStatus.CANCELLED
                self._save_scheduled_posts()
                return True
        return False
    
    def reschedule_post(self, post_id: str, new_time: datetime) -> bool:
        """Reschedule a post"""
        if post_id in self.scheduled_posts:
            post = self.scheduled_posts[post_id]
            if post.status == PublishStatus.SCHEDULED:
                post.scheduled_time = new_time
                self._save_scheduled_posts()
                return True
        return False
    
    def get_publishing_stats(self) -> Dict[str, Any]:
        """Get publishing statistics"""
        stats = {
            "total_posts": len(self.scheduled_posts),
            "by_status": {},
            "by_platform": {},
            "success_rate": 0.0
        }
        
        for post in self.scheduled_posts.values():
            # Count by status
            status = post.status.value
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # Count by platform
            platform = post.platform
            stats["by_platform"][platform] = stats["by_platform"].get(platform, 0) + 1
        
        # Calculate success rate
        published = stats["by_status"].get("published", 0)
        failed = stats["by_status"].get("failed", 0)
        total_attempted = published + failed
        
        if total_attempted > 0:
            stats["success_rate"] = published / total_attempted
        
        return stats
    
    def _save_scheduled_posts(self):
        """Save scheduled posts to file"""
        data = {}
        for post_id, post in self.scheduled_posts.items():
            data[post_id] = {
                "post_id": post.post_id,
                "content_id": post.content_id,
                "platform": post.platform,
                "content": post.content,
                "scheduled_time": post.scheduled_time.isoformat(),
                "status": post.status.value,
                "metadata": post.metadata,
                "created_at": post.created_at.isoformat(),
                "published_at": post.published_at.isoformat() if post.published_at else None,
                "error_message": post.error_message
            }
        
        filepath = os.path.join(self.scheduler_db_path, "scheduled_posts.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_scheduled_posts(self):
        """Load scheduled posts from file"""
        filepath = os.path.join(self.scheduler_db_path, "scheduled_posts.json")
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for post_id, post_data in data.items():
                    post = ScheduledPost(
                        post_id=post_data["post_id"],
                        content_id=post_data["content_id"],
                        platform=post_data["platform"],
                        content=post_data["content"],
                        scheduled_time=datetime.fromisoformat(post_data["scheduled_time"]),
                        status=PublishStatus(post_data["status"]),
                        metadata=post_data["metadata"],
                        created_at=datetime.fromisoformat(post_data["created_at"]),
                        published_at=datetime.fromisoformat(post_data["published_at"]) if post_data["published_at"] else None,
                        error_message=post_data["error_message"]
                    )
                    self.scheduled_posts[post_id] = post
                    
            except Exception as e:
                print(f"Error loading scheduled posts: {e}")

# Global scheduler instance
scheduler = SchedulerPublisher()

def get_scheduler() -> SchedulerPublisher:
    """Get the global scheduler instance"""
    return scheduler
