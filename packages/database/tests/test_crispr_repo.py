"""Tests for CRISPRRepository."""

import pytest
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from database.connection import Base
from database.models.user import User as DBUser
from database.repositories.crispr_repo import CRISPRRepository


@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_create_and_get_crispr_design(async_session: AsyncSession):
    user_id = uuid.uuid4()
    user = DBUser(id=user_id, username="crispr_researcher", email="crispr@mit.edu", password_hash="hash")
    async_session.add(user)
    await async_session.commit()

    repo = CRISPRRepository(async_session)

    design = await repo.create_design(
        user_id=user_id,
        target_gene="PCSK9",
        genomic_locus="Chr1:55039447-55064852",
        organism="Homo sapiens",
        cas_enzyme="SpCas9",
        pam_motif="NGG",
        target_strand="both",
        editing_modality="knockout_cleavage",
        target_sequence_fasta="ATGGGCACCGTCAGCTCCAGGCGGTCCTGGTGGCCGCTGCCACTGCTGCTGCTG",
        design_summary_json={"exon": "Exon 1", "top_on_target_score": 88.4},
    )

    assert design.id is not None
    assert design.target_gene == "PCSK9"
    assert design.cas_enzyme == "SpCas9"

    # Add Guide RNA
    guides = await repo.add_guide_rnas(
        design_id=design.id,
        guides_data=[
            {
                "guide_name": "PCSK9_Exon1_g1",
                "spacer_sequence_20nt": "CACCGTCAGCTCCAGGCGGT",
                "pam_sequence": "CGG",
                "genomic_position": 7,
                "strand": "+",
                "cut_position_rel": 17,
                "on_target_efficiency_score": 88.4,
                "off_target_cfd_score": 94.2,
                "gc_content_pct": 65.0,
                "secondary_structure_delta_g": -2.4,
                "recommendation_tier": "optimal",
                "oligo_forward_top": "5'-CACCCACCGTCAGCTCCAGGCGGT-3'",
                "oligo_reverse_bottom": "5'-AAACACCGCCTGGAGCTGACGGTG-3'",
            }
        ],
    )

    assert len(guides) == 1
    guide = guides[0]
    assert guide.id is not None
    assert guide.recommendation_tier == "optimal"

    # Add Off Target Site
    off_targets = await repo.add_off_target_sites(
        guide_id=guide.id,
        off_targets_data=[
            {
                "chromosome": "Chr1",
                "genomic_coordinate": 55041200,
                "mismatched_sequence": "CACCGTCAGCTCCAGGCGAA",
                "mismatch_count": 2,
                "mismatch_positions_json": [18, 19],
                "cfd_cleavage_score": 0.034,
                "gene_annotation": "PCSK9_Homolog_Chr1",
                "is_exonic": False,
            }
        ],
    )
    assert len(off_targets) == 1

    # Add Base Editing Profile
    be_profiles = await repo.add_base_editing_profiles(
        guide_id=guide.id,
        profiles_data=[
            {
                "editing_type": "ABE8e (A->G)",
                "target_base": "A",
                "editing_window_start": 4,
                "editing_window_end": 8,
                "expected_product_sequence": "CACCATCAGCTCCAGGCGGT",
                "bystander_bases_count": 0,
                "purity_score_pct": 94.0,
                "activity_score_pct": 74.5,
            }
        ],
    )
    assert len(be_profiles) == 1

    # Retrieve full design
    loaded = await repo.get_design(design.id)
    assert loaded is not None
    assert len(loaded.guide_rnas) == 1
    assert len(loaded.guide_rnas[0].off_target_sites) == 1
    assert len(loaded.guide_rnas[0].base_editing_profiles) == 1

    # Get single guide
    single_g = await repo.get_guide(guide.id)
    assert single_g is not None
    assert single_g.spacer_sequence_20nt == "CACCGTCAGCTCCAGGCGGT"

    # List designs
    designs_list = await repo.list_designs(user_id=user_id)
    assert len(designs_list) == 1

    # Delete design
    deleted = await repo.delete_design(design.id)
    assert deleted is True
    assert await repo.get_design(design.id) is None
