"""Settings management routes."""

from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.db.settings import SettingsDB

router = APIRouter(prefix="/settings", tags=["settings"])


class SettingResponse(BaseModel):
    key: str
    value: dict


class UpdateSettingRequest(BaseModel):
    value: dict


@router.get("", response_model=List[SettingResponse])
async def list_settings():
    """List all settings."""
    settings_db = SettingsDB()
    settings = settings_db.get_all()
    return [SettingResponse(key=s["key"], value=s.get("value", {})) for s in settings]


@router.get("/{key}", response_model=SettingResponse)
async def get_setting(key: str):
    """Get a specific setting."""
    settings_db = SettingsDB()
    setting = settings_db.get(key)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return SettingResponse(key=setting["key"], value=setting.get("value", {}))


@router.put("/{key}", response_model=SettingResponse)
async def update_setting(key: str, request: UpdateSettingRequest):
    """Update a setting."""
    settings_db = SettingsDB()
    setting = settings_db.set(key, request.value)
    if not setting:
        raise HTTPException(status_code=500, detail="Failed to update setting")
    return SettingResponse(key=setting["key"], value=setting.get("value", {}))


@router.delete("/{key}")
async def delete_setting(key: str):
    """Delete a setting."""
    settings_db = SettingsDB()
    if not settings_db.delete(key):
        raise HTTPException(status_code=404, detail="Setting not found")
    return {"message": "Setting deleted"}


# Convenience endpoints for common settings

@router.get("/scheduler/config")
async def get_scheduler_config():
    """Get scheduler configuration."""
    settings_db = SettingsDB()
    return settings_db.get_scheduler_config()


@router.get("/rate-limits/config")
async def get_rate_limits_config():
    """Get rate limit configuration."""
    settings_db = SettingsDB()
    return settings_db.get_rate_limits()


@router.get("/generation/config")
async def get_generation_config():
    """Get generation configuration."""
    settings_db = SettingsDB()
    return settings_db.get_generation_config()


@router.get("/trending/config")
async def get_trending_config():
    """Get trending topics configuration."""
    settings_db = SettingsDB()
    return settings_db.get_trending_config()
