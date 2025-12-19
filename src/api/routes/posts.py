"""Post management routes."""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from src.api.models import (
    PostResponse,
    CreatePostRequest,
    UpdatePostRequest,
    PostStatus,
    PostType,
)
from src.db.posts import PostsDB

router = APIRouter(prefix="/posts", tags=["posts"])


def db_to_response(post: dict) -> PostResponse:
    """Convert database record to response model."""
    return PostResponse(
        id=post["id"],
        content=post["content"],
        topic=post.get("topic"),
        post_type=PostType(post.get("post_type", "original")),
        format_type=post.get("format_type"),
        virtue=post.get("virtue"),
        tweets=post.get("tweets"),
        tweet_count=post.get("tweet_count", 1),
        reply_to_tweet_id=post.get("reply_to_tweet_id"),
        reply_to_content=post.get("reply_to_content"),
        reply_to_username=post.get("reply_to_username"),
        model=post.get("model"),
        citations=post.get("citations"),
        status=PostStatus(post.get("status", "pending_review")),
        is_evergreen=post.get("is_evergreen", True),
        recycle_count=post.get("recycle_count", 0),
        created_at=post["created_at"],
        approved_at=post.get("approved_at"),
        posted_at=post.get("posted_at"),
        x_post_id=post.get("x_post_id"),
    )


@router.get("", response_model=List[PostResponse])
async def list_posts(
    status: Optional[str] = Query(None, description="Filter by status"),
    post_type: Optional[str] = Query(None, description="Filter by post type (original/reply)"),
    virtue: Optional[str] = Query(None, description="Filter by virtue"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List all posts with optional filtering."""
    posts_db = PostsDB()
    posts = posts_db.get_all(
        status=status,
        post_type=post_type,
        virtue=virtue,
        limit=limit,
        offset=offset
    )
    return [db_to_response(p) for p in posts]


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: str):
    """Get a specific post by ID."""
    posts_db = PostsDB()
    post = posts_db.get_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_to_response(post)


@router.post("", response_model=PostResponse)
async def create_post(request: CreatePostRequest):
    """Create a new post manually."""
    posts_db = PostsDB()
    post_data = {
        "content": request.content,
        "topic": request.topic,
        "post_type": request.post_type.value,
        "format_type": request.format_type or "short",
        "virtue": request.virtue,
        "tweets": [request.content],
        "tweet_count": 1,
        "reply_to_tweet_id": request.reply_to_tweet_id,
        "reply_to_content": request.reply_to_content,
        "reply_to_username": request.reply_to_username,
        "is_evergreen": request.is_evergreen,
        "status": "pending_review"
    }
    post = posts_db.create(post_data)
    if not post:
        raise HTTPException(status_code=500, detail="Failed to create post")
    return db_to_response(post)


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(post_id: str, request: UpdatePostRequest):
    """Update a post."""
    posts_db = PostsDB()

    update_data = {}
    if request.content is not None:
        update_data["content"] = request.content
    if request.status is not None:
        update_data["status"] = request.status.value
    if request.virtue is not None:
        update_data["virtue"] = request.virtue
    if request.is_evergreen is not None:
        update_data["is_evergreen"] = request.is_evergreen

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    post = posts_db.update(post_id, update_data)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_to_response(post)


@router.post("/{post_id}/approve", response_model=PostResponse)
async def approve_post(post_id: str):
    """Approve a post for posting."""
    posts_db = PostsDB()
    post = posts_db.approve(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_to_response(post)


@router.post("/{post_id}/skip", response_model=PostResponse)
async def skip_post(post_id: str):
    """Skip a post (mark as skipped)."""
    posts_db = PostsDB()
    post = posts_db.skip(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_to_response(post)


@router.delete("/{post_id}")
async def delete_post(post_id: str):
    """Delete a post."""
    posts_db = PostsDB()
    if not posts_db.delete(post_id):
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted"}


@router.get("/evergreen/candidates", response_model=List[PostResponse])
async def get_evergreen_candidates(
    min_age_days: int = Query(30, description="Minimum age in days"),
    limit: int = Query(10, ge=1, le=50),
):
    """Get posts eligible for evergreen recycling."""
    posts_db = PostsDB()
    posts = posts_db.get_evergreen_candidates(min_age_days=min_age_days, limit=limit)
    return [db_to_response(p) for p in posts]
