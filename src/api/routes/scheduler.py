"""Scheduler management routes."""

from fastapi import APIRouter, HTTPException, Request
from src.api.models import SchedulerStatusResponse, SchedulerConfigRequest
from src.scheduler import PostingScheduler
from src.db.settings import SettingsDB
from src.db.posts import PostsDB

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


def get_scheduler(request: Request) -> PostingScheduler:
    """Get the scheduler instance from app state."""
    if not hasattr(request.app.state, "scheduler"):
        raise HTTPException(status_code=503, detail="Scheduler not initialized")
    return request.app.state.scheduler


@router.get("/status", response_model=SchedulerStatusResponse)
async def get_scheduler_status(request: Request):
    """Get current scheduler status."""
    try:
        scheduler = get_scheduler(request)
        status = scheduler.get_status()

        return SchedulerStatusResponse(
            is_running=status.get("is_running", False),
            is_paused=status.get("is_paused", False),
            next_post_at=status.get("next_post_at"),
            in_blackout=status.get("in_blackout", False),
            rate_limit=status.get("rate_limit", {}),
            active_hours=status.get("active_hours", 24),
            estimated_posts_per_day=status.get("estimated_posts_per_day", 0),
        )
    except HTTPException:
        return SchedulerStatusResponse(
            is_running=False,
            is_paused=False,
            next_post_at=None,
            in_blackout=False,
            rate_limit={},
            active_hours=24,
            estimated_posts_per_day=0,
        )


@router.post("/start")
async def start_scheduler(request: Request):
    """Start the scheduler."""
    if not hasattr(request.app.state, "scheduler"):
        request.app.state.scheduler = PostingScheduler()

    scheduler = request.app.state.scheduler

    if scheduler.is_running():
        return {"message": "Scheduler already running"}

    await scheduler.start()
    return {"message": "Scheduler started"}


@router.post("/stop")
async def stop_scheduler(request: Request):
    """Stop the scheduler."""
    scheduler = get_scheduler(request)

    if not scheduler.is_running():
        return {"message": "Scheduler not running"}

    scheduler.stop()
    return {"message": "Scheduler stopped"}


@router.post("/pause")
async def pause_scheduler(request: Request):
    """Pause the scheduler (keeps running but skips posts)."""
    scheduler = get_scheduler(request)
    await scheduler.pause()
    return {"message": "Scheduler paused"}


@router.post("/resume")
async def resume_scheduler(request: Request):
    """Resume the scheduler."""
    scheduler = get_scheduler(request)
    await scheduler.resume()
    return {"message": "Scheduler resumed"}


@router.post("/post-now/{post_id}")
async def post_now(request: Request, post_id: str):
    """Immediately post a specific approved post."""
    scheduler = get_scheduler(request)
    result = await scheduler.post_now(post_id)

    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.get("/config")
async def get_scheduler_config():
    """Get scheduler configuration."""
    settings_db = SettingsDB()
    return settings_db.get_scheduler_config()


@router.put("/config")
async def update_scheduler_config(request: Request, config: SchedulerConfigRequest):
    """Update scheduler configuration."""
    settings_db = SettingsDB()
    current = settings_db.get_scheduler_config()

    if config.enabled is not None:
        current["enabled"] = config.enabled
    if config.intervals is not None:
        current["intervals"] = config.intervals
    if config.blackout_start is not None:
        current["blackout_start"] = config.blackout_start
    if config.blackout_end is not None:
        current["blackout_end"] = config.blackout_end
    if config.timezone is not None:
        current["timezone"] = config.timezone

    settings_db.set_scheduler_config(current)

    if hasattr(request.app.state, "scheduler"):
        scheduler = request.app.state.scheduler
        scheduler._load_config()

    return current


@router.get("/estimate")
async def get_posting_estimate():
    """Get estimated posts per day based on current configuration."""
    settings_db = SettingsDB()
    config = settings_db.get_scheduler_config()

    from src.scheduler import IntervalRandomizer, BlackoutManager

    randomizer = IntervalRandomizer(config.get("intervals", [45, 60, 90, 120]))
    blackout = BlackoutManager(
        start_time=config.get("blackout_start", "23:00"),
        end_time=config.get("blackout_end", "05:00"),
        timezone=config.get("timezone", "America/New_York"),
    )

    active_hours = blackout.get_active_hours()
    estimated = randomizer.get_posts_per_day_estimate(active_hours)

    posts_db = PostsDB()
    rate_status = posts_db.get_rate_limit_status()

    return {
        "active_hours": active_hours,
        "average_interval_minutes": randomizer.get_average_interval(),
        "estimated_posts_per_day": round(estimated, 1),
        "rate_limit_daily": rate_status.get("daily_limit", 17),
        "within_rate_limit": estimated <= rate_status.get("daily_limit", 17),
    }
