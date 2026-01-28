"""
ONI v2.0 - Health Check Endpoints
"""
from datetime import datetime
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""
    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    timestamp: str
    components: dict[str, str]


class ReadinessResponse(BaseModel):
    """Readiness check response."""
    ready: bool
    checks: dict[str, bool]


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns current health status of the ONI system.
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.now().isoformat(),
        components={
            "api": "up",
            "llm": "pending",
            "vision": "pending",
            "memory": "pending",
        }
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check() -> ReadinessResponse:
    """
    Readiness check endpoint.
    
    Returns whether the system is ready to accept requests.
    """
    # TODO: Add actual readiness checks
    checks = {
        "config_loaded": True,
        "llm_ready": False,
        "vision_ready": False,
        "memory_ready": False,
    }
    
    return ReadinessResponse(
        ready=all(checks.values()),
        checks=checks
    )


@router.get("/info")
async def system_info() -> dict[str, str]:
    """
    System information endpoint.
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "mode": settings.agent.mode.value,
        "debug": str(settings.debug),
    }
