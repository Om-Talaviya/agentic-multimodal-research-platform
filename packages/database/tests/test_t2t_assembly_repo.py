"""Tests for Phase 126 T2TAssemblyRepository."""

import pytest
import uuid
from database.repositories.t2t_assembly_repo import T2TAssemblyRepository


@pytest.mark.asyncio
async def test_t2t_assembly_repo_lifecycle(db_session):
    repo = T2TAssemblyRepository(db_session)

    # 1. Create assembly
    assembly = await repo.create_assembly(
        sample_name="CHM13_T2T_v2_Haploid",
        sequencing_technology="PacBio-HiFi+ONT-UltraLong",
        total_contig_length_bp=3117275501,
        n50_length_kbp=154200.0,
        qv_consensus_accuracy=73.5,
        kmer_completeness_pct=99.99,
        telomere_telomere_closed_chromosomes=24,
        metadata_json={"lineage": "Complete Hydatidiform Mole"},
    )
    assert assembly.id is not None
    assert assembly.sample_name == "CHM13_T2T_v2_Haploid"

    # 2. Add structural variant
    sv = await repo.add_structural_variant(
        assembly_id=assembly.id,
        variant_id="SV_DEL_CHR1_0042",
        chromosome="chr1",
        start_position=145200000,
        end_position=145245000,
        sv_type="DELETION",
        sv_length_bp=45000,
        genotype_quality=99.9,
        supporting_reads_count=52,
        flanking_repeat_motif="AluYb8",
        functional_impact_score=0.88,
    )
    assert sv.id is not None
    assert sv.sv_type == "DELETION"

    # 3. Add phased haplotype block
    block = await repo.add_haplotype_block(
        assembly_id=assembly.id,
        chromosome="chr1",
        block_start_bp=1,
        block_end_bp=248956422,
        phase_switch_error_rate=0.0008,
        maternal_markers_count=18500,
        paternal_markers_count=18200,
    )
    assert block.id is not None
    assert block.chromosome == "chr1"

    # 4. Get assembly
    fetched = await repo.get_assembly(assembly.id)
    assert fetched is not None
    assert len(fetched.variants) == 1
    assert len(fetched.haplotypes) == 1
    assert fetched.variants[0].variant_id == "SV_DEL_CHR1_0042"

    # 5. List assemblies
    assemblies = await repo.list_assemblies(limit=10)
    assert len(assemblies) >= 1
