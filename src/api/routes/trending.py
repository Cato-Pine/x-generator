"""Trending discovery routes."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from src.api.models import TrendingPostResponse
from src.twitter.twitterapi_client import TwitterAPIClient
from src.db.trending_cache import TrendingCacheDB
from src.db.settings import SettingsDB

router = APIRouter(prefix="/trending", tags=["trending"])


@router.get("", response_model=List[TrendingPostResponse])
async def get_trending_posts(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of posts"),
    exclude_seen: bool = Query(True, description="Exclude already shown tweets"),
):
    """Get trending posts matching configured topics."""
    settings_db = SettingsDB()
    config = settings_db.get_trending_config()
    topics = config.get("topics", ["stoicism", "philosophy", "self-improvement"])

    client = TwitterAPIClient()

    try:
        posts = await client.search_trending(topics, limit=limit * 2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trending: {str(e)}")

    cache_db = TrendingCacheDB()
    results = []

    for post in posts:
        if exclude_seen and cache_db.is_seen(post.tweet_id):
            continue

        cache_db.add(post.tweet_id, post.content, post.username)

        results.append(TrendingPostResponse(
            tweet_id=post.tweet_id,
            content=post.content,
            username=post.username,
            likes=post.likes,
            retweets=post.retweets,
            relevance_score=post.relevance_score,
            cache_status="new" if not cache_db.is_seen(post.tweet_id) else "shown",
        ))

        if len(results) >= limit:
            break

    return results


@router.get("/topics")
async def get_trending_topics():
    """Get configured trending search topics."""
    settings_db = SettingsDB()
    config = settings_db.get_trending_config()
    return {"topics": config.get("topics", [])}


@router.put("/topics")
async def update_trending_topics(topics: List[str]):
    """Update trending search topics."""
    settings_db = SettingsDB()
    config = settings_db.get_trending_config()
    config["topics"] = topics
    settings_db.set_trending_config(config)
    return {"topics": topics}


@router.get("/cache", response_model=List[TrendingPostResponse])
async def get_cached_trending(
    status: Optional[str] = Query(None, description="Filter by status: shown, skipped, replied"),
    limit: int = Query(50, ge=1, le=100),
):
    """Get cached trending tweets."""
    cache_db = TrendingCacheDB()
    entries = cache_db.get_all(status=status, limit=limit)

    return [
        TrendingPostResponse(
            tweet_id=e["tweet_id"],
            content=e.get("content", ""),
            username=e.get("username", ""),
            likes=None,
            retweets=None,
            relevance_score=None,
            cache_status=e.get("status"),
        )
        for e in entries
    ]


@router.post("/cache/{tweet_id}/skip")
async def skip_trending_tweet(tweet_id: str):
    """Mark a trending tweet as skipped."""
    cache_db = TrendingCacheDB()
    entry = cache_db.mark_skipped(tweet_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Tweet not found in cache")
    return {"message": "Tweet marked as skipped"}


@router.post("/cache/{tweet_id}/replied")
async def mark_replied(tweet_id: str):
    """Mark a trending tweet as replied to."""
    cache_db = TrendingCacheDB()
    entry = cache_db.mark_replied(tweet_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Tweet not found in cache")
    return {"message": "Tweet marked as replied"}


@router.get("/cache/stats")
async def get_cache_stats():
    """Get trending cache statistics."""
    cache_db = TrendingCacheDB()
    return cache_db.count_by_status()


@router.delete("/cache/cleanup")
async def cleanup_cache(days: int = Query(30, description="Remove entries older than N days")):
    """Clean up old cache entries."""
    cache_db = TrendingCacheDB()
    count = cache_db.cleanup_old(days=days)
    return {"deleted": count}
