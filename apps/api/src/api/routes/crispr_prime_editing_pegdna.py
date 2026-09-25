"""FastAPI routes for Phase 180: CRISPR Prime Editing pegRNA Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.crispr_prime_editing_pegdna_repo import CRISPRPrimeEditingPegDNARepository
from research.genomics.crispr_prime_editing_pegdna_engine import CRISPRPrimeEditingPegDNAEngine

router = APIRouter(prefix="/crispr-prime-editing-pegdna", tags=["CRISPR Prime Editing pegRNA"])


class SimulatePegDNARequest(BaseModel):
    name: str = Field(..., example="HBB E6V Sickle Cell Prime Editing Design")
    target_gene: str = Field(..., example="HBB")
    intended_mutation_type: str = Field(default="point_substitution")
    pbs_length_nt: int = Field(default=13, ge=9, le=18)
    rtt_length_nt: int = Field(default=15, ge=10, le=25)
    nick_to_edit_distance_bp: int = Field(default=3, ge=1, le=20)
    pe_system_version: str = Field(default="PEmax_epegRNA")


@router.post("/simulate", status_code=status.HTTP_201_CREATED)
async def simulate_and_persist_pegdna(
    req: SimulatePegDNARequest,
    session: AsyncSession = Depends(get_db_session),
):
    engine = CRISPRPrimeEditingPegDNAEngine()
    result = engine.simulate_pegdna_design(
        target_gene=req.target_gene,
        intended_mutation_type=req.intended_mutation_type,
        pbs_length_nt=req.pbs_length_nt,
        rtt_length_nt=req.rtt_length_nt,
        nick_to_edit_distance_bp=req.nick_to_edit_distance_bp,
        pe_system_version=req.pe_system_version,
    )

    repo = CRISPRPrimeEditingPegDNARepository(session)
    study = await repo.create_study(
        name=req.name,
        target_gene=result.target_gene,
        intended_mutation_type=result.intended_mutation_type,
        pbs_length_nt=result.pbs_length_nt,
        rtt_length_nt=result.rtt_length_nt,
        nick_to_edit_distance_bp=result.nick_to_edit_distance_bp,
        predicted_prime_editing_efficiency=result.predicted_prime_editing_efficiency,
        indel_byproduct_frequency=result.indel_byproduct_frequency,
        flap_equilibrium_ratio=result.flap_equilibrium_ratio,
        pe_system_version=result.pe_system_version,
        status="completed",
        parameters={
            "fidelity_index": result.fidelity_index,
        },
        summary_report=result.design_recommendation,
    )

    for c in result.pegdna_candidates:
        await repo.add_pegdna_design(
            study_id=study.id,
            candidate_id=c.candidate_id,
            spacer_sequence_20nt=c.spacer_sequence_20nt,
            pbs_sequence=c.pbs_sequence,
            rtt_sequence_with_edit=c.rtt_sequence_with_edit,
            tevpre_structural_motif=c.tevpre_structural_motif,
            deep_pe_score=c.deep_pe_score,
            melting_temp_pbs_celsius=c.melting_temp_pbs_celsius,
        )

    for f in result.flap_kinetics:
        await repo.add_flap_metric(
            study_id=study.id,
            flap_position_nt=f.flap_position_nt,
            gibbs_free_energy_edited_flap_kcal=f.gibbs_free_energy_edited_flap_kcal,
            gibbs_free_energy_unmodified_flap_kcal=f.gibbs_free_energy_unmodified_flap_kcal,
            fen1_endonuclease_cleavage_rate=f.fen1_endonuclease_cleavage_rate,
            incorporation_probability=f.incorporation_probability,
        )

    return {
        "id": str(study.id),
        "name": study.name,
        "target_gene": study.target_gene,
        "intended_mutation_type": study.intended_mutation_type,
        "predicted_prime_editing_efficiency": study.predicted_prime_editing_efficiency,
        "indel_byproduct_frequency": study.indel_byproduct_frequency,
        "flap_equilibrium_ratio": study.flap_equilibrium_ratio,
        "fidelity_index": result.fidelity_index,
        "recommendation": result.design_recommendation,
        "pegdna_candidates": [
            {
                "candidate_id": cand.candidate_id,
                "spacer_sequence_20nt": cand.spacer_sequence_20nt,
                "pbs_sequence": cand.pbs_sequence,
                "rtt_sequence_with_edit": cand.rtt_sequence_with_edit,
                "deep_pe_score": cand.deep_pe_score,
                "melting_temp_pbs_celsius": cand.melting_temp_pbs_celsius,
            }
            for cand in result.pegdna_candidates
        ],
        "flap_kinetics": [
            {
                "flap_position_nt": fk.flap_position_nt,
                "gibbs_free_energy_edited_flap_kcal": fk.gibbs_free_energy_edited_flap_kcal,
                "fen1_endonuclease_cleavage_rate": fk.fen1_endonuclease_cleavage_rate,
                "incorporation_probability": fk.incorporation_probability,
            }
            for fk in result.flap_kinetics
        ],
    }


@router.get("/studies")
async def list_studies(
    limit: int = Query(default=50, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    repo = CRISPRPrimeEditingPegDNARepository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "target_gene": s.target_gene,
            "intended_mutation_type": s.intended_mutation_type,
            "predicted_prime_editing_efficiency": s.predicted_prime_editing_efficiency,
            "indel_byproduct_frequency": s.indel_byproduct_frequency,
            "pe_system_version": s.pe_system_version,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in studies
    ]
