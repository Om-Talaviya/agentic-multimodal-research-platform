"""Trial Telemetry Routes (Phase 122)."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from database.repositories.trial_telemetry_repo import TrialTelemetryRepository
from research.clinical.telemetry_engine import TrialTelemetrySentinelEngine

router = APIRouter(prefix="/trial-telemetry", tags=["Trial Telemetry Engine"])

class TelemetryScanRequest(BaseModel):
    protocol_number: str = Field(..., example="PROTO-ONC-2026-09")
    total_subjects: int = Field(default=150, example=150)
    anomaly_threshold: float = Field(default=0.92, example=0.92)
    workspace_id: Optional[str] = None

@router.post("/scan-anomalies", status_code=status.HTTP_201_CREATED)
async def scan_telemetry_endpoint(req: TelemetryScanRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    engine = TrialTelemetrySentinelEngine()
    res = engine.scan_telemetry_anomalies(req.protocol_number, req.total_subjects, req.anomaly_threshold)
    repo = TrialTelemetryRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else uuid.uuid4()
    c = await repo.create_cohort(
        workspace_id=ws_id,
        protocol_number=res["protocol"],
        total_active_subjects=res["subjects"],
        telemetry_frequency_hz=1.0,
        anomaly_alert_threshold=res["threshold"]
    )
    for a in res["anomalies"]:
        await repo.add_anomaly(
            cohort_id=c.id,
            subject_id=a["subject"],
            biomarker_stream_type=a["stream"],
            anomaly_severity_score=a["score"],
            ecog_performance_delta=a["ecog"]
        )
    return {"status": "SUCCESS", "cohort_id": str(c.id), "result": res}

@router.get("/cohorts/{cohort_id}")
async def get_cohort(cohort_id: str, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    repo = TrialTelemetryRepository(db)
    try:
        cid = uuid.UUID(cohort_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")
    c = await repo.get_cohort(cid)
    if not c:
        raise HTTPException(status_code=404, detail="Cohort not found")
    return {"id": str(c.id), "protocol": c.protocol_number}
