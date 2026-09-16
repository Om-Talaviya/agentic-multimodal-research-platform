"""
Repository for Autonomous Computational Immunology & TCR-pMHC Neoantigen Binding Predictor (Phase 55).
"""
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.immunology import (
    DBNeoantigenScreen,
    DBNeoantigenEpitope,
    DBVaccineConstructDesign,
)


class ImmunologyRepository:
    """Handles CRUD operations for neoantigen screening and vaccine construct designs."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_screen(
        self,
        patient_id: str,
        tumor_type: str,
        hla_alleles: List[str],
        mutation_count: int = 0,
        metadata_info: Optional[Dict[str, Any]] = None,
    ) -> DBNeoantigenScreen:
        screen = DBNeoantigenScreen(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            tumor_type=tumor_type,
            hla_alleles=hla_alleles,
            mutation_count=mutation_count,
            metadata_info=metadata_info or {},
        )
        self.session.add(screen)
        await self.session.flush()
        await self.session.commit()
        return screen

    async def add_epitopes(
        self,
        screen_id: str,
        epitopes_data: List[Dict[str, Any]],
    ) -> List[DBNeoantigenEpitope]:
        created_epitopes = []
        for ep in epitopes_data:
            epitope = DBNeoantigenEpitope(
                id=str(uuid.uuid4()),
                screen_id=screen_id,
                gene_symbol=ep.get("gene_symbol", "UNKNOWN"),
                mutation_variant=ep.get("mutation_variant", "MUT"),
                peptide_sequence=ep["peptide_sequence"],
                wildtype_sequence=ep.get("wildtype_sequence"),
                hla_allele=ep["hla_allele"],
                binding_ic50_nm=ep.get("binding_ic50_nm", 50.0),
                percentile_rank=ep.get("percentile_rank", 0.5),
                tcr_immunogenicity_score=ep.get("tcr_immunogenicity_score", 0.8),
                proteasomal_cleavage_score=ep.get("proteasomal_cleavage_score", 0.85),
                tap_transport_efficiency=ep.get("tap_transport_efficiency", 0.90),
                composite_priority_score=ep.get("composite_priority_score", 0.9),
                recommended_for_vaccine=ep.get("recommended_for_vaccine", False),
            )
            self.session.add(epitope)
            created_epitopes.append(epitope)

        await self.session.flush()

        # Update screen candidate count
        screen = await self.get_screen(screen_id)
        if screen:
            top_rec = sum(1 for e in created_epitopes if e.recommended_for_vaccine)
            screen.top_candidates_count = top_rec
            self.session.add(screen)

        await self.session.commit()
        return created_epitopes

    async def create_vaccine_construct(
        self,
        screen_id: str,
        construct_name: str,
        construct_type: str,
        ordered_epitopes: List[str],
        linker_sequences: List[str],
        full_polyepitope_sequence: str,
        junctional_immunogenicity_risk: float = 0.05,
        predicted_expression_efficiency: float = 0.92,
    ) -> DBVaccineConstructDesign:
        construct = DBVaccineConstructDesign(
            id=str(uuid.uuid4()),
            screen_id=screen_id,
            construct_name=construct_name,
            construct_type=construct_type,
            ordered_epitopes=ordered_epitopes,
            linker_sequences=linker_sequences,
            full_polyepitope_sequence=full_polyepitope_sequence,
            junctional_immunogenicity_risk=junctional_immunogenicity_risk,
            predicted_expression_efficiency=predicted_expression_efficiency,
        )
        self.session.add(construct)
        await self.session.flush()
        await self.session.commit()
        return construct

    async def get_screen(self, screen_id: str) -> Optional[DBNeoantigenScreen]:
        self.session.expire_all()
        query = (
            select(DBNeoantigenScreen)
            .options(
                selectinload(DBNeoantigenScreen.epitopes),
                selectinload(DBNeoantigenScreen.vaccine_constructs),
            )
            .where(DBNeoantigenScreen.id == screen_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_screens(self, limit: int = 50) -> List[DBNeoantigenScreen]:
        query = (
            select(DBNeoantigenScreen)
            .options(selectinload(DBNeoantigenScreen.epitopes))
            .order_by(desc(DBNeoantigenScreen.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_top_epitopes(self, screen_id: str, limit: int = 20) -> List[DBNeoantigenEpitope]:
        query = (
            select(DBNeoantigenEpitope)
            .where(DBNeoantigenEpitope.screen_id == screen_id)
            .order_by(desc(DBNeoantigenEpitope.composite_priority_score))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
