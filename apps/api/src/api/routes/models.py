"""Model provider and intelligent ecosystem optimization routes."""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ai.providers.router import ModelRouter
from ai.router.optimizer import (
    OptimizationProfile,
    OptimizationResult,
    PRESET_PROFILES,
    ProfileType,
)
from ai.schemas import ModelCapability, ProviderHealth

router = APIRouter(prefix="/models", tags=["models"])


async def get_model_router() -> ModelRouter:
    from api.dependencies import get_model_router as get_router
    return await get_router()


class OptimizeRequest(BaseModel):
    """Payload for simulating multi-parameter model routing optimization."""
    task: Optional[str] = Field(default=None, description="Research or sub-agent task type")
    profile: Optional[str] = Field(default="balanced", description="Preset optimization profile name")
    custom_profile: Optional[OptimizationProfile] = Field(default=None, description="Custom weight parameters")
    required_capabilities: Optional[List[str]] = Field(default=None, description="Mandatory model capabilities")


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


@router.get("/profiles", response_model=Dict[str, Any])
async def list_optimization_profiles():
    """List preset model ecosystem optimization profiles with weight breakdowns."""
    return {
        profile_key.value: profile.model_dump()
        for profile_key, profile in PRESET_PROFILES.items()
    }


@router.post("/optimize", response_model=Dict[str, Any])
async def optimize_model_selection(
    payload: OptimizeRequest,
    router: ModelRouter = Depends(get_model_router),
):
    """Simulate and rank candidate models using multi-parameter Pareto optimization."""
    target_profile: Optional[OptimizationProfile] = payload.custom_profile
    if not target_profile and payload.profile:
        try:
            ptype = ProfileType(payload.profile)
            target_profile = PRESET_PROFILES.get(ptype)
        except ValueError:
            target_profile = PRESET_PROFILES[ProfileType.BALANCED]

    target_caps = None
    if payload.required_capabilities:
        target_caps = {
            ModelCapability(c) for c in payload.required_capabilities
            if c in [cap.value for cap in ModelCapability]
        }

    result = router.optimize_routing(
        task=payload.task,
        profile=target_profile,
        required_capabilities=target_caps,
    )
    return result.model_dump()


@router.get("", response_model=dict)
async def list_models(
    router: ModelRouter = Depends(get_model_router),
):
    """List all available models."""
    return router.get_all_models()