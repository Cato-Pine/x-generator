"""Pydantic models for API requests and responses."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class PostType(str, Enum):
    ORIGINAL = "original"
    REPLY = "reply"


class FormatType(str, Enum):
    SHORT = "short"
    THREAD = "thread"
    LONG = "long"


class Virtue(str, Enum):
    WISDOM = "wisdom"
    COURAGE = "courage"
    JUSTICE = "justice"
    TEMPERANCE = "temperance"
    GENERAL = "general"


class PostStatus(str, Enum):
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    POSTED = "posted"
    SKIPPED = "skipped"


class QueueStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    POSTED = "posted"
    FAILED = "failed"


# Request models
class GenerateRequest(BaseModel):
    topic: Optional[str] = Field(None, description="Topic for content generation")
    include_examples: bool = Field(True, description="Include style examples in generation")
    format_type: Optional[str] = Field(
        None,
        description="Format type: 'short', 'thread', 'long'. If not provided, randomly selects based on 70/20/10 weights."
    )
    virtue: Optional[str] = Field(
        None,
        description="Stoic virtue: 'wisdom', 'courage', 'justice', 'temperance', 'general'. If not provided, randomly selects."
    )


class GenerateReplyRequest(BaseModel):
    tweet_text: str = Field(..., description="Original tweet text to reply to")
    tweet_id: Optional[str] = Field(None, description="Original tweet ID")
    username: Optional[str] = Field(None, description="Original tweet author username")
    include_examples: bool = Field(True, description="Include style examples")
    virtue: Optional[str] = Field(None, description="Stoic virtue for reply")


class CreatePostRequest(BaseModel):
    content: str = Field(..., description="Post content")
    topic: Optional[str] = None
    post_type: PostType = PostType.ORIGINAL
    format_type: Optional[str] = Field(None, description="Format type: short, thread, or long")
    virtue: Optional[str] = Field(None, description="Stoic virtue")
    reply_to_tweet_id: Optional[str] = None
    reply_to_content: Optional[str] = None
    reply_to_username: Optional[str] = None
    is_evergreen: bool = True


class UpdatePostRequest(BaseModel):
    content: Optional[str] = None
    status: Optional[PostStatus] = None
    virtue: Optional[str] = None
    is_evergreen: Optional[bool] = None


class QueuePostRequest(BaseModel):
    post_id: str = Field(..., description="Post ID to queue")
    scheduled_for: datetime = Field(..., description="When to post")


class RefineRequest(BaseModel):
    content: str = Field(..., description="Content to refine")
    instruction: str = Field(..., description="How to refine the content")


class SchedulerConfigRequest(BaseModel):
    enabled: Optional[bool] = None
    intervals: Optional[List[int]] = None
    blackout_start: Optional[str] = None
    blackout_end: Optional[str] = None
    timezone: Optional[str] = None


# Response models
class PostResponse(BaseModel):
    id: str
    content: str
    topic: Optional[str]
    post_type: PostType
    format_type: Optional[str] = None
    virtue: Optional[str] = None
    tweets: Optional[List[str]] = None
    tweet_count: int = 1
    reply_to_tweet_id: Optional[str]
    reply_to_content: Optional[str]
    reply_to_username: Optional[str]
    model: Optional[str]
    citations: Optional[dict]
    status: PostStatus
    is_evergreen: bool
    recycle_count: int
    created_at: datetime
    approved_at: Optional[datetime]
    posted_at: Optional[datetime]
    x_post_id: Optional[str]


class QueueResponse(BaseModel):
    id: str
    post_id: str
    scheduled_for: datetime
    status: QueueStatus
    posted_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime
    post: Optional[PostResponse] = None


class GenerateResponse(BaseModel):
    content: str
    tweets: List[str]
    format_type: str
    virtue: Optional[str] = None
    tweet_count: int = 1
    topic: Optional[str]
    model: str
    citations: Optional[List[dict]]
    post_id: Optional[str] = None


class RefineResponse(BaseModel):
    content: str
    original: str
    instruction: str
    model: str


class TrendingPostResponse(BaseModel):
    tweet_id: str
    content: str
    username: str
    likes: Optional[int]
    retweets: Optional[int]
    relevance_score: Optional[float]
    cache_status: Optional[str] = None


class SchedulerStatusResponse(BaseModel):
    is_running: bool
    is_paused: bool
    next_post_at: Optional[str]
    in_blackout: bool
    rate_limit: dict
    active_hours: int
    estimated_posts_per_day: float


class AuthStatusResponse(BaseModel):
    authenticated: bool
    username: Optional[str] = None
    profile_image: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
