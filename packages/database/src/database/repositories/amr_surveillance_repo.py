"""Repository for Metagenomic Pathogen Surveillance & AMR."""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from database.models.amr_surveillance import (
    DBMetagenomicSample,
    DBPathogenAbundance,
    DBAntimicrobialResistanceGene,
)


class AMRSurveillanceRepository:
    """Handles async database operations for metagenomic pathogen surveillance and AMR resistome."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_sample(
        self,
        sample_name: str,
        sample_type: str = "WASTEWATER",
        collection_location: str = "Municipal Facility A",
        total_reads_sequenced: int = 5000000,
        pathogen_count: int = 4,
        amr_genes_count: int = 6,
        outbreak_risk_level: str = "LOW",
        sample_metadata_json: Optional[Dict[str, Any]] = None,
    ) -> DBMetagenomicSample:
        sample = DBMetagenomicSample(
            sample_name=sample_name,
            sample_type=sample_type,
            collection_location=collection_location,
            total_reads_sequenced=total_reads_sequenced,
            pathogen_count=pathogen_count,
            amr_genes_count=amr_genes_count,
            outbreak_risk_level=outbreak_risk_level,
            sample_metadata_json=sample_metadata_json or {},
        )
        self.session.add(sample)
        await self.session.commit()
        await self.session.refresh(sample)
        return sample

    async def get_sample(self, sample_id: str) -> Optional[DBMetagenomicSample]:
        stmt = select(DBMetagenomicSample).where(DBMetagenomicSample.id == sample_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_samples(self, limit: int = 50, offset: int = 0) -> List[DBMetagenomicSample]:
        stmt = select(DBMetagenomicSample).order_by(desc(DBMetagenomicSample.created_at)).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_pathogens(
        self,
        sample_id: str,
        pathogens_data: List[Dict[str, Any]],
    ) -> List[DBPathogenAbundance]:
        created = []
        for p in pathogens_data:
            item = DBPathogenAbundance(
                sample_id=sample_id,
                taxon_name=p["taxon_name"],
                ncbi_taxid=p.get("ncbi_taxid", 0),
                relative_abundance_pct=p.get("relative_abundance_pct", 1.0),
                read_depth=p.get("read_depth", 1000),
                pathogenicity_grade=p.get("pathogenicity_grade", "OPPORTUNISTIC"),
                is_priority_pathogen=p.get("is_priority_pathogen", False),
            )
            self.session.add(item)
            created.append(item)
        await self.session.commit()
        for item in created:
            await self.session.refresh(item)
        return created

    async def get_pathogens_by_sample(self, sample_id: str) -> List[DBPathogenAbundance]:
        stmt = select(DBPathogenAbundance).where(DBPathogenAbundance.sample_id == sample_id).order_by(desc(DBPathogenAbundance.relative_abundance_pct))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_amr_genes(
        self,
        sample_id: str,
        amr_data: List[Dict[str, Any]],
    ) -> List[DBAntimicrobialResistanceGene]:
        created = []
        for a in amr_data:
            item = DBAntimicrobialResistanceGene(
                sample_id=sample_id,
                gene_symbol=a["gene_symbol"],
                resistance_mechanism=a.get("resistance_mechanism", "BETA_LACTAMASE"),
                drug_class=a.get("drug_class", "CARBAPENEMS"),
                identity_pct=a.get("identity_pct", 99.0),
                coverage_pct=a.get("coverage_pct", 100.0),
                plasmid_mediated=a.get("plasmid_mediated", True),
            )
            self.session.add(item)
            created.append(item)
        await self.session.commit()
        for item in created:
            await self.session.refresh(item)
        return created

    async def get_amr_genes_by_sample(self, sample_id: str) -> List[DBAntimicrobialResistanceGene]:
        stmt = select(DBAntimicrobialResistanceGene).where(DBAntimicrobialResistanceGene.sample_id == sample_id).order_by(desc(DBAntimicrobialResistanceGene.identity_pct))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
