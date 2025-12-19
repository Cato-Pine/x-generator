"""Random interval selection for scheduling."""

import random
from typing import List
from datetime import timedelta


class IntervalRandomizer:
    """Generate random posting intervals with jitter."""

    def __init__(self, intervals: List[int] = None):
        """
        Args:
            intervals: List of base intervals in minutes (e.g., [45, 60, 90, 120])
        """
        self.intervals = intervals or [45, 60, 90, 120]

    def get_next_interval(self) -> timedelta:
        """
        Get a random interval for the next post.

        Returns:
            timedelta for the next posting interval
        """
        base_minutes = random.choice(self.intervals)
        jitter = self._add_jitter(base_minutes)
        return timedelta(minutes=jitter)

    def _add_jitter(self, base_minutes: int, jitter_percent: float = 0.15) -> int:
        """
        Add random jitter to avoid predictable patterns.

        Args:
            base_minutes: Base interval in minutes
            jitter_percent: Percentage of jitter (default 15%)

        Returns:
            Adjusted minutes with jitter
        """
        jitter_range = int(base_minutes * jitter_percent)
        jitter = random.randint(-jitter_range, jitter_range)
        return max(5, base_minutes + jitter)

    def get_average_interval(self) -> float:
        """Get the average interval in minutes."""
        return sum(self.intervals) / len(self.intervals)

    def get_posts_per_day_estimate(self, active_hours: int = 16) -> float:
        """
        Estimate posts per day based on intervals.

        Args:
            active_hours: Hours of active posting (excluding blackout)

        Returns:
            Estimated posts per day
        """
        avg_interval = self.get_average_interval()
        return (active_hours * 60) / avg_interval
