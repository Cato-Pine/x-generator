"""Trending cache database operations."""

from typing import Optional, List
from datetime import datetime, timedelta
from supabase import Client
from src.db.supabase_client import get_supabase


class TrendingCacheDB:
    """Database operations for tracking shown/skipped trending tweets."""

    def __init__(self, client: Optional[Client] = None):
        self.client = client or get_supabase()

    def add(self, tweet_id: str, content: str, username: str) -> dict:
        """Add a tweet to the cache as 'shown'."""
        data = {
            "tweet_id": tweet_id,
            "content": content,
            "username": username,
            "status": "shown",
            "shown_at": datetime.utcnow().isoformat()
        }
        result = self.client.table("trending_cache").upsert(
            data,
            on_conflict="tweet_id"
        ).execute()
        return result.data[0] if result.data else None

    def get_by_tweet_id(self, tweet_id: str) -> Optional[dict]:
        """Get a cached tweet by its ID."""
        result = self.client.table("trending_cache").select("*").eq(
            "tweet_id", tweet_id
        ).execute()
        return result.data[0] if result.data else None

    def is_seen(self, tweet_id: str) -> bool:
        """Check if a tweet has already been shown."""
        return self.get_by_tweet_id(tweet_id) is not None

    def mark_skipped(self, tweet_id: str) -> Optional[dict]:
        """Mark a tweet as skipped."""
        result = self.client.table("trending_cache").update({
            "status": "skipped"
        }).eq("tweet_id", tweet_id).execute()
        return result.data[0] if result.data else None

    def mark_replied(self, tweet_id: str) -> Optional[dict]:
        """Mark a tweet as replied to."""
        result = self.client.table("trending_cache").update({
            "status": "replied"
        }).eq("tweet_id", tweet_id).execute()
        return result.data[0] if result.data else None

    def get_all(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """Get cached tweets with optional filtering."""
        query = self.client.table("trending_cache").select("*")

        if status:
            query = query.eq("status", status)

        query = query.order("shown_at", desc=True).range(offset, offset + limit - 1)
        result = query.execute()
        return result.data or []

    def get_recent(self, days: int = 7) -> List[dict]:
        """Get tweets shown in the last N days."""
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        result = self.client.table("trending_cache").select("*").gte(
            "shown_at", cutoff
        ).order("shown_at", desc=True).execute()
        return result.data or []

    def get_replied(self, limit: int = 50) -> List[dict]:
        """Get tweets we've replied to."""
        return self.get_all(status="replied", limit=limit)

    def get_skipped(self, limit: int = 50) -> List[dict]:
        """Get tweets we've skipped."""
        return self.get_all(status="skipped", limit=limit)

    def cleanup_old(self, days: int = 30) -> int:
        """Remove cache entries older than N days."""
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        result = self.client.table("trending_cache").delete().lt(
            "shown_at", cutoff
        ).execute()
        return len(result.data) if result.data else 0

    def count_by_status(self) -> dict:
        """Get counts by status."""
        all_entries = self.client.table("trending_cache").select("status").execute()
        entries = all_entries.data or []

        counts = {"shown": 0, "skipped": 0, "replied": 0}
        for entry in entries:
            status = entry.get("status", "shown")
            counts[status] = counts.get(status, 0) + 1

        return counts
