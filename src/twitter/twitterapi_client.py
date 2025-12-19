"""TwitterAPI.io client for trending discovery."""

import os
from typing import List, Optional
import httpx
from pydantic import BaseModel


class TrendingPost(BaseModel):
    """A trending post from Twitter/X."""
    tweet_id: str
    content: str
    username: str
    likes: int = 0
    retweets: int = 0
    relevance_score: Optional[float] = None


class TwitterAPIClient:
    """
    Client for TwitterAPI.io - a paid third-party Twitter API.
    Used for discovering trending posts to reply to.
    Pricing: ~$0.15 per 1,000 tweets
    """

    BASE_URL = "https://api.twitterapi.io/twitter"

    def __init__(self):
        self.api_key = os.getenv("TWITTERAPI_IO_KEY")

    def _get_headers(self) -> dict:
        """Get request headers with API key."""
        if not self.api_key:
            raise ValueError("TWITTERAPI_IO_KEY environment variable is not set")

        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    async def search_trending(
        self,
        topics: List[str],
        limit: int = 10
    ) -> List[TrendingPost]:
        """
        Search for trending posts matching the given topics.

        Args:
            topics: List of topics/keywords to search
            limit: Maximum number of posts to return

        Returns:
            List of trending posts
        """
        results = []

        async with httpx.AsyncClient() as client:
            for topic in topics:
                if len(results) >= limit:
                    break

                try:
                    response = await client.get(
                        f"{self.BASE_URL}/tweet/search",
                        headers=self._get_headers(),
                        params={
                            "query": topic,
                            "type": "Top",
                            "count": min(limit - len(results), 20)
                        }
                    )
                    response.raise_for_status()
                    data = response.json()

                    tweets = data.get("tweets", [])
                    for tweet in tweets:
                        results.append(TrendingPost(
                            tweet_id=tweet.get("id", ""),
                            content=tweet.get("text", ""),
                            username=tweet.get("user", {}).get("screen_name", "unknown"),
                            likes=tweet.get("favorite_count", 0),
                            retweets=tweet.get("retweet_count", 0),
                            relevance_score=self._calculate_relevance(
                                tweet.get("favorite_count", 0),
                                tweet.get("retweet_count", 0)
                            )
                        ))

                        if len(results) >= limit:
                            break

                except httpx.HTTPStatusError as e:
                    print(f"HTTP error searching for topic '{topic}': {e}")
                    continue
                except Exception as e:
                    print(f"Error searching for topic '{topic}': {e}")
                    continue

        results.sort(key=lambda x: x.relevance_score or 0, reverse=True)
        return results[:limit]

    async def get_tweet(self, tweet_id: str) -> Optional[TrendingPost]:
        """Get a specific tweet by ID."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/tweet/{tweet_id}",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                tweet = response.json()

                return TrendingPost(
                    tweet_id=tweet.get("id", ""),
                    content=tweet.get("text", ""),
                    username=tweet.get("user", {}).get("screen_name", "unknown"),
                    likes=tweet.get("favorite_count", 0),
                    retweets=tweet.get("retweet_count", 0),
                    relevance_score=self._calculate_relevance(
                        tweet.get("favorite_count", 0),
                        tweet.get("retweet_count", 0)
                    )
                )

            except Exception as e:
                print(f"Error fetching tweet {tweet_id}: {e}")
                return None

    @staticmethod
    def _calculate_relevance(likes: int, retweets: int) -> float:
        """Calculate a simple relevance score based on engagement."""
        if not likes and not retweets:
            return 0.0
        return likes + retweets * 2
