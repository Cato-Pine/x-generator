"""X API v2 client for posting tweets."""

from typing import Optional, Dict, List
import httpx
from src.twitter.oauth import OAuthManager


class XClient:
    """
    Client for posting to X (Twitter) via API v2.
    Uses OAuth2 for user authentication.
    Free tier limit: 17 tweets per 24 hours.
    """

    BASE_URL = "https://api.twitter.com/2"

    def __init__(self, oauth_manager: OAuthManager = None):
        self.oauth = oauth_manager or OAuthManager()

    async def _get_headers(self) -> Dict[str, str]:
        """Get request headers with valid OAuth token."""
        token = await self.oauth.get_valid_token()
        if not token:
            raise ValueError("Not authenticated. Please complete OAuth flow first.")

        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def post_tweet(
        self,
        text: str,
        reply_to: str = None,
        quote_tweet_id: str = None,
    ) -> Optional[Dict]:
        """
        Post a tweet to X.

        Args:
            text: The tweet text (max 280 chars for regular, 4000 for premium)
            reply_to: Tweet ID to reply to (optional)
            quote_tweet_id: Tweet ID to quote (optional)

        Returns:
            Dict with tweet data or None on failure
        """
        headers = await self._get_headers()

        payload = {"text": text}

        if reply_to:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to}

        if quote_tweet_id:
            payload["quote_tweet_id"] = quote_tweet_id

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.BASE_URL}/tweets",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

                return {
                    "tweet_id": data.get("data", {}).get("id"),
                    "text": data.get("data", {}).get("text"),
                }

            except httpx.HTTPStatusError as e:
                error_data = e.response.json() if e.response.content else {}
                print(f"HTTP error posting tweet: {e}")
                print(f"Error details: {error_data}")
                return None

            except Exception as e:
                print(f"Error posting tweet: {e}")
                return None

    async def post_thread(self, tweets: List[str]) -> List[Dict]:
        """
        Post a thread of tweets.

        Args:
            tweets: List of tweet texts to post as a thread

        Returns:
            List of posted tweet data
        """
        results = []
        reply_to = None

        for tweet_text in tweets:
            result = await self.post_tweet(tweet_text, reply_to=reply_to)
            if result:
                results.append(result)
                reply_to = result.get("tweet_id")
            else:
                print(f"Failed to post tweet in thread. Stopping.")
                break

        return results

    async def delete_tweet(self, tweet_id: str) -> bool:
        """Delete a tweet by ID."""
        headers = await self._get_headers()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(
                    f"{self.BASE_URL}/tweets/{tweet_id}",
                    headers=headers,
                )
                response.raise_for_status()
                return True

            except Exception as e:
                print(f"Error deleting tweet: {e}")
                return False

    async def get_me(self) -> Optional[Dict]:
        """Get the authenticated user's info."""
        headers = await self._get_headers()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/users/me",
                    headers=headers,
                    params={"user.fields": "username,name,profile_image_url"},
                )
                response.raise_for_status()
                data = response.json()

                return data.get("data")

            except Exception as e:
                print(f"Error getting user info: {e}")
                return None

    async def is_rate_limited(self) -> bool:
        """
        Check if we're rate limited.
        Note: X API v2 doesn't expose rate limit headers easily,
        so we track this ourselves via the database.
        """
        from src.db.posts import PostsDB

        posts_db = PostsDB()
        status = posts_db.get_rate_limit_status()
        return not status.get("can_post", True)
