"""X OAuth2 authentication routes."""

import secrets
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from src.api.models import AuthStatusResponse
from src.twitter.oauth import OAuthManager
from src.twitter.x_client import XClient

router = APIRouter(prefix="/auth", tags=["auth"])

oauth_states = {}


@router.get("/x/login")
async def initiate_x_login(request: Request):
    """
    Initiate X OAuth2 login flow.
    Returns the authorization URL to redirect the user to.
    """
    oauth = OAuthManager()

    state = secrets.token_urlsafe(16)
    pkce = oauth.generate_pkce()

    oauth_states[state] = pkce["code_verifier"]

    auth_url = oauth.get_authorization_url(state, pkce["code_challenge"])

    return {"authorization_url": auth_url, "state": state}


@router.get("/x/callback")
async def x_oauth_callback(code: str, state: str):
    """
    Handle X OAuth2 callback.
    Exchanges the authorization code for tokens.
    """
    if state not in oauth_states:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    code_verifier = oauth_states.pop(state)

    oauth = OAuthManager()
    tokens = await oauth.exchange_code(code, code_verifier)

    if not tokens:
        raise HTTPException(status_code=500, detail="Failed to exchange code for tokens")

    return {"message": "Authentication successful", "authenticated": True}


@router.get("/x/status", response_model=AuthStatusResponse)
async def get_auth_status():
    """Check X authentication status."""
    oauth = OAuthManager()
    is_auth = await oauth.is_authenticated()

    if not is_auth:
        return AuthStatusResponse(authenticated=False)

    x_client = XClient(oauth)
    user = await x_client.get_me()

    return AuthStatusResponse(
        authenticated=True,
        username=user.get("username") if user else None,
        profile_image=user.get("profile_image_url") if user else None,
    )


@router.post("/x/logout")
async def logout():
    """Revoke X tokens and log out."""
    oauth = OAuthManager()
    await oauth.revoke_tokens()
    return {"message": "Logged out successfully"}


@router.post("/x/refresh")
async def refresh_tokens():
    """Manually refresh the access token."""
    oauth = OAuthManager()
    tokens = await oauth.refresh_tokens()

    if not tokens:
        raise HTTPException(status_code=500, detail="Failed to refresh tokens")

    return {"message": "Tokens refreshed successfully"}
