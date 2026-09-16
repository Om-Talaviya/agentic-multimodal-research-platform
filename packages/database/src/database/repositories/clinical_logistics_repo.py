"""
Repository for Global Multi-Site Clinical Trial Logistics (Phase 63).
"""
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.clinical_logistics import (
    DBClinicalTrialNetwork,
    DBClinicalSiteNode,
    DBLogisticsSupplyRoute,
)


class ClinicalTrialLogisticsRepository:
    """Handles CRUD operations for clinical trial logistics networks, hospital sites, and supply routes."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_network(
        self,
        trial_protocol_number: str,
        trial_title: str,
        phase: str = "Phase III",
        product_storage_regime: str = "Ultra-Cold Chain (-80°C)",
        metadata_info: Optional[Dict[str, Any]] = None,
    ) -> DBClinicalTrialNetwork:
        net = DBClinicalTrialNetwork(
            id=str(uuid.uuid4()),
            trial_protocol_number=trial_protocol_number,
            trial_title=trial_title,
            phase=phase,
            product_storage_regime=product_storage_regime,
            metadata_info=metadata_info or {},
        )
        self.session.add(net)
        await self.session.flush()
        await self.session.commit()
        return net

    async def add_sites_and_routes(
        self,
        network_id: str,
        sites_data: List[Dict[str, Any]],
        routes_data: List[Dict[str, Any]],
        global_risk: float = 0.22,
    ) -> DBClinicalTrialNetwork:
        for s in sites_data:
            site = DBClinicalSiteNode(
                id=str(uuid.uuid4()),
                network_id=network_id,
                site_name=s["site_name"],
                country_code=s.get("country_code", "US"),
                active_enrolled_patients=s.get("active_enrolled_patients", 15),
                current_inventory_vials=s.get("current_inventory_vials", 60),
                inventory_runway_days=s.get("inventory_runway_days", 45.0),
                cold_chain_compliance_pct=s.get("cold_chain_compliance_pct", 99.0),
                stockout_risk_score=s.get("stockout_risk_score", 0.15),
            )
            self.session.add(site)

        for r in routes_data:
            route = DBLogisticsSupplyRoute(
                id=str(uuid.uuid4()),
                network_id=network_id,
                origin_depot=r["origin_depot"],
                destination_site=r["destination_site"],
                transport_mode=r.get("transport_mode", "Cryo-Courier Air Express"),
                transit_time_hours=r.get("transit_time_hours", 18.0),
                temperature_excursion_risk_pct=r.get("temperature_excursion_risk_pct", 2.0),
                customs_clearance_delay_risk_pct=r.get("customs_clearance_delay_risk_pct", 3.0),
                contingency_action=r.get("contingency_action", "Secondary depot dispatch"),
            )
            self.session.add(route)

        await self.session.flush()

        net = await self.get_network(network_id)
        if net:
            net.total_sites = len(sites_data)
            net.global_supply_risk_index = global_risk
            self.session.add(net)

        await self.session.commit()
        return net

    async def get_network(self, network_id: str) -> Optional[DBClinicalTrialNetwork]:
        self.session.expire_all()
        query = (
            select(DBClinicalTrialNetwork)
            .options(
                selectinload(DBClinicalTrialNetwork.sites),
                selectinload(DBClinicalTrialNetwork.routes),
            )
            .where(DBClinicalTrialNetwork.id == network_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_networks(self, limit: int = 50) -> List[DBClinicalTrialNetwork]:
        query = (
            select(DBClinicalTrialNetwork)
            .options(selectinload(DBClinicalTrialNetwork.sites))
            .order_by(desc(DBClinicalTrialNetwork.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
