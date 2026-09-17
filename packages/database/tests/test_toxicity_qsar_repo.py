import pytest
import pytest_asyncio
from database.models.toxicity_qsar import DBCompoundToxicityScreen
from database.repositories.toxicity_qsar_repo import ToxicityQSARRepository

@pytest.mark.asyncio
async def test_toxicity_qsar_repository(async_db_session):
    repo = ToxicityQSARRepository(async_db_session)

    # 1. Create screen
    screen = await repo.create_screen(
        compound_name="Imatinib-Test",
        smiles_string="Cc1ccc(cc1Nc2nccc(n2)c3cccnc3)NC(=O)c4ccc(cc4)CN5CCN(CC5)C",
        molecular_weight=493.6,
        log_p=3.2,
        ames_mutagenicity_status="NEGATIVE",
        herg_ic50_micromolar=24.5,
    )
    assert screen.id is not None
    assert screen.compound_name == "Imatinib-Test"

    # 2. Add structural alert
    alert = await repo.add_structural_alert(
        screen_id=screen.id,
        alert_name="Primary Aromatic Amine",
        smarts_pattern="c[NH2]",
        toxicophore_category="CYP Bioactivation",
        severity_level="MODERATE",
    )
    assert alert.id is not None
    assert alert.screen_id == screen.id

    # 3. Fetch hydrated screen
    fetched = await repo.get_screen_by_id(screen.id)
    assert fetched is not None
    assert len(fetched.structural_alerts) == 1
    assert fetched.structural_alerts[0].alert_name == "Primary Aromatic Amine"
