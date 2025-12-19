"""OAuth2 token management for X API."""

import os
import secrets
import hashlib
import base64
from typing import Optional, Dict
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from src.db.supabase_client import get_supabase


class OAuthManager:
    """Manage OAuth2 tokens for X API."""

    def __init__(self):
        self.client_id = os.getenv("X_CLIENT_ID")
        self.client_secret = os.getenv("X_CLIENT_SECRET")
        self.redirect_uri = os.getenv("X_REDIRECT_URI", "http://localhost:8000/auth/x/callback")
        self.db = get_supabase()

    def generate_pkce(self) -> Dict[str, str]:
        """Generate PKCE code verifier and challenge."""
        code_verifier = secrets.token_urlsafe(32)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip("=")

        return {
            "code_verifier": code_verifier,
            "code_challenge": code_challenge,
        }

    def get_authorization_url(self, state: str, code_challenge: str) -> str:
        """Generate the X OAuth2 authorization URL."""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "tweet.read tweet.write users.read offline.access",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }

        return f"https://twitter.com/i/oauth2/authorize?{urlencode(params)}"

    async def exchange_code(self, code: str, code_verifier: str) -> Optional[Dict]:
        """Exchange authorization code for tokens."""
        import httpx

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.twitter.com/2/oauth2/token",
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": self.redirect_uri,
                        "code_verifier": code_verifier,
                        "client_id": self.client_id,
                    },
                    auth=(self.client_id, self.client_secret) if self.client_secret else None,
                )
                response.raise_for_status()
                tokens = response.json()

                await self._save_tokens(tokens)
                return tokens

            except Exception as e:
                print(f"Error exchanging code: {e}")
                return None

    async def refresh_tokens(self) -> Optional[Dict]:
        """Refresh the access token using refresh token."""
        import httpx

        current = await self.get_tokens()
        if not current or not current.get("refresh_token"):
            return None

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.twitter.com/2/oauth2/token",
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": current["refresh_token"],
                        "client_id": self.client_id,
                    },
                    auth=(self.client_id, self.client_secret) if self.client_secret else None,
                )
                response.raise_for_status()
                tokens = response.json()

                await self._save_tokens(tokens)
                return tokens

            except Exception as e:
                print(f"Error refreshing tokens: {e}")
                return None

    async def _save_tokens(self, tokens: Dict) -> None:
        """Save tokens to database."""
        expires_in = tokens.get("expires_in", 7200)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        data = {
            "provider": "x",
            "access_token": tokens.get("access_token"),
            "refresh_token": tokens.get("refresh_token"),
            "expires_at": expires_at.isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        self.db.table("oauth_tokens").upsert(
            data,
            on_conflict="provider"
        ).execute()

    async def get_tokens(self) -> Optional[Dict]:
        """Get current tokens from database."""
        result = self.db.table("oauth_tokens").select("*").eq(
            "provider", "x"
        ).execute()

        if not result.data:
            return None

        token = result.data[0]
        return {
            "access_token": token.get("access_token"),
            "refresh_token": token.get("refresh_token"),
            "expires_at": token.get("expires_at"),
        }

    async def get_valid_token(self) -> Optional[str]:
        """Get a valid access token, refreshing if needed."""
        tokens = await self.get_tokens()
        if not tokens:
            return None

        expires_at = tokens.get("expires_at")
        if expires_at:
            expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            if expiry <= datetime.now(timezone.utc) + timedelta(minutes=5):
                refreshed = await self.refresh_tokens()
                if refreshed:
                    return refreshed.get("access_token")
                return None

        return tokens.get("access_token")

    async def revoke_tokens(self) -> bool:
        """Revoke current tokens."""
        import httpx

        tokens = await self.get_tokens()
        if not tokens:
            return True

        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    "https://api.twitter.com/2/oauth2/revoke",
                    data={
                        "token": tokens.get("access_token"),
                        "token_type_hint": "access_token",
                        "client_id": self.client_id,
                    },
                    auth=(self.client_id, self.client_secret) if self.client_secret else None,
                )
            except Exception as e:
                print(f"Error revoking token: {e}")

        self.db.table("oauth_tokens").delete().eq("provider", "x").execute()
        return True

    async def is_authenticated(self) -> bool:
        """Check if we have valid tokens."""
        token = await self.get_valid_token()
        return token is not None
