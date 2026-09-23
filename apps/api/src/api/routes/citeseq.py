"""
Phase 128: Autonomous Single-Cell Spatial CITE-seq Multi-Modal API Routes.
"""
from typing import Dict, Any, Optional, List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from database.repositories.citeseq_repo import CITEseqRepository
from research.singlecell.citeseq_engine import CITEseqMultiModalEngine

router = APIRouter(prefix="/citeseq", tags=["Phase 128: CITE-seq Multi-Modal Mapping"])


class AnalyzeCITEseqRequest(BaseModel):
    sample_name: str = Field(..., example="Melanoma_TIL_CITEseq_54P")
    tissue_origin: str = Field("Tumor-Infiltrating Lymphocytes", example="Tumor-Infiltrating Lymphocytes")
    project_id: Optional[str] = Field(None)


@router.post("/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_citeseq_sample(
    req: AnalyzeCITEseqRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Executes single-cell CITE-seq surface protein & mRNA multi-modal analysis.
    """
    engine = CITEseqMultiModalEngine()
    pipeline_res = engine.simulate_citeseq_pipeline(
        sample_name=req.sample_name,
        tissue_origin=req.tissue_origin,
    )

    repo = CITEseqRepository(db)
    dataset = await repo.create_dataset(
        sample_name=req.sample_name,
        tissue_origin=req.tissue_origin,
        total_cells_profiled=pipeline_res["total_cells"],
        adt_panel_size=pipeline_res["adt_panel_size"],
        rna_features_count=24500,
        dsb_background_ambient_mean=1.85,
        wNN_modality_weight_protein=pipeline_res["wnn_weights"]["weight_protein_adt"],
        wNN_modality_weight_rna=pipeline_res["wnn_weights"]["weight_rna"],
        metadata_json={"summary": pipeline_res["summary"]},
        project_id=req.project_id,
    )

    # Persist antibody tags
    for tag in pipeline_res["tags"]:
        await repo.add_antibody_tag(
            dataset_id=dataset.id,
            tag_barcode=tag["tag_barcode"],
            marker_name=tag["marker"],
            clone_id=tag["clone"],
            isotype_control="IgG1-k",
            signal_to_noise_ratio=tag["snr"],
        )

    # Persist expressions
    for conc in pipeline_res["concordance_profiles"]:
        await repo.add_protein_expression(
            dataset_id=dataset.id,
            cell_cluster_id=conc["cell_type_annotation"],
            marker_name=conc["marker_name"],
            dsb_normalized_expression=conc["adt_dsb_normalized"],
            corresponding_rna_tpm=conc["rna_tpm"],
            concordance_spearman_rho=conc["concordance_rho"],
            discordance_pvalue=0.0001,
        )

    saved = await repo.get_dataset(dataset.id)
    return {
        "status": "success",
        "dataset_id": str(dataset.id),
        "sample_name": dataset.sample_name,
        "total_cells": dataset.total_cells_profiled,
        "antibodies_count": len(saved.antibodies) if saved else 0,
        "expressions_count": len(saved.expressions) if saved else 0,
        "wnn_weights": pipeline_res["wnn_weights"],
        "summary": pipeline_res["summary"],
    }


@router.get("/datasets", status_code=status.HTTP_200_OK)
async def list_citeseq_datasets(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """List CITE-seq multi-modal datasets."""
    repo = CITEseqRepository(db)
    datasets = await repo.list_datasets(limit=limit)
    return [
        {
            "id": str(d.id),
            "sample_name": d.sample_name,
            "tissue_origin": d.tissue_origin,
            "total_cells": d.total_cells_profiled,
            "adt_panel_size": d.adt_panel_size,
            "antibodies_count": len(d.antibodies),
            "expressions_count": len(d.expressions),
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in datasets
    ]


@router.get("/datasets/{dataset_id}", status_code=status.HTTP_200_OK)
async def get_citeseq_dataset(
    dataset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get single CITE-seq dataset details."""
    repo = CITEseqRepository(db)
    dataset = await repo.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset {dataset_id} not found",
        )
    return {
        "id": str(dataset.id),
        "sample_name": dataset.sample_name,
        "tissue_origin": dataset.tissue_origin,
        "total_cells": dataset.total_cells_profiled,
        "adt_panel_size": dataset.adt_panel_size,
        "wnn_weights": {
            "protein": dataset.wNN_modality_weight_protein,
            "rna": dataset.wNN_modality_weight_rna,
        },
        "antibodies": [
            {
                "tag_barcode": a.tag_barcode,
                "marker_name": a.marker_name,
                "clone_id": a.clone_id,
                "snr": a.signal_to_noise_ratio,
            }
            for a in dataset.antibodies
        ],
        "expressions": [
            {
                "cell_cluster": e.cell_cluster_id,
                "marker": e.marker_name,
                "dsb_expression": e.dsb_normalized_expression,
                "rna_tpm": e.corresponding_rna_tpm,
                "rho": e.concordance_spearman_rho,
            }
            for e in dataset.expressions
        ],
    }
