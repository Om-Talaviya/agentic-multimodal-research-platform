"""FastAPI Route for smFRET Kinetics (Phase 160)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.single_molecule_fret_repo import SingleMoleculeFRETRepository
from research.biophysics.smfret_kinetics_engine import (
    smFRETKineticsEngine,
    smFRETRequest,
    smFRETResult,
)

router = APIRouter(prefix="/smfret-kinetics", tags=["smFRET Kinetics"])


@router.post("/analyze", response_model=smFRETResult)
async def analyze_smfret_kinetics(
    payload: smFRETRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = smFRETKineticsEngine()
    result = engine.analyze_traces(payload)

    repo = SingleMoleculeFRETRepository(db)
    study = await repo.create_study(
        biomolecule_name=result.biomolecule_name,
        donor_fluorophore=result.donor_fluorophore,
        acceptor_fluorophore=result.acceptor_fluorophore,
        forster_distance_r0_nm=result.forster_distance_r0_nm,
        molecules_analyzed_count=result.molecules_analyzed_count,
        mean_fret_efficiency=result.mean_fret_efficiency,
        transition_rate_k_open_s=result.transition_rate_k_open_s,
        transition_rate_k_close_s=result.transition_rate_k_close_s,
    )

    for s in result.conformational_states:
        await repo.add_state_transition(
            study_id=study.id,
            state_label=s.state_label,
            fret_efficiency_peak=s.fret_efficiency_peak,
            mean_dwell_time_ms=s.mean_dwell_time_ms,
            state_occupancy_percentage=s.state_occupancy_percentage,
            apparent_distance_angstrom=s.apparent_distance_angstrom,
        )

    for t in result.sample_time_traces:
        await repo.add_trajectory(
            study_id=study.id,
            molecule_index=t.molecule_index,
            donor_lifetime_seconds=t.donor_lifetime_seconds,
            acceptor_lifetime_seconds=t.acceptor_lifetime_seconds,
            total_transitions_observed=t.total_transitions_observed,
            single_step_photobleaching=t.single_step_photobleaching,
        )

    return result
