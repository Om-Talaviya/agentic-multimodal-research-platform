"""Model provider routes."""

from fastapi import APIRouter, Depends
from ai.providers.router import ModelRouter
from ai.schemas import ProviderHealth, ModelInfo
from typing import List

router = APIRouter(prefix="/models", tags=["models"])


async def get_model_router() -> ModelRouter:
    from api.dependencies import get_model_router as get_router
    return await get_router()


@router.get("/health", response_model=dict)
async def models_health(
    router: ModelRouter = Depends(get_model_router),
):
    """Check health of all model providers."""
    health_results = await router.health_check_all()
    
    return {
        name: {
            "provider": health.provider,
            "healthy": health.healthy,
            "error": health.error,
            "models": [m.model_dump() for m in health.models],
        }
        for name, health in health_results.items()
    }


@router.get("", response_model=dict)
async def list_models(
    router: ModelRouter = Depends(get_model_router),
):
    """List all available models."""
    return router.get_all_models()