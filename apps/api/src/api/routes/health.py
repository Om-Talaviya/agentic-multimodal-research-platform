"""Health check routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_session
from database.repositories import ResearchJobRepository
from ai.providers.router import ModelRouter
from shared.config import settings
from shared.logging import get_logger

router = APIRouter(tags=["health"])
logger = get_logger(__name__)


@router.get("/health")
async def health_check(
    session: AsyncSession = Depends(get_session),
):
    """Health check endpoint."""
    checks = {}
    
    # Database
    try:
        repo = ResearchJobRepository(session)
        await repo.count_jobs()
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {e}"
    
    # Model providers
    try:
        from api.dependencies import get_model_router
        router: ModelRouter = get_model_router()
        health_results = await router.health_check_all()
        for name, health in health_results.items():
            checks[name] = "healthy" if health.healthy else f"unhealthy: {health.error}"
    except Exception as e:
        checks["model_providers"] = f"error: {e}"
    
    overall = "healthy" if all(v == "healthy" for v in checks.values()) else "degraded"
    
    return {
        "status": overall,
        "version": settings.app_version,
        "checks": checks,
    }


@router.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe."""
    return {"status": "ready"}


@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe."""
    return {"status": "alive"}