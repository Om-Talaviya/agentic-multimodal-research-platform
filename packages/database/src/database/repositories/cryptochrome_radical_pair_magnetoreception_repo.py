"""Repository for Phase 493: Autonomous Quantum Coherent Magnetoreception Cryptochrome Radical Pair Dynamics Simulator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cryptochrome_radical_pair_magnetoreception import (
    CryptochromeRadicalPairMagnetoreceptionStudy,
    CryptochromeRadicalPairMagnetoreceptionItemProfile,
    CryptochromeRadicalPairMagnetoreceptionMetricTrace,
)


class CryptochromeRadicalPairMagnetoreceptionRepository:
    """Database operations for Autonomous Quantum Coherent Magnetoreception Cryptochrome Radical Pair Dynamics Simulator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Purified Migratory Avian Cryptochrome-4 (ErCry4) Flavin-Tryptophan Photoreduced Radical Pair",
        analytical_modality: str = "quantum-radical-pair-magnetoreception",
        singlet_triplet_yield_anisotropy_ratio: float = 1.48,
        radical_pair_quantum_coherence_time_us: float = 4.85,
        geomagnetic_field_inclination_sensitivity_nT: float = 25.0,
        spin_state_entanglement_fidelity: float = 0.982,
        confidence_score: float = 0.993,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CryptochromeRadicalPairMagnetoreceptionStudy:
        study = CryptochromeRadicalPairMagnetoreceptionStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            singlet_triplet_yield_anisotropy_ratio=singlet_triplet_yield_anisotropy_ratio,
            radical_pair_quantum_coherence_time_us=radical_pair_quantum_coherence_time_us,
            geomagnetic_field_inclination_sensitivity_nT=geomagnetic_field_inclination_sensitivity_nT,
            spin_state_entanglement_fidelity=spin_state_entanglement_fidelity,
            confidence_score=confidence_score,
            status=status,
            parameters=parameters or {},
            summary_report=summary_report,
        )
        self.session.add(study)
        await self.session.flush()
        await self.session.refresh(study)
        return study

    async def add_item_profile(
        self,
        study_id: UUID,
        item_name: str,
        profile_category: str = "Analysis Profile",
        quantitative_value: float = 1.0,
        log2_fold_change: float = 1.5,
        significance_score: float = 0.95,
    ) -> CryptochromeRadicalPairMagnetoreceptionItemProfile:
        item = CryptochromeRadicalPairMagnetoreceptionItemProfile(
            study_id=study_id,
            item_name=item_name,
            profile_category=profile_category,
            quantitative_value=quantitative_value,
            log2_fold_change=log2_fold_change,
            significance_score=significance_score,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def add_metric_trace(
        self,
        study_id: UUID,
        metric_dimension: str,
        observed_value: float,
        z_score: float = 0.0,
        p_value: float = 0.05,
    ) -> CryptochromeRadicalPairMagnetoreceptionMetricTrace:
        trace = CryptochromeRadicalPairMagnetoreceptionMetricTrace(
            study_id=study_id,
            metric_dimension=metric_dimension,
            observed_value=observed_value,
            z_score=z_score,
            p_value=p_value,
        )
        self.session.add(trace)
        await self.session.flush()
        await self.session.refresh(trace)
        return trace

    async def get_study(self, study_id: UUID) -> Optional[CryptochromeRadicalPairMagnetoreceptionStudy]:
        result = await self.session.execute(
            select(CryptochromeRadicalPairMagnetoreceptionStudy)
            .options(
                selectinload(CryptochromeRadicalPairMagnetoreceptionStudy.item_profiles),
                selectinload(CryptochromeRadicalPairMagnetoreceptionStudy.metric_traces),
            )
            .where(CryptochromeRadicalPairMagnetoreceptionStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[CryptochromeRadicalPairMagnetoreceptionStudy]:
        result = await self.session.execute(
            select(CryptochromeRadicalPairMagnetoreceptionStudy)
            .options(
                selectinload(CryptochromeRadicalPairMagnetoreceptionStudy.item_profiles),
                selectinload(CryptochromeRadicalPairMagnetoreceptionStudy.metric_traces),
            )
            .order_by(CryptochromeRadicalPairMagnetoreceptionStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
