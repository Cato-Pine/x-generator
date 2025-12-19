"""Settings database operations."""

from typing import Optional, List, Any
from datetime import datetime
from supabase import Client
from src.db.supabase_client import get_supabase


class SettingsDB:
    """Database operations for settings."""

    def __init__(self, client: Optional[Client] = None):
        self.client = client or get_supabase()

    def get(self, key: str) -> Optional[dict]:
        """Get a setting by key."""
        result = self.client.table("settings").select("*").eq("key", key).execute()
        return result.data[0] if result.data else None

    def get_value(self, key: str, default: Any = None) -> Any:
        """Get just the value of a setting."""
        setting = self.get(key)
        return setting.get("value") if setting else default

    def get_all(self) -> List[dict]:
        """Get all settings."""
        result = self.client.table("settings").select("*").execute()
        return result.data or []

    def set(self, key: str, value: dict) -> dict:
        """Set a setting (upsert)."""
        data = {
            "key": key,
            "value": value,
            "updated_at": datetime.utcnow().isoformat()
        }
        result = self.client.table("settings").upsert(
            data,
            on_conflict="key"
        ).execute()
        return result.data[0] if result.data else None

    def delete(self, key: str) -> bool:
        """Delete a setting."""
        result = self.client.table("settings").delete().eq("key", key).execute()
        return bool(result.data)

    # Scheduler settings

    def get_scheduler_config(self) -> dict:
        """Get scheduler configuration."""
        return self.get_value("scheduler", {
            "enabled": True,
            "intervals": [45, 60, 90, 120],
            "blackout_start": "23:00",
            "blackout_end": "05:00",
            "timezone": "America/New_York",
            "paused": False
        })

    def set_scheduler_config(self, config: dict) -> dict:
        """Update scheduler configuration."""
        return self.set("scheduler", config)

    def get_scheduler_paused(self) -> bool:
        """Check if scheduler is paused."""
        config = self.get_scheduler_config()
        return config.get("paused", False)

    def set_scheduler_paused(self, paused: bool) -> dict:
        """Set scheduler paused state."""
        config = self.get_scheduler_config()
        config["paused"] = paused
        return self.set_scheduler_config(config)

    # Rate limit settings

    def get_rate_limits(self) -> dict:
        """Get the X API rate limit settings (Free tier defaults)."""
        return self.get_value("rate_limits", {
            "max_daily_tweets": 17,
            "max_tweets_per_hour": 17,
            "enabled": True
        })

    def set_rate_limits(self, limits: dict) -> dict:
        """Update rate limit settings."""
        return self.set("rate_limits", limits)

    # Content generation settings

    def get_generation_config(self) -> dict:
        """Get content generation configuration."""
        return self.get_value("generation", {
            "default_virtue": None,
            "format_weights": {"short": 70, "thread": 20, "long": 10},
            "include_examples": True,
            "model": "gpt-4-turbo"
        })

    def set_generation_config(self, config: dict) -> dict:
        """Update generation configuration."""
        return self.set("generation", config)

    # Trending topics settings

    def get_trending_config(self) -> dict:
        """Get trending topics configuration."""
        return self.get_value("trending", {
            "topics": ["stoicism", "philosophy", "self-improvement", "wisdom"],
            "max_results": 10,
            "min_engagement": 100
        })

    def set_trending_config(self, config: dict) -> dict:
        """Update trending configuration."""
        return self.set("trending", config)
