import pytest
import pytest_asyncio
from database.models.synthetic_lethality import DBSyntheticLethalScreen
from database.repositories.synthetic_lethality_repo import SyntheticLethalityRepository

@pytest.mark.asyncio
async def test_synthetic_lethality_repository(async_db_session):
    repo = SyntheticLethalityRepository(async_db_session)

    # 1. Create screen
    screen = await repo.create_screen(
        screen_name="BRCA1 Synthetic Lethal Discovery",
        primary_target_gene="BRCA1",
        tumor_indication="Ovarian Carcinoma",
        ceres_dependency_threshold=-0.5,
    )
    assert screen.id is not None
    assert screen.primary_target_gene == "BRCA1"

    # 2. Add partner
    partner = await repo.add_synthetic_lethal_partner(
        screen_id=screen.id,
        partner_gene="PARP1",
        interaction_type="DNA Repair Compensation",
        ceres_depmap_delta_score=-0.88,
        synthetic_lethal_p_value=1.4e-12,
        is_validated_druggable=True,
        confidence_tier="HIGH",
    )
    assert partner.id is not None
    assert partner.screen_id == screen.id

    # 3. Add dependency score
    score = await repo.add_dependency_score(
        screen_id=screen.id,
        cell_line_name="MDA-MB-436",
        lineage="Breast",
        primary_gene_dependency_score=-0.92,
        partner_gene_dependency_score=-0.88,
        co_essentiality_correlation=0.74,
    )
    assert score.id is not None

    # 4. Fetch hydrated screen
    fetched = await repo.get_screen_by_id(screen.id)
    assert fetched is not None
    assert len(fetched.partners) == 1
    assert len(fetched.dependency_scores) == 1
    assert fetched.partners[0].partner_gene == "PARP1"
