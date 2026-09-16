"""
FastAPI router for Antibody-Drug Conjugate (ADC) Design (Phase 59).
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session
from database.repositories.adc_design_repo import ADCDesignRepository
from research.adc.adc_engine import ADCDesignEngine

router = APIRouter(prefix="/adc-design", tags=["ADC Payload-Linker Design"])


class CreateCampaignRequest(BaseModel):
    antibody_name: str = Field(default="Trastuzumab")
    target_antigen: str = Field(default="HER2")
    conjugation_chemistry: str = Field(default="Maleimide-Cysteine")
    target_dar: float = Field(default=8.0)


@router.post("/campaigns", status_code=status.HTTP_201_CREATED)
async def create_adc_campaign(
    request: CreateCampaignRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Executes ADC payload-linker screening, DAR optimization, and therapeutic index ranking."""
    repo = ADCDesignRepository(db)
    camp = await repo.create_campaign(
        antibody_name=request.antibody_name,
        target_antigen=request.target_antigen,
        conjugation_chemistry=request.conjugation_chemistry,
        target_dar=request.target_dar,
    )

    constructs_data = ADCDesignEngine.screen_payload_linkers(
        antibody_name=request.antibody_name,
        target_antigen=request.target_antigen,
        target_dar=request.target_dar,
    )

    await repo.add_constructs(campaign_id=camp.id, constructs_data=constructs_data)
    return await repo.get_campaign(camp.id)


@router.get("/campaigns")
async def list_campaigns(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
):
    """Lists ADC design campaigns."""
    repo = ADCDesignRepository(db)
    return await repo.list_campaigns(limit=limit)


@router.get("/campaigns/{campaign_id}")
async def get_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieves full campaign details with payload-linker constructs."""
    repo = ADCDesignRepository(db)
    camp = await repo.get_campaign(campaign_id)
    if not camp:
        raise HTTPException(status_code=404, detail="ADC campaign not found")
    return camp
