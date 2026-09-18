"""Tests for LongReadGenomicsRepository."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories.long_read_genomics_repo import LongReadGenomicsRepository


@pytest.mark.asyncio
async def test_long_read_repo_lifecycle(db_session: AsyncSession):
    repo = LongReadGenomicsRepository(db_session)

    # 1. Create run
    run = await repo.create_run(
        sample_name="NA12878_PacBio_HiFi_Benchmark",
        platform="PACBIO_HIFI",
        flowcell_type="Sequel_IIe",
        mean_read_length_bp=19400.0,
        total_gigabases=55.0,
        n50_length_bp=22100,
        mean_phred_quality=33.2,
    )
    assert run.id is not None
    assert run.sample_name == "NA12878_PacBio_HiFi_Benchmark"
    assert run.n50_length_bp == 22100

    # 2. Add structural variant
    sv = await repo.add_structural_variant(
        run_id=run.id,
        chromosome="chr1",
        start_pos=100000,
        end_pos=105000,
        sv_type="DELETION",
        sv_length_bp=5000,
        genotype="0/1",
        support_reads=32,
        filter_status="PASS",
    )
    assert sv.id is not None
    assert sv.sv_type == "DELETION"

    # 3. Add telomeric repeat profile
    tel = await repo.add_telomere_profile(
        run_id=run.id,
        chromosome_arm="chr1p",
        hexamer_motif="TTAGGG",
        repeat_count=1500,
        telomere_length_kbp=9.0,
        erosion_hazard_level="LOW",
    )
    assert tel.id is not None
    assert tel.telomere_length_kbp == 9.0

    # 4. Fetch run
    fetched = await repo.get_run(run.id)
    assert fetched is not None
    assert len(fetched.structural_variants) == 1
    assert len(fetched.telomeric_profiles) == 1

    # 5. List runs
    runs = await repo.list_runs()
    assert len(runs) >= 1
