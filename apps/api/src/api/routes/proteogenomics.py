"""API Routes for Proteogenomics & Mass Spectrometry Spectral Libraries (Phase 95)."""

import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.proteogenomics_repo import ProteogenomicsRepository
from research.proteomics.proteogenomics_engine import ProteogenomicsEngine

router = APIRouter(prefix="/proteogenomics", tags=["Proteogenomics & MS/MS"])


class TheoreticalSpectrumRequest(BaseModel):
    peptide_sequence: str = Field(..., example="LVNEVTEFAK")
    charge: int = Field(default=2, example=2)


class ProteogenomicSearchRequest(BaseModel):
    sample_id: str = Field(..., example="Melanoma_Patient_Tumor_MS01")
    instrument_type: str = Field(default="Orbitrap Exploris 480", example="Orbitrap Exploris 480")
    search_database: str = Field(default="UniProtKB + Ribo-Seq Novel ORFs", example="UniProtKB + Ribo-Seq Novel ORFs")
    fdr_threshold: float = Field(default=0.01, example=0.01)
    workspace_id: Optional[str] = None


@router.post("/fragmentation-spectrum")
async def generate_fragmentation_spectrum(request: TheoreticalSpectrumRequest):
    """Predict theoretical b-ion and y-ion fragmentation spectrum for a peptide."""
    engine = ProteogenomicsEngine()
    spectrum = engine.generate_theoretical_spectrum(sequence=request.peptide_sequence, charge=request.charge)
    return {"status": "SUCCESS", "spectrum": spectrum}


@router.post("/search", status_code=status.HTTP_201_CREATED)
async def run_proteogenomic_search(
    request: ProteogenomicSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Execute proteogenomic database search to discover canonical and novel non-canonical ORFs."""
    engine = ProteogenomicsEngine()
    result = engine.run_proteogenomic_search(
        sample_id=request.sample_id,
        instrument_type=request.instrument_type,
        search_database=request.search_database,
        fdr_threshold=request.fdr_threshold,
    )

    repo = ProteogenomicsRepository(db)
    ws_id = uuid.UUID(request.workspace_id) if request.workspace_id else uuid.uuid4()

    exp = await repo.create_experiment(
        workspace_id=ws_id,
        sample_id=result["sample_id"],
        instrument_type=result["instrument_type"],
        search_database=result["search_database"],
        fdr_threshold=result["fdr_threshold"],
        total_spectra_analyzed=result["total_spectra_analyzed"],
        identified_peptides_count=result["identified_peptides_count"],
        novel_noncanonical_orfs_count=result["novel_noncanonical_orfs_count"],
        analysis_metadata={"summary": result["summary"]},
    )

    for psm in result["psm_matches"]:
        await repo.add_psm_match(
            experiment_id=exp.id,
            scan_number=psm["scan_number"],
            peptide_sequence=psm["peptide_sequence"],
            protein_accession=psm["protein_accession"],
            charge_state=psm["charge_state"],
            precursor_mz=psm["precursor_mz"],
            calculated_mz=psm["calculated_mz"],
            hyperscore=psm["hyperscore"],
            posterior_error_prob=psm["posterior_error_prob"],
            is_novel_variant=psm["is_novel_variant"],
        )

    for junc in result["novel_junctions"]:
        await repo.add_novel_junction(
            experiment_id=exp.id,
            chromosome=junc["chromosome"],
            junction_start=junc["junction_start"],
            junction_end=junc["junction_end"],
            supporting_reads_count=junc["supporting_reads_count"],
            peptide_evidence=junc["peptide_evidence"],
            frameshift_flag=junc["frameshift_flag"],
        )

    return {
        "status": "SUCCESS",
        "experiment_id": str(exp.id),
        "sample_id": exp.sample_id,
        "identified_peptides_count": exp.identified_peptides_count,
        "novel_noncanonical_orfs_count": exp.novel_noncanonical_orfs_count,
        "psm_matches": result["psm_matches"],
        "novel_junctions": result["novel_junctions"],
        "summary": result["summary"],
    }


@router.get("/experiments/{experiment_id}")
async def get_experiment_details(
    experiment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Retrieve full proteogenomic experiment and spectrum matches."""
    repo = ProteogenomicsRepository(db)
    try:
        eid = uuid.UUID(experiment_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid experiment UUID format")

    exp = await repo.get_experiment(eid)
    if not exp:
        raise HTTPException(status_code=404, detail="Proteogenomic experiment not found")

    return {
        "id": str(exp.id),
        "sample_id": exp.sample_id,
        "instrument_type": exp.instrument_type,
        "total_spectra_analyzed": exp.total_spectra_analyzed,
        "identified_peptides_count": exp.identified_peptides_count,
        "novel_noncanonical_orfs_count": exp.novel_noncanonical_orfs_count,
        "psm_matches": [
            {
                "scan_number": psm.scan_number,
                "peptide_sequence": psm.peptide_sequence,
                "protein_accession": psm.protein_accession,
                "hyperscore": psm.hyperscore,
                "is_novel_variant": psm.is_novel_variant,
            }
            for psm in exp.psm_matches
        ],
        "novel_junctions": [
            {
                "chromosome": j.chromosome,
                "junction_start": j.junction_start,
                "junction_end": j.junction_end,
                "peptide_evidence": j.peptide_evidence,
            }
            for j in exp.novel_junctions
        ],
    }
