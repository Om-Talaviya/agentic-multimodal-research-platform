"""REST API routes for Synthetic Instruction Dataset Generation & Active Learning Engine."""

import json
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db_session
from database.models.dataset_synthesis import (
    DBAlignmentExport,
    DBInstructionSample,
    DBSyntheticDataset,
)
from database.repositories.dataset_synthesis_repo import DatasetSynthesisRepository
from research.datasets.synthesizer import InstructionDatasetSynthesizer
from shared.auth import User
from shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/datasets", tags=["datasets"])


# ---------------- Request & Response Schemas ----------------

class SynthesizeDatasetPayload(BaseModel):
    name: str = Field(..., min_length=3, max_length=512)
    description: Optional[str] = None
    dataset_format: str = Field(default="alpaca_sft", pattern="^(alpaca_sft|sharegpt|dpo_preference|rl_trajectory|cot_reasoning)$")
    domain_field: str = Field(default="general_science")
    target_model_family: str = Field(default="llama_3")
    sample_count: int = Field(default=5, ge=1, le=100)
    topic: str = Field(..., min_length=3)
    research_findings: List[Dict[str, Any]] = Field(default_factory=list)
    workspace_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None


class EvolveSamplePayload(BaseModel):
    strategy: str = Field(default="in_depth_expansion", pattern="^(in_depth_expansion|in_breadth_variation|constraint_hardening|adversarial_redteaming|cot_decomposition)$")


class CurationPayload(BaseModel):
    verdict: str = Field(..., pattern="^(accepted|rejected|edited)$")
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    chosen_response: Optional[str] = None


class ExportDatasetPayload(BaseModel):
    export_format: str = Field(default="jsonl", pattern="^(jsonl|parquet|huggingface_arrow|csv)$")


# ---------------- Route Implementations ----------------

