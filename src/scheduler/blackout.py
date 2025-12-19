"""Blackout window management for scheduling."""

from datetime import datetime, time
from typing import Optional
import pytz


class BlackoutManager:
    """Manage blackout windows when posting is disabled."""

    def __init__(
        self,
        start_time: str = "23:00",
        end_time: str = "05:00",
        timezone: str = "America/New_York"
    ):
        """
        Args:
            start_time: Blackout start time (HH:MM format)
            end_time: Blackout end time (HH:MM format)
            timezone: Timezone for blackout window
        """
        self.start = self._parse_time(start_time)
        self.end = self._parse_time(end_time)
        self.timezone = pytz.timezone(timezone)

    def _parse_time(self, time_str: str) -> time:
        """Parse HH:MM string to time object."""
        parts = time_str.split(":")
        return time(int(parts[0]), int(parts[1]))

    def is_blackout(self, dt: Optional[datetime] = None) -> bool:
        """
        Check if a given time is within the blackout window.

        Args:
            dt: Datetime to check (default: now)

        Returns:
            True if in blackout window
        """
        if dt is None:
            dt = datetime.now(self.timezone)
        elif dt.tzinfo is None:
            dt = self.timezone.localize(dt)
        else:
            dt = dt.astimezone(self.timezone)

        current_time = dt.time()

        if self.start > self.end:
            return current_time >= self.start or current_time < self.end
        else:
            return self.start <= current_time < self.end

    def get_next_active_time(self, dt: Optional[datetime] = None) -> datetime:
        """
        Get the next time when posting is allowed.

        Args:
            dt: Starting datetime (default: now)

        Returns:
            Next datetime when posting is allowed
        """
        if dt is None:
            dt = datetime.now(self.timezone)
        elif dt.tzinfo is None:
            dt = self.timezone.localize(dt)
        else:
            dt = dt.astimezone(self.timezone)

        if not self.is_blackout(dt):
            return dt

        next_day = dt.date()
        if dt.time() >= self.start:
            from datetime import timedelta
            next_day = dt.date() + timedelta(days=1)

        return self.timezone.localize(
            datetime.combine(next_day, self.end)
        )

    def get_blackout_duration(self) -> int:
        """Get blackout duration in hours."""
        start_minutes = self.start.hour * 60 + self.start.minute
        end_minutes = self.end.hour * 60 + self.end.minute

        if self.start > self.end:
            duration = (24 * 60 - start_minutes) + end_minutes
        else:
            duration = end_minutes - start_minutes

        return duration // 60

    def get_active_hours(self) -> int:
        """Get active posting hours per day."""
        return 24 - self.get_blackout_duration()
