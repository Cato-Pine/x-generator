"""Queue management routes."""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from src.api.models import QueueResponse, QueuePostRequest, PostResponse, PostType, PostStatus
from src.db.queue import QueueDB
from src.db.posts import PostsDB

router = APIRouter(prefix="/queue", tags=["queue"])


def db_to_response(queue_entry: dict) -> QueueResponse:
    """Convert database record to response model."""
    post_data = queue_entry.get("posts")
    post_response = None

    if post_data:
        post_response = PostResponse(
            id=post_data["id"],
            content=post_data["content"],
            topic=post_data.get("topic"),
            post_type=PostType(post_data.get("post_type", "original")),
            format_type=post_data.get("format_type"),
            virtue=post_data.get("virtue"),
            tweets=post_data.get("tweets"),
            tweet_count=post_data.get("tweet_count", 1),
            reply_to_tweet_id=post_data.get("reply_to_tweet_id"),
            reply_to_content=post_data.get("reply_to_content"),
            reply_to_username=post_data.get("reply_to_username"),
            model=post_data.get("model"),
            citations=post_data.get("citations"),
            status=PostStatus(post_data.get("status", "pending_review")),
            is_evergreen=post_data.get("is_evergreen", True),
            recycle_count=post_data.get("recycle_count", 0),
            created_at=post_data["created_at"],
            approved_at=post_data.get("approved_at"),
            posted_at=post_data.get("posted_at"),
            x_post_id=post_data.get("x_post_id"),
        )

    return QueueResponse(
        id=queue_entry["id"],
        post_id=queue_entry["post_id"],
        scheduled_for=queue_entry["scheduled_for"],
        status=queue_entry.get("status", "pending"),
        posted_at=queue_entry.get("posted_at"),
        error_message=queue_entry.get("error_message"),
        created_at=queue_entry["created_at"],
        post=post_response,
    )


@router.get("", response_model=List[QueueResponse])
async def list_queue(
    status: Optional[str] = Query(None, description="Filter by status"),
    post_type: Optional[str] = Query(None, description="Filter by post type"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List queue entries with optional filtering."""
    queue_db = QueueDB()
    entries = queue_db.get_all(
        status=status,
        post_type=post_type,
        limit=limit,
        offset=offset
    )
    return [db_to_response(e) for e in entries]


@router.get("/next", response_model=Optional[QueueResponse])
async def get_next_for_review(
    post_type: Optional[str] = Query(None, description="Filter by post type"),
):
    """Get the next post pending review."""
    queue_db = QueueDB()
    entry = queue_db.get_next_for_review(post_type=post_type)
    if not entry:
        return None
    return db_to_response(entry)


@router.get("/pending-to-post", response_model=List[QueueResponse])
async def get_pending_to_post(
    post_type: Optional[str] = Query(None, description="Filter by post type"),
):
    """Get approved posts that are due to be posted."""
    queue_db = QueueDB()
    entries = queue_db.get_pending_to_post(post_type=post_type)
    return [db_to_response(e) for e in entries]


@router.get("/rate-limit")
async def get_rate_limit_status():
    """Get current X API rate limit status."""
    posts_db = PostsDB()
    return posts_db.get_rate_limit_status()


@router.post("", response_model=QueueResponse)
async def add_to_queue(request: QueuePostRequest):
    """Add a post to the queue."""
    queue_db = QueueDB()
    entry = queue_db.create(request.post_id, request.scheduled_for)
    if not entry:
        raise HTTPException(status_code=500, detail="Failed to add to queue")

    full_entry = queue_db.get_by_id(entry["id"])
    return db_to_response(full_entry)


@router.post("/{queue_id}/approve", response_model=QueueResponse)
async def approve_queue_entry(queue_id: str):
    """Approve a queue entry."""
    queue_db = QueueDB()
    entry = queue_db.approve(queue_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")

    full_entry = queue_db.get_by_id(queue_id)
    return db_to_response(full_entry)


@router.post("/{queue_id}/mark-posted", response_model=QueueResponse)
async def mark_queue_posted(queue_id: str):
    """Mark a queue entry as posted."""
    queue_db = QueueDB()
    entry = queue_db.mark_posted(queue_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")

    full_entry = queue_db.get_by_id(queue_id)
    return db_to_response(full_entry)


@router.post("/{queue_id}/mark-failed")
async def mark_queue_failed(queue_id: str, error: str = Query(...)):
    """Mark a queue entry as failed."""
    queue_db = QueueDB()
    entry = queue_db.mark_failed(queue_id, error)
    if not entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")

    full_entry = queue_db.get_by_id(queue_id)
    return db_to_response(full_entry)


@router.delete("/{queue_id}")
async def delete_queue_entry(queue_id: str):
    """Delete a queue entry."""
    queue_db = QueueDB()
    if not queue_db.delete(queue_id):
        raise HTTPException(status_code=404, detail="Queue entry not found")
    return {"message": "Queue entry deleted"}
