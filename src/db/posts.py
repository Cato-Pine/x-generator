"""Post database operations."""

import hashlib
from typing import Optional, List
from datetime import datetime, timedelta
from supabase import Client
from src.db.supabase_client import get_supabase


def content_hash(content: str) -> str:
    """Generate a hash of content for duplicate detection."""
    normalized = " ".join(content.lower().split())
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


class PostsDB:
    """Database operations for posts."""

    def __init__(self, client: Optional[Client] = None):
        self.client = client or get_supabase()

    def create(self, data: dict) -> dict:
        """Create a new post with content hash for duplicate detection."""
        if "content" in data:
            data["content_hash"] = content_hash(data["content"])
        result = self.client.table("posts").insert(data).execute()
        return result.data[0] if result.data else None

    def is_duplicate(self, content: str, days_lookback: int = 30) -> bool:
        """Check if similar content was posted recently."""
        hash_value = content_hash(content)
        cutoff = (datetime.utcnow() - timedelta(days=days_lookback)).isoformat()
        result = self.client.table("posts").select("id").eq(
            "content_hash", hash_value
        ).gte("created_at", cutoff).execute()
        return bool(result.data)

    def get_by_id(self, post_id: str) -> Optional[dict]:
        """Get a post by ID."""
        result = self.client.table("posts").select("*").eq("id", post_id).execute()
        return result.data[0] if result.data else None

    def get_all(
        self,
        status: Optional[str] = None,
        post_type: Optional[str] = None,
        virtue: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """Get all posts with optional filtering."""
        query = self.client.table("posts").select("*")

        if status:
            query = query.eq("status", status)
        if post_type:
            query = query.eq("post_type", post_type)
        if virtue:
            query = query.eq("virtue", virtue)

        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
        result = query.execute()
        return result.data or []

    def update(self, post_id: str, data: dict) -> Optional[dict]:
        """Update a post."""
        result = self.client.table("posts").update(data).eq("id", post_id).execute()
        return result.data[0] if result.data else None

    def approve(self, post_id: str) -> Optional[dict]:
        """Approve a post for posting."""
        return self.update(post_id, {
            "status": "approved",
            "approved_at": datetime.utcnow().isoformat()
        })

    def mark_posted(self, post_id: str, x_post_id: str) -> Optional[dict]:
        """Mark a post as posted."""
        return self.update(post_id, {
            "status": "posted",
            "posted_at": datetime.utcnow().isoformat(),
            "x_post_id": x_post_id
        })

    def skip(self, post_id: str) -> Optional[dict]:
        """Skip a post."""
        return self.update(post_id, {"status": "skipped"})

    def get_evergreen_candidates(self, min_age_days: int = 30, limit: int = 10) -> List[dict]:
        """Get posts eligible for evergreen recycling."""
        result = self.client.table("posts").select("*").eq(
            "is_evergreen", True
        ).eq(
            "status", "posted"
        ).order(
            "recycle_count", desc=False
        ).order(
            "posted_at", desc=False
        ).limit(limit).execute()

        return result.data or []

    def increment_recycle_count(self, post_id: str) -> Optional[dict]:
        """Increment the recycle count for a post."""
        post = self.get_by_id(post_id)
        if post:
            return self.update(post_id, {
                "recycle_count": post.get("recycle_count", 0) + 1
            })
        return None

    def delete(self, post_id: str) -> bool:
        """Delete a post."""
        result = self.client.table("posts").delete().eq("id", post_id).execute()
        return bool(result.data)

    def count_posted_last_24h(self) -> int:
        """Count posts that were posted in the last 24 hours."""
        cutoff = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        result = self.client.table("posts").select(
            "id", count="exact"
        ).eq(
            "status", "posted"
        ).gte(
            "posted_at", cutoff
        ).execute()
        return result.count or 0

    def count_posted_today(self) -> int:
        """Count posts posted today (since midnight UTC)."""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        result = self.client.table("posts").select(
            "id", count="exact"
        ).eq(
            "status", "posted"
        ).gte(
            "posted_at", today_start
        ).execute()
        return result.count or 0

    def count_posted_this_month(self) -> int:
        """Count posts posted this month (since 1st of month UTC)."""
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        result = self.client.table("posts").select(
            "id", count="exact"
        ).eq(
            "status", "posted"
        ).gte(
            "posted_at", month_start
        ).execute()
        return result.count or 0

    def get_rate_limit_status(self) -> dict:
        """Get current rate limit status with counts."""
        from src.db.settings import SettingsDB
        settings = SettingsDB(self.client)
        limits = settings.get_rate_limits()

        rolling_24h_count = self.count_posted_last_24h()
        today_count = self.count_posted_today()
        month_count = self.count_posted_this_month()

        return {
            "daily_limit": limits["max_daily_tweets"],
            "rolling_24h_used": rolling_24h_count,
            "rolling_24h_remaining": max(0, limits["max_daily_tweets"] - rolling_24h_count),
            "today_count": today_count,
            "month_count": month_count,
            "can_post": (
                limits["enabled"] is False or
                rolling_24h_count < limits["max_daily_tweets"]
            ),
            "rate_limiting_enabled": limits["enabled"]
        }

    def get_by_virtue(self, virtue: str, limit: int = 50) -> List[dict]:
        """Get posts by stoic virtue."""
        result = self.client.table("posts").select("*").eq(
            "virtue", virtue
        ).order("created_at", desc=True).limit(limit).execute()
        return result.data or []