@router.get("/metrics")
async def get_dataset_synthesis_metrics(
    workspace_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Query platform-wide synthetic datasets, sample counts, and quality distributions."""
    repo = DatasetSynthesisRepository(session)
    return await repo.get_synthesis_metrics(workspace_id=workspace_id)


@router.post("/synthesize", status_code=status.HTTP_201_CREATED)
async def synthesize_instruction_dataset(
    payload: SynthesizeDatasetPayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Synthesize new fine-tuning instruction dataset from research findings."""
    repo = DatasetSynthesisRepository(session)

    dataset = DBSyntheticDataset(
        user_id=current_user.id,
        workspace_id=payload.workspace_id,
        project_id=payload.project_id,
        name=payload.name,
        description=payload.description or f"Synthesized fine-tuning dataset for {payload.topic}",
        dataset_format=payload.dataset_format,
        domain_field=payload.domain_field,
        target_model_family=payload.target_model_family,
        status="synthesizing",
    )
    created_dataset = await repo.create_dataset(dataset)

    # Generate samples via synthesizer engine
    raw_samples = InstructionDatasetSynthesizer.synthesize_from_research_findings(
        title=payload.name,
        topic=payload.topic,
        findings=payload.research_findings if payload.research_findings else None,
        dataset_format=payload.dataset_format,
        sample_count=payload.sample_count,
    )

    db_samples = [
        DBInstructionSample(
            dataset_id=created_dataset.id,
            sample_index=s["sample_index"],
            system_prompt=s["system_prompt"],
            instruction=s["instruction"],
            input_context=s["input_context"],
            chosen_response=s["chosen_response"],
            rejected_response=s["rejected_response"],
            cot_reasoning_trace=s["cot_reasoning_trace"],
            evolution_strategy=s["evolution_strategy"],
            quality_score=s["quality_score"],
            toxicity_score=s["toxicity_score"],
            hallucination_risk=s["hallucination_risk"],
            dedup_hash=s["dedup_hash"],
            curation_verdict=s["curation_verdict"],
            metadata_json=s["metadata_json"],
        )
        for s in raw_samples
    ]

    await repo.batch_add_samples(created_dataset.id, db_samples)
    await repo.update_dataset_status(created_dataset.id, "curated", total_samples=len(db_samples))

    return {
        "id": str(created_dataset.id),
        "name": created_dataset.name,
        "dataset_format": created_dataset.dataset_format,
        "total_samples": len(db_samples),
        "status": "curated",
        "created_at": created_dataset.created_at.isoformat(),
    }


@router.get("")
async def list_synthetic_datasets(
    workspace_id: Optional[uuid.UUID] = Query(None),
    project_id: Optional[uuid.UUID] = Query(None),
    dataset_format: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> List[Dict[str, Any]]:
    """List synthetic instruction datasets."""
    repo = DatasetSynthesisRepository(session)
    datasets = await repo.list_datasets(
        user_id=current_user.id if not workspace_id else None,
        workspace_id=workspace_id,
        project_id=project_id,
        dataset_format=dataset_format,
        limit=limit,
        offset=offset,
    )
    return [
        {
            "id": str(d.id),
            "name": d.name,
            "description": d.description,
            "dataset_format": d.dataset_format,
            "domain_field": d.domain_field,
            "target_model_family": d.target_model_family,
            "total_samples": d.total_samples,
            "status": d.status,
            "created_at": d.created_at.isoformat(),
        }
        for d in datasets
    ]


@router.get("/{dataset_id}")
async def get_synthetic_dataset(
    dataset_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Fetch complete synthetic dataset with instruction samples and export history."""
    repo = DatasetSynthesisRepository(session)
    dataset = await repo.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Synthetic dataset not found")

    return {
        "id": str(dataset.id),
        "name": dataset.name,
        "description": dataset.description,
        "dataset_format": dataset.dataset_format,
        "domain_field": dataset.domain_field,
        "target_model_family": dataset.target_model_family,
        "total_samples": dataset.total_samples,
        "quality_filter_threshold": dataset.quality_filter_threshold,
        "status": dataset.status,
        "created_at": dataset.created_at.isoformat(),
        "samples": [
            {
                "id": str(s.id),
                "sample_index": s.sample_index,
                "instruction": s.instruction,
                "input_context": s.input_context,
                "chosen_response": s.chosen_response,
                "rejected_response": s.rejected_response,
                "cot_reasoning_trace": s.cot_reasoning_trace,
                "evolution_strategy": s.evolution_strategy,
                "quality_score": s.quality_score,
                "toxicity_score": s.toxicity_score,
                "hallucination_risk": s.hallucination_risk,
                "curation_verdict": s.curation_verdict,
            }
            for s in dataset.samples
        ],
        "exports": [
            {
                "id": str(e.id),
                "export_format": e.export_format,
                "sample_count": e.sample_count,
                "file_size_bytes": e.file_size_bytes,
                "exported_at": e.exported_at.isoformat(),
            }
            for e in dataset.exports
        ],
    }


@router.patch("/{dataset_id}/samples/{sample_id}")
async def curate_instruction_sample(
    dataset_id: uuid.UUID,
    sample_id: uuid.UUID,
    payload: CurationPayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Active-learning human/agent curation of an instruction sample."""
    repo = DatasetSynthesisRepository(session)
    sample = await repo.update_sample_curation(
        sample_id=sample_id,
        verdict=payload.verdict,
        quality_score=payload.quality_score,
        chosen_response=payload.chosen_response,
    )
    if not sample:
        raise HTTPException(status_code=404, detail="Instruction sample not found")

    return {
        "id": str(sample.id),
        "dataset_id": str(sample.dataset_id),
        "curation_verdict": sample.curation_verdict,
        "quality_score": sample.quality_score,
    }


@router.post("/{dataset_id}/export", status_code=status.HTTP_201_CREATED)
async def export_synthetic_dataset(
    dataset_id: uuid.UUID,
    payload: ExportDatasetPayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Export synthetic dataset into standardized fine-tuning JSONL payload."""
    repo = DatasetSynthesisRepository(session)
    dataset = await repo.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Synthetic dataset not found")

    raw_samples = [
        {
            "instruction": s.instruction,
            "input_context": s.input_context,
            "chosen_response": s.chosen_response,
            "rejected_response": s.rejected_response,
            "cot_reasoning_trace": s.cot_reasoning_trace,
            "system_prompt": s.system_prompt,
        }
        for s in dataset.samples
        if s.curation_verdict != "rejected"
    ]

    formatted_data = InstructionDatasetSynthesizer.format_dataset(
        samples=raw_samples,
        dataset_format=dataset.dataset_format,
    )

    jsonl_content = "\n".join([json.dumps(item) for item in formatted_data])
    file_bytes = len(jsonl_content.encode("utf-8"))

    export = DBAlignmentExport(
        dataset_id=dataset_id,
        export_format=payload.export_format,
        sample_count=len(formatted_data),
        file_size_bytes=file_bytes,
    )
    created_export = await repo.record_export(export)
    await repo.update_dataset_status(dataset_id, "exported")

    return {
        "id": str(created_export.id),
        "dataset_id": str(dataset_id),
        "export_format": created_export.export_format,
        "sample_count": created_export.sample_count,
        "file_size_bytes": created_export.file_size_bytes,
        "exported_at": created_export.exported_at.isoformat(),
        "preview_jsonl": jsonl_content[:2000],
    }


@router.delete("/{dataset_id}")
async def delete_synthetic_dataset(
    dataset_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Delete synthetic dataset and child samples."""
    repo = DatasetSynthesisRepository(session)
    deleted = await repo.delete_dataset(dataset_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Synthetic dataset not found")
    return {"message": "Synthetic dataset deleted successfully"}
