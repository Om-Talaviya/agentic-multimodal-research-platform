"""Repository for Proteogenomics & Spectral Library data access (Phase 95)."""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.models.proteogenomics import (
    DBProteogenomicExperiment,
    DBPeptideSpectrumMatch,
    DBNovelSpliceJunction,
)


class ProteogenomicsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_experiment(
        self,
        workspace_id: uuid.UUID,
        sample_id: str,
        organism: str = "Homo sapiens",
        instrument_type: str = "Orbitrap Exploris 480",
        search_database: str = "UniProtKB + Ribo-Seq Novel ORFs",
        fdr_threshold: float = 0.01,
        total_spectra_analyzed: int = 50000,
        identified_peptides_count: int = 12400,
        novel_noncanonical_orfs_count: int = 38,
        analysis_metadata: Optional[Dict[str, Any]] = None,
    ) -> DBProteogenomicExperiment:
        exp = DBProteogenomicExperiment(
            workspace_id=workspace_id,
            sample_id=sample_id,
            organism=organism,
            instrument_type=instrument_type,
            search_database=search_database,
            fdr_threshold=fdr_threshold,
            total_spectra_analyzed=total_spectra_analyzed,
            identified_peptides_count=identified_peptides_count,
            novel_noncanonical_orfs_count=novel_noncanonical_orfs_count,
            analysis_metadata=analysis_metadata or {},
        )
        self.session.add(exp)
        await self.session.commit()
        await self.session.refresh(exp)
        return exp

    async def add_psm_match(
        self,
        experiment_id: uuid.UUID,
        scan_number: int,
        peptide_sequence: str,
        protein_accession: str,
        charge_state: int,
        precursor_mz: float,
        calculated_mz: float,
        hyperscore: float = 45.2,
        posterior_error_prob: float = 0.002,
        is_novel_variant: str = "CANONICAL",
    ) -> DBPeptideSpectrumMatch:
        psm = DBPeptideSpectrumMatch(
            experiment_id=experiment_id,
            scan_number=scan_number,
            peptide_sequence=peptide_sequence,
            protein_accession=protein_accession,
            charge_state=charge_state,
            precursor_mz=precursor_mz,
            calculated_mz=calculated_mz,
            hyperscore=hyperscore,
            posterior_error_prob=posterior_error_prob,
            is_novel_variant=is_novel_variant,
        )
        self.session.add(psm)
        await self.session.commit()
        await self.session.refresh(psm)
        return psm

    async def add_novel_junction(
        self,
        experiment_id: uuid.UUID,
        chromosome: str,
        junction_start: int,
        junction_end: int,
        supporting_reads_count: int = 14,
        peptide_evidence: str = "",
        frameshift_flag: str = "IN_FRAME",
    ) -> DBNovelSpliceJunction:
        junction = DBNovelSpliceJunction(
            experiment_id=experiment_id,
            chromosome=chromosome,
            junction_start=junction_start,
            junction_end=junction_end,
            supporting_reads_count=supporting_reads_count,
            peptide_evidence=peptide_evidence,
            frameshift_flag=frameshift_flag,
        )
        self.session.add(junction)
        await self.session.commit()
        await self.session.refresh(junction)
        return junction

    async def get_experiment(self, experiment_id: uuid.UUID) -> Optional[DBProteogenomicExperiment]:
        stmt = (
            select(DBProteogenomicExperiment)
            .options(
                selectinload(DBProteogenomicExperiment.psm_matches),
                selectinload(DBProteogenomicExperiment.novel_junctions),
            )
            .where(DBProteogenomicExperiment.id == experiment_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
