"""Milestone v1.6 Routes (Phase 125)."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from database.repositories.milestone_v1_6_repo import MilestoneV16Repository
from research.automation.milestone_v1_6_engine import MilestoneV16Engine

router = APIRouter(prefix="/milestone-v1-6", tags=["Milestone v1.6 Centennial Platform"])

class MilestoneVerifyRequest(BaseModel):
    milestone_name: str = Field(default="Milestone v1.6 Centennial Frontier", example="Milestone v1.6 Centennial Frontier")
    workspace_id: Optional[str] = None

@router.post("/verify-platform", status_code=status.HTTP_201_CREATED)
async def verify_platform_endpoint(req: MilestoneVerifyRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    engine = MilestoneV16Engine()
    res = engine.verify_centennial_platform(req.milestone_name)
    repo = MilestoneV16Repository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else uuid.uuid4()
    m = await repo.create_orchestration_record(
        workspace_id=ws_id,
        milestone_name=res["milestone"],
        total_integrated_phases=res["total_phases"],
        system_readiness_score=res["readiness_score"],
        active_domain_engines_count=res["total_phases"]
    )
    return {"status": "SUCCESS", "milestone_id": str(m.id), "result": res}

@router.get("/records/{record_id}")
async def get_record(record_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    repo = MilestoneV16Repository(db)
    try:
        rid = uuid.UUID(record_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
    r = await repo.get_orchestration(rid)
    if not r:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"id": str(r.id), "milestone": r.milestone_name, "total_phases": r.total_integrated_phases}
