"""Repository for siRNA Duplex Thermodynamics & Off-Target Suppressor."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.connection import AsyncSession
from database.models.sirna_thermodynamics import (
    DBsiRNAThermodynamicsStudy,
    DBsiRNADuplexConstruct,
    DBOffTargetSeedMatch,
)


class SiRNAThermodynamicsRepository:
    """Repository handling CRUD operations for siRNA Thermodynamics."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        study_name: str,
        target_mrna_transcript: str = "NM_000546.6 (TP53)",
        target_gene: str = "TP53",
        candidates_screened: int = 4,
        best_candidate_guide_strand: str = "UACAGUCAGUACUACAGUAAU",
        mean_on_target_efficiency: float = 88.5,
        summary_metrics: Optional[Dict[str, Any]] = None,
        duplexes: Optional[List[Dict[str, Any]]] = None,
        off_targets: Optional[List[Dict[str, Any]]] = None,
    ) -> DBsiRNAThermodynamicsStudy:
        study_id = uuid.uuid4()
        study = DBsiRNAThermodynamicsStudy(
            id=study_id,
            study_name=study_name,
            target_mrna_transcript=target_mrna_transcript,
            target_gene=target_gene,
            candidates_screened=candidates_screened,
            best_candidate_guide_strand=best_candidate_guide_strand,
            mean_on_target_efficiency=mean_on_target_efficiency,
            summary_metrics=summary_metrics or {},
        )
        self.session.add(study)
        await self.session.flush()

        if duplexes:
            for d in duplexes:
                construct = DBsiRNADuplexConstruct(
                    id=uuid.uuid4(),
                    study_id=study_id,
                    guide_strand_sequence=d["guide_strand_sequence"],
                    passenger_strand_sequence=d["passenger_strand_sequence"],
                    delta_g_5p_kcal_mol=d["delta_g_5p_kcal_mol"],
                    delta_g_3p_kcal_mol=d["delta_g_3p_kcal_mol"],
                    delta_delta_g_asymmetry=d["delta_delta_g_asymmetry"],
                    seed_region_tm_celsius=d["seed_region_tm_celsius"],
                    risc_loading_preference=d.get("risc_loading_preference", "guide_dominant"),
                    predicted_knockdown_efficiency=d["predicted_knockdown_efficiency"],
                    chemical_mod_pattern=d.get("chemical_mod_pattern", "2OMe_2F_phosphorothioate"),
                )
                self.session.add(construct)

        if off_targets:
            for ot in off_targets:
                match = DBOffTargetSeedMatch(
                    id=uuid.uuid4(),
                    study_id=study_id,
                    off_target_gene=ot["off_target_gene"],
                    utr3_seed_match_type=ot.get("utr3_seed_match_type", "7mer-m8"),
                    seed_binding_free_energy=ot["seed_binding_free_energy"],
                    off_target_silencing_risk=ot.get("off_target_silencing_risk", "low"),
                )
                self.session.add(match)

        await self.session.commit()
        return await self.get_study(study_id)  # type: ignore

    async def get_study(self, study_id: uuid.UUID) -> Optional[DBsiRNAThermodynamicsStudy]:
        stmt = (
            select(DBsiRNAThermodynamicsStudy)
            .where(DBsiRNAThermodynamicsStudy.id == study_id)
            .options(
                selectinload(DBsiRNAThermodynamicsStudy.duplexes),
                selectinload(DBsiRNAThermodynamicsStudy.off_targets),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DBsiRNAThermodynamicsStudy]:
        stmt = (
            select(DBsiRNAThermodynamicsStudy)
            .order_by(DBsiRNAThermodynamicsStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
            .options(
                selectinload(DBsiRNAThermodynamicsStudy.duplexes),
                selectinload(DBsiRNAThermodynamicsStudy.off_targets),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def delete_study(self, study_id: uuid.UUID) -> bool:
        study = await self.get_study(study_id)
        if not study:
            return False
        await self.session.delete(study)
        await self.session.commit()
        return True
