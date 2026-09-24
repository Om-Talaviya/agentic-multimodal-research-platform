"""FastAPI Route for Hi-C Chromatin Loop Mapping (Phase 152)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.chromatin_looping_repo import ChromatinLoopRepository
from research.genomics.chromatin_loop_engine import (
    ChromatinLoopEngine,
    ChromatinLoopRequest,
    ChromatinLoopResult,
)

router = APIRouter(prefix="/chromatin-loop", tags=["Chromatin Loop"])


@router.post("/map", response_model=ChromatinLoopResult)
async def map_chromatin_loops(
    payload: ChromatinLoopRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = ChromatinLoopEngine()
    result = engine.map_loops(payload)

    repo = ChromatinLoopRepository(db)
    study = await repo.create_study(
        cell_line_name=result.cell_line_name,
        chromosome=result.chromosome,
        genomic_resolution_bp=result.genomic_resolution_bp,
        total_loops_detected=result.total_loops_detected,
        tad_count=result.tad_count,
        mean_insulation_score=result.mean_insulation_score,
        mean_loop_span_kb=result.mean_loop_span_kb,
    )

    for e in result.contact_edges:
        await repo.add_contact_edge(
            study_id=study.id,
            enhancer_locus=e.enhancer_locus,
            target_gene=e.target_gene,
            contact_frequency=e.contact_frequency,
            loop_span_bp=e.loop_span_bp,
            ctcf_convergent_motif=e.ctcf_convergent_motif,
            activation_log2fc=e.activation_log2fc,
        )

    for t in result.tad_boundaries:
        await repo.add_tad_boundary(
            study_id=study.id,
            start_bp=t.start_bp,
            end_bp=t.end_bp,
            insulation_score=t.insulation_score,
            ctcf_occupancy_score=t.ctcf_occupancy_score,
        )

    return result
