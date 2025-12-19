"""Queue database operations."""

from typing import Optional, List
from datetime import datetime
from supabase import Client
from src.db.supabase_client import get_supabase


class QueueDB:
    """Database operations for the post queue."""

    def __init__(self, client: Optional[Client] = None):
        self.client = client or get_supabase()

    def create(self, post_id: str, scheduled_for: datetime) -> dict:
        """Add a post to the queue."""
        data = {
            "post_id": post_id,
            "scheduled_for": scheduled_for.isoformat(),
            "status": "pending"
        }
        result = self.client.table("queue").insert(data).execute()
        return result.data[0] if result.data else None

    def get_by_id(self, queue_id: str) -> Optional[dict]:
        """Get a queue entry by ID."""
        result = self.client.table("queue").select(
            "*, posts(*)"
        ).eq("id", queue_id).execute()
        return result.data[0] if result.data else None

    def get_all(
        self,
        status: Optional[str] = None,
        post_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """Get all queue entries with optional filtering."""
        query = self.client.table("queue").select("*, posts(*)")

        if status:
            query = query.eq("status", status)

        query = query.order("scheduled_for", desc=False).range(offset, offset + limit - 1)
        result = query.execute()

        data = result.data or []
        if post_type:
            data = [q for q in data if q.get("posts", {}).get("post_type") == post_type]

        return data

    def get_pending_to_post(self, post_type: Optional[str] = None) -> List[dict]:
        """Get approved posts that are due to be posted."""
        now = datetime.utcnow().isoformat()

        query = self.client.table("queue").select(
            "*, posts(*)"
        ).eq(
            "status", "approved"
        ).lte(
            "scheduled_for", now
        ).order("scheduled_for", desc=False)

        result = query.execute()
        data = result.data or []

        if post_type:
            data = [q for q in data if q.get("posts", {}).get("post_type") == post_type]

        return data

    def get_next_for_review(self, post_type: Optional[str] = None) -> Optional[dict]:
        """Get the next post pending review."""
        query = self.client.table("queue").select(
            "*, posts(*)"
        ).eq(
            "status", "pending"
        ).order("scheduled_for", desc=False).limit(1)

        result = query.execute()
        data = result.data or []

        if post_type:
            data = [q for q in data if q.get("posts", {}).get("post_type") == post_type]

        return data[0] if data else None

    def update(self, queue_id: str, data: dict) -> Optional[dict]:
        """Update a queue entry."""
        result = self.client.table("queue").update(data).eq("id", queue_id).execute()
        return result.data[0] if result.data else None

    def approve(self, queue_id: str) -> Optional[dict]:
        """Approve a queue entry."""
        return self.update(queue_id, {"status": "approved"})

    def mark_posted(self, queue_id: str) -> Optional[dict]:
        """Mark a queue entry as posted."""
        return self.update(queue_id, {
            "status": "posted",
            "posted_at": datetime.utcnow().isoformat()
        })

    def mark_failed(self, queue_id: str, error: str) -> Optional[dict]:
        """Mark a queue entry as failed."""
        return self.update(queue_id, {
            "status": "failed",
            "error_message": error
        })

    def delete(self, queue_id: str) -> bool:
        """Delete a queue entry."""
        result = self.client.table("queue").delete().eq("id", queue_id).execute()
        return bool(result.data)

    def get_by_post_id(self, post_id: str) -> Optional[dict]:
        """Get queue entry by post ID."""
        result = self.client.table("queue").select(
            "*, posts(*)"
        ).eq("post_id", post_id).execute()
        return result.data[0] if result.data else None

    def get_next_scheduled(self) -> Optional[dict]:
        """Get the next scheduled post (for scheduler)."""
        now = datetime.utcnow().isoformat()
        result = self.client.table("queue").select(
            "*, posts(*)"
        ).eq(
            "status", "approved"
        ).gt(
            "scheduled_for", now
        ).order("scheduled_for", desc=False).limit(1).execute()
        return result.data[0] if result.data else None
