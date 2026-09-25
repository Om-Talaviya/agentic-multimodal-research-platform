"""Repository for Phase 183: CAR-T Cell Exhaustion & Persistence Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.car_t_exhaustion_kinetics import CARTExhaustionStudy, CARTDifferentiationState, CARTExhaustionCheckpointMarker


class CARTExhaustionKineticsRepository:
    """Database operations for CAR-T exhaustion studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        car_construct_name: str,
        costimulatory_domain: str = "4-1BB",
        antigen_density_per_tumor_cell: float = 15000.0,
        tonic_signaling_level: str = "low",
        t_stem_cell_memory_pct: float = 38.5,
        tox_nr4a_epigenetic_exhaustion_score: float = 0.24,
        predicted_persistence_half_life_days: float = 185.0,
        in_vivo_antitumor_efficacy_score: float = 0.88,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CARTExhaustionStudy:
        study = CARTExhaustionStudy(
            name=name,
            car_construct_name=car_construct_name,
            costimulatory_domain=costimulatory_domain,
            antigen_density_per_tumor_cell=antigen_density_per_tumor_cell,
            tonic_signaling_level=tonic_signaling_level,
            t_stem_cell_memory_pct=t_stem_cell_memory_pct,
            tox_nr4a_epigenetic_exhaustion_score=tox_nr4a_epigenetic_exhaustion_score,
            predicted_persistence_half_life_days=predicted_persistence_half_life_days,
            in_vivo_antitumor_efficacy_score=in_vivo_antitumor_efficacy_score,
            status=status,
            parameters=parameters or {},
            summary_report=summary_report,
        )
        self.session.add(study)
        await self.session.flush()
        await self.session.refresh(study)
        return study

    async def add_differentiation_state(
        self,
        study_id: UUID,
        state_name: str,
        population_percentage: float,
        tcf7_expression_level: float,
        proliferative_capacity_score: float,
        cytolytic_granzyme_b_score: float,
    ) -> CARTDifferentiationState:
        item = CARTDifferentiationState(
            study_id=study_id,
            state_name=state_name,
            population_percentage=population_percentage,
            tcf7_expression_level=tcf7_expression_level,
            proliferative_capacity_score=proliferative_capacity_score,
            cytolytic_granzyme_b_score=cytolytic_granzyme_b_score,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def add_checkpoint_marker(
        self,
        study_id: UUID,
        marker_symbol: str,
        surface_density_molecules: float,
        epigenetic_chromatin_accessibility_score: float,
        reversibility_potential_pct: float,
    ) -> CARTExhaustionCheckpointMarker:
        item = CARTExhaustionCheckpointMarker(
            study_id=study_id,
            marker_symbol=marker_symbol,
            surface_density_molecules=surface_density_molecules,
            epigenetic_chromatin_accessibility_score=epigenetic_chromatin_accessibility_score,
            reversibility_potential_pct=reversibility_potential_pct,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_study(self, study_id: UUID) -> Optional[CARTExhaustionStudy]:
        stmt = select(CARTExhaustionStudy).where(CARTExhaustionStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[CARTExhaustionStudy]:
        stmt = select(CARTExhaustionStudy).order_by(CARTExhaustionStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())