"""Repository for Liquid Biopsy ctDNA Fragmentomics & MRD Detection."""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from database.models.liquid_biopsy_fragmentomics import (
    DBLiquidBiopsySample,
    DBFragmentSizeDistribution,
    DBEndMotifProfile,
)


class LiquidBiopsyRepository:
    """Handles async database operations for liquid biopsy fragmentomics."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_sample(
        self,
        patient_id: str,
        sample_barcode: str,
        cancer_type: str,
        sampling_timepoint: str,
        total_cfdna_ng_ml: float,
        tumor_fraction_pct: float,
        mrd_status: str,
        fragment_short_ratio: float,
        median_fragment_length_bp: int,
        sample_metadata_json: Optional[Dict[str, Any]] = None,
    ) -> DBLiquidBiopsySample:
        sample = DBLiquidBiopsySample(
            patient_id=patient_id,
            sample_barcode=sample_barcode,
            cancer_type=cancer_type,
            sampling_timepoint=sampling_timepoint,
            total_cfdna_ng_ml=total_cfdna_ng_ml,
            tumor_fraction_pct=tumor_fraction_pct,
            mrd_status=mrd_status,
            fragment_short_ratio=fragment_short_ratio,
            median_fragment_length_bp=median_fragment_length_bp,
            sample_metadata_json=sample_metadata_json or {},
        )
        self.session.add(sample)
        await self.session.commit()
        await self.session.refresh(sample)
        return sample

    async def get_sample(self, sample_id: str) -> Optional[DBLiquidBiopsySample]:
        stmt = select(DBLiquidBiopsySample).where(DBLiquidBiopsySample.id == sample_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_samples(self, limit: int = 50, offset: int = 0) -> List[DBLiquidBiopsySample]:
        stmt = select(DBLiquidBiopsySample).order_by(desc(DBLiquidBiopsySample.created_at)).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_size_distributions(
        self,
        sample_id: str,
        distributions_data: List[Dict[str, Any]],
    ) -> List[DBFragmentSizeDistribution]:
        created = []
        for d in distributions_data:
            item = DBFragmentSizeDistribution(
                sample_id=sample_id,
                bin_start_bp=d["bin_start_bp"],
                bin_end_bp=d["bin_end_bp"],
                fragment_count=d["fragment_count"],
                fragment_frequency_pct=d["fragment_frequency_pct"],
            )
            self.session.add(item)
            created.append(item)
        await self.session.commit()
        for item in created:
            await self.session.refresh(item)
        return created

    async def get_size_distributions_by_sample(self, sample_id: str) -> List[DBFragmentSizeDistribution]:
        stmt = select(DBFragmentSizeDistribution).where(DBFragmentSizeDistribution.sample_id == sample_id).order_by(DBFragmentSizeDistribution.bin_start_bp)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_end_motifs(
        self,
        sample_id: str,
        motifs_data: List[Dict[str, Any]],
    ) -> List[DBEndMotifProfile]:
        created = []
        for m in motifs_data:
            item = DBEndMotifProfile(
                sample_id=sample_id,
                motif_sequence_4mer=m["motif_sequence_4mer"],
                observed_frequency=m["observed_frequency"],
                reference_frequency=m.get("reference_frequency", 0.0625),
                motif_diversity_score=m.get("motif_diversity_score", 1.0),
            )
            self.session.add(item)
            created.append(item)
        await self.session.commit()
        for item in created:
            await self.session.refresh(item)
        return created

    async def get_end_motifs_by_sample(self, sample_id: str) -> List[DBEndMotifProfile]:
        stmt = select(DBEndMotifProfile).where(DBEndMotifProfile.sample_id == sample_id).order_by(desc(DBEndMotifProfile.observed_frequency))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
