"""
FastAPI router for Autonomous Computational Immunology & TCR-pMHC Neoantigen Binding Predictor (Phase 55).
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session
from database.repositories.immunology_repo import ImmunologyRepository
from research.immunology.immunology_engine import ComputationalImmunologyEngine

router = APIRouter(prefix="/immunology", tags=["Computational Immunology"])


class MutationItem(BaseModel):
    gene_symbol: str = "GENE"
    mutation_variant: str = "MUT"
    peptide_sequence: str
    wildtype_sequence: Optional[str] = None


class CreateScreenRequest(BaseModel):
    patient_id: str = Field(default="PT-MEL-2026-09")
    tumor_type: str = Field(default="Cutaneous Melanoma")
    hla_alleles: List[str] = Field(default=["HLA-A*02:01", "HLA-B*07:02", "HLA-C*07:01"])
    mutations: List[MutationItem] = Field(
        default=[
            MutationItem(gene_symbol="BRAF", mutation_variant="V600E", peptide_sequence="EDLTVKIGD", wildtype_sequence="EDLTVKIGV"),
            MutationItem(gene_symbol="NRAS", mutation_variant="Q61K", peptide_sequence="ILDTAGKEEY", wildtype_sequence="ILDTAGQEEY"),
        ]
    )


class DesignVaccineRequest(BaseModel):
    construct_name: str = Field(default="NeoVax-Melanoma-PolyEpitope")
    construct_type: str = Field(default="mRNA_LNP")
    linker: str = Field(default="AAY")


@router.post("/screens")
async def run_neoantigen_screening(
    request: CreateScreenRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Executes neoantigen prediction and epitope immunogenicity prioritization across patient HLA alleles."""
    repo = ImmunologyRepository(db)
    screen = await repo.create_screen(
        patient_id=request.patient_id,
        tumor_type=request.tumor_type,
        hla_alleles=request.hla_alleles,
        mutation_count=len(request.mutations),
    )

    all_predictions = []
    for mut in request.mutations:
        for allele in request.hla_alleles:
            pred = ComputationalImmunologyEngine.predict_pMHC_affinity(
                peptide=mut.peptide_sequence,
                hla_allele=allele,
                mutation_variant=mut.mutation_variant,
                gene_symbol=mut.gene_symbol,
                wildtype_sequence=mut.wildtype_sequence,
            )
            all_predictions.append(pred)

    await repo.add_epitopes(screen.id, all_predictions)
    refreshed_screen = await repo.get_screen(screen.id)
    return refreshed_screen


@router.get("/screens")
async def list_neoantigen_screens(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
):
    """Lists neoantigen screening campaigns."""
    repo = ImmunologyRepository(db)
    return await repo.list_screens(limit=limit)


@router.get("/screens/{screen_id}")
async def get_neoantigen_screen(
    screen_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieves full screen details including epitopes and vaccine constructs."""
    repo = ImmunologyRepository(db)
    screen = await repo.get_screen(screen_id)
    if not screen:
        raise HTTPException(status_code=404, detail="Neoantigen screen not found")
    return screen


@router.post("/screens/{screen_id}/design-vaccine")
async def design_vaccine_construct(
    screen_id: str,
    request: DesignVaccineRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Generates an optimized poly-epitope mRNA/peptide vaccine construct for the screened epitopes."""
    repo = ImmunologyRepository(db)
    screen = await repo.get_screen(screen_id)
    if not screen:
        raise HTTPException(status_code=404, detail="Neoantigen screen not found")

    epitopes_dict = [
        {
            "peptide_sequence": e.peptide_sequence,
            "composite_priority_score": e.composite_priority_score,
            "gene_symbol": e.gene_symbol,
            "hla_allele": e.hla_allele,
        }
        for e in screen.epitopes
    ]

    design = ComputationalImmunologyEngine.design_vaccine_construct(
        screen_id=screen_id,
        epitopes=epitopes_dict,
        construct_name=request.construct_name,
        construct_type=request.construct_type,
        linker=request.linker,
    )

    construct = await repo.create_vaccine_construct(
        screen_id=screen_id,
        construct_name=design["construct_name"],
        construct_type=design["construct_type"],
        ordered_epitopes=design["ordered_epitopes"],
        linker_sequences=design["linker_sequences"],
        full_polyepitope_sequence=design["full_polyepitope_sequence"],
        junctional_immunogenicity_risk=design["junctional_immunogenicity_risk"],
        predicted_expression_efficiency=design["predicted_expression_efficiency"],
    )
    return construct
