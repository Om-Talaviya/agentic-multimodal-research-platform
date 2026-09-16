"""
Repository for Antibody-Drug Conjugate (ADC) Design (Phase 59).
"""
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.adc_design import (
    DBADCDesignCampaign,
    DBADCPayloadLinkerConstruct,
)


class ADCDesignRepository:
    """Handles CRUD operations for ADC design campaigns and payload-linker constructs."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_campaign(
        self,
        antibody_name: str,
        target_antigen: str,
        conjugation_chemistry: str = "Maleimide-Cysteine",
        target_dar: float = 4.0,
        metadata_info: Optional[Dict[str, Any]] = None,
    ) -> DBADCDesignCampaign:
        camp = DBADCDesignCampaign(
            id=str(uuid.uuid4()),
            antibody_name=antibody_name,
            target_antigen=target_antigen,
            conjugation_chemistry=conjugation_chemistry,
            target_dar=target_dar,
            metadata_info=metadata_info or {},
        )
        self.session.add(camp)
        await self.session.flush()
        await self.session.commit()
        return camp

    async def add_constructs(
        self,
        campaign_id: str,
        constructs_data: List[Dict[str, Any]],
    ) -> List[DBADCPayloadLinkerConstruct]:
        created_constructs = []
        for c in constructs_data:
            construct = DBADCPayloadLinkerConstruct(
                id=str(uuid.uuid4()),
                campaign_id=campaign_id,
                construct_code=c.get("construct_code", "ADC-001"),
                payload_name=c["payload_name"],
                payload_class=c.get("payload_class", "Topoisomerase I Inhibitor"),
                linker_type=c.get("linker_type", "Val-Cit Cleavable"),
                measured_dar=c.get("measured_dar", 4.0),
                bystander_killing_score=c.get("bystander_killing_score", 0.85),
                plasma_half_life_hours=c.get("plasma_half_life_hours", 168.0),
                aggregation_propensity_pct=c.get("aggregation_propensity_pct", 1.5),
                therapeutic_index_score=c.get("therapeutic_index_score", 8.8),
                recommended_lead=c.get("recommended_lead", False),
            )
            self.session.add(construct)
            created_constructs.append(construct)

        await self.session.flush()

        camp = await self.get_campaign(campaign_id)
        if camp:
            camp.total_constructs_screened = len(created_constructs)
            self.session.add(camp)

        await self.session.commit()
        return created_constructs

    async def get_campaign(self, campaign_id: str) -> Optional[DBADCDesignCampaign]:
        self.session.expire_all()
        query = (
            select(DBADCDesignCampaign)
            .options(selectinload(DBADCDesignCampaign.constructs))
            .where(DBADCDesignCampaign.id == campaign_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_campaigns(self, limit: int = 50) -> List[DBADCDesignCampaign]:
        query = (
            select(DBADCDesignCampaign)
            .options(selectinload(DBADCDesignCampaign.constructs))
            .order_by(desc(DBADCDesignCampaign.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
