"""FastAPI routes for Phase 179: circRNA Biogenesis & miRNA Sponge Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.circrna_biogenesis_repo import CircRNABiogenesisRepository
from research.genomics.circrna_biogenesis_engine import CircRNABiogenesisEngine

router = APIRouter(prefix="/circrna-biogenesis", tags=["circRNA Biogenesis"])


class SimulateCircRNARequest(BaseModel):
    name: str = Field(..., example="CDR1as (ciRS-7) Back-Splicing & miR-7 Sponge Analysis")
    host_gene_symbol: str = Field(..., example="CDR1as")
    genomic_locus: str = Field(default="chrX:139865339-139866824")
    exon_count: int = Field(default=3, ge=1, le=15)
    flanking_alu_elements_count: int = Field(default=2, ge=0, le=10)
    quaking_motif_present: bool = Field(default=True)


@router.post("/simulate", status_code=status.HTTP_201_CREATED)
async def simulate_and_persist_circrna(
    req: SimulateCircRNARequest,
    session: AsyncSession = Depends(get_db_session),
):
    engine = CircRNABiogenesisEngine()
    result = engine.simulate_circrna_biogenesis(
        host_gene_symbol=req.host_gene_symbol,
        genomic_locus=req.genomic_locus,
        exon_count=req.exon_count,
        flanking_alu_elements_count=req.flanking_alu_elements_count,
        quaking_motif_present=req.quaking_motif_present,
    )

    repo = CircRNABiogenesisRepository(session)
    study = await repo.create_study(
        name=req.name,
        host_gene_symbol=result.host_gene_symbol,
        genomic_locus=result.genomic_locus,
        exon_count=result.exon_count,
        flanking_alu_elements_count=result.flanking_alu_elements_count,
        backsplice_efficiency_score=result.backsplice_efficiency_score,
        circular_form_half_life_hours=result.circular_form_half_life_hours,
        total_mirna_sponge_binding_sites=result.total_mirna_sponge_binding_sites,
        quaking_rbp_affinity_score=result.quaking_rbp_affinity_score,
        status="completed",
        parameters={
            "sponge_efficiency_index": result.sponge_efficiency_index,
            "quaking_motif_present": req.quaking_motif_present,
        },
        summary_report=result.biogenesis_summary,
    )

    for j in result.backsplice_junctions:
        await repo.add_backsplice_junction(
            study_id=study.id,
            junction_id=j.junction_id,
            donor_exon=j.donor_exon,
            acceptor_exon=j.acceptor_exon,
            junction_sequence=j.junction_sequence,
            junction_reads_ratio=j.junction_reads_ratio,
            flanking_repeat_match_score=j.flanking_repeat_match_score,
        )

    for s in result.mirna_sponge_targets:
        await repo.add_mirna_sponge_target(
            study_id=study.id,
            mirna_family=s.mirna_family,
            binding_site_start=s.binding_site_start,
            binding_site_end=s.binding_site_end,
            seed_match_type=s.seed_match_type,
            binding_free_energy_kcal_mol=s.binding_free_energy_kcal_mol,
            inhibition_potency_score=s.inhibition_potency_score,
        )

    return {
        "id": str(study.id),
        "name": study.name,
        "host_gene_symbol": study.host_gene_symbol,
        "genomic_locus": study.genomic_locus,
        "exon_count": study.exon_count,
        "backsplice_efficiency_score": study.backsplice_efficiency_score,
        "circular_form_half_life_hours": study.circular_form_half_life_hours,
        "total_mirna_sponge_binding_sites": study.total_mirna_sponge_binding_sites,
        "quaking_rbp_affinity_score": study.quaking_rbp_affinity_score,
        "sponge_efficiency_index": result.sponge_efficiency_index,
        "summary": result.biogenesis_summary,
        "backsplice_junctions": [
            {
                "junction_id": bj.junction_id,
                "donor_exon": bj.donor_exon,
                "acceptor_exon": bj.acceptor_exon,
                "junction_sequence": bj.junction_sequence,
                "junction_reads_ratio": bj.junction_reads_ratio,
                "flanking_repeat_match_score": bj.flanking_repeat_match_score,
            }
            for bj in result.backsplice_junctions
        ],
        "mirna_sponge_targets": [
            {
                "mirna_family": mt.mirna_family,
                "binding_site_start": mt.binding_site_start,
                "binding_site_end": mt.binding_site_end,
                "seed_match_type": mt.seed_match_type,
                "binding_free_energy_kcal_mol": mt.binding_free_energy_kcal_mol,
                "inhibition_potency_score": mt.inhibition_potency_score,
            }
            for mt in result.mirna_sponge_targets
        ],
    }


@router.get("/studies")
async def list_studies(
    limit: int = Query(default=50, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    repo = CircRNABiogenesisRepository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "host_gene_symbol": s.host_gene_symbol,
            "genomic_locus": s.genomic_locus,
            "backsplice_efficiency_score": s.backsplice_efficiency_score,
            "circular_form_half_life_hours": s.circular_form_half_life_hours,
            "total_mirna_sponge_binding_sites": s.total_mirna_sponge_binding_sites,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in studies
    ]
