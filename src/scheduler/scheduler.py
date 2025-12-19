"""Main scheduler for automated posting."""

import asyncio
from datetime import datetime
from typing import Optional, Callable
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from src.scheduler.randomizer import IntervalRandomizer
from src.scheduler.blackout import BlackoutManager
from src.db.settings import SettingsDB
from src.db.queue import QueueDB
from src.db.posts import PostsDB
from src.twitter.x_client import XClient


class PostingScheduler:
    """Manage automated posting to X with random intervals and blackout windows."""

    def __init__(
        self,
        x_client: XClient = None,
        on_post_success: Optional[Callable] = None,
        on_post_failure: Optional[Callable] = None,
    ):
        """
        Args:
            x_client: X API client for posting
            on_post_success: Callback for successful posts
            on_post_failure: Callback for failed posts
        """
        self.scheduler = AsyncIOScheduler()
        self.x_client = x_client or XClient()
        self.on_post_success = on_post_success
        self.on_post_failure = on_post_failure

        self.settings_db = SettingsDB()
        self.queue_db = QueueDB()
        self.posts_db = PostsDB()

        self._is_running = False
        self._is_paused = False

    def _load_config(self):
        """Load scheduler configuration from database."""
        config = self.settings_db.get_scheduler_config()

        self.randomizer = IntervalRandomizer(config.get("intervals", [45, 60, 90, 120]))
        self.blackout = BlackoutManager(
            start_time=config.get("blackout_start", "23:00"),
            end_time=config.get("blackout_end", "05:00"),
            timezone=config.get("timezone", "America/New_York"),
        )
        self._is_paused = config.get("paused", False)

    async def start(self):
        """Start the scheduler."""
        if self._is_running:
            return

        self._load_config()
        self.scheduler.start()
        self._is_running = True

        await self._schedule_next_post()

    def stop(self):
        """Stop the scheduler."""
        if not self._is_running:
            return

        self.scheduler.shutdown()
        self._is_running = False

    async def pause(self):
        """Pause posting (keeps scheduler running but skips posts)."""
        self._is_paused = True
        self.settings_db.set_scheduler_paused(True)

    async def resume(self):
        """Resume posting."""
        self._is_paused = False
        self.settings_db.set_scheduler_paused(False)
        await self._schedule_next_post()

    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._is_running

    def is_paused(self) -> bool:
        """Check if scheduler is paused."""
        return self._is_paused

    async def _schedule_next_post(self):
        """Schedule the next post with random interval."""
        if not self._is_running or self._is_paused:
            return

        now = datetime.now(self.blackout.timezone)

        if self.blackout.is_blackout(now):
            next_time = self.blackout.get_next_active_time(now)
        else:
            interval = self.randomizer.get_next_interval()
            next_time = now + interval

            if self.blackout.is_blackout(next_time):
                next_time = self.blackout.get_next_active_time(next_time)

        self.scheduler.add_job(
            self._post_next,
            trigger=DateTrigger(run_date=next_time),
            id="next_post",
            replace_existing=True,
        )

    async def _post_next(self):
        """Post the next approved item from queue."""
        if self._is_paused:
            await self._schedule_next_post()
            return

        rate_status = self.posts_db.get_rate_limit_status()
        if not rate_status.get("can_post", True):
            print("Rate limit reached. Skipping post.")
            await self._schedule_next_post()
            return

        pending = self.queue_db.get_pending_to_post()
        if not pending:
            await self._schedule_next_post()
            return

        queue_entry = pending[0]
        post = queue_entry.get("posts", {})

        try:
            content = post.get("content", "")
            format_type = post.get("format_type", "short")

            if format_type == "thread":
                tweets = content.split("\n\n")
                result = await self.x_client.post_thread(tweets)
                tweet_id = result[0].get("tweet_id") if result else None
            else:
                result = await self.x_client.post_tweet(content)
                tweet_id = result.get("tweet_id") if result else None

            if tweet_id:
                self.queue_db.mark_posted(queue_entry["id"])
                self.posts_db.mark_posted(post["id"], tweet_id)

                if self.on_post_success:
                    self.on_post_success(post, tweet_id)
            else:
                self.queue_db.mark_failed(queue_entry["id"], "No tweet ID returned")
                if self.on_post_failure:
                    self.on_post_failure(post, "No tweet ID returned")

        except Exception as e:
            error_msg = str(e)
            self.queue_db.mark_failed(queue_entry["id"], error_msg)

            if self.on_post_failure:
                self.on_post_failure(post, error_msg)

        await self._schedule_next_post()

    def get_status(self) -> dict:
        """Get current scheduler status."""
        next_job = self.scheduler.get_job("next_post")
        next_run = next_job.next_run_time if next_job else None

        rate_status = self.posts_db.get_rate_limit_status()

        return {
            "is_running": self._is_running,
            "is_paused": self._is_paused,
            "next_post_at": next_run.isoformat() if next_run else None,
            "in_blackout": self.blackout.is_blackout() if hasattr(self, "blackout") else False,
            "rate_limit": rate_status,
            "active_hours": self.blackout.get_active_hours() if hasattr(self, "blackout") else 24,
            "estimated_posts_per_day": (
                self.randomizer.get_posts_per_day_estimate(
                    self.blackout.get_active_hours()
                )
                if hasattr(self, "randomizer") else 0
            ),
        }

    async def post_now(self, post_id: str) -> dict:
        """Immediately post a specific approved post."""
        post = self.posts_db.get_by_id(post_id)
        if not post:
            return {"error": "Post not found"}

        if post.get("status") != "approved":
            return {"error": "Post is not approved"}

        rate_status = self.posts_db.get_rate_limit_status()
        if not rate_status.get("can_post", True):
            return {"error": "Rate limit reached"}

        try:
            content = post.get("content", "")
            format_type = post.get("format_type", "short")

            if format_type == "thread":
                tweets = content.split("\n\n")
                result = await self.x_client.post_thread(tweets)
                tweet_id = result[0].get("tweet_id") if result else None
            else:
                result = await self.x_client.post_tweet(content)
                tweet_id = result.get("tweet_id") if result else None

            if tweet_id:
                self.posts_db.mark_posted(post_id, tweet_id)
                return {"success": True, "tweet_id": tweet_id}
            else:
                return {"error": "Failed to post"}

        except Exception as e:
            return {"error": str(e)}
