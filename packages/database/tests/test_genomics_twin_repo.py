"""Tests for ClinicalGenomicsTwinRepository."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories.clinical_genomics_twin_repo import ClinicalGenomicsTwinRepository


@pytest.mark.asyncio
async def test_genomics_twin_repo_lifecycle(db_session: AsyncSession):
    repo = ClinicalGenomicsTwinRepository(db_session)

    # 1. Create Profile
    profile = await repo.create_profile(
        patient_mrn="MRN-90210-GEN",
        age=62,
        sex="MALE",
        ancestry="EAST_ASIAN",
        total_star_alleles_called=4,
        high_risk_drug_interactions_count=1,
    )
    assert profile.id is not None
    assert profile.patient_mrn == "MRN-90210-GEN"

    # 2. Add Guideline
    guideline = await repo.add_guideline(
        profile_id=profile.id,
        gene_symbol="CYP2C19",
        diplotype_call="*2/*2",
        metabolizer_phenotype="POOR_METABOLIZER",
        affected_drug_class="ANTIPLATELET",
        cpic_level="LEVEL_A",
        clinical_dose_recommendation="Avoid Clopidogrel",
    )
    assert guideline.id is not None
    assert guideline.gene_symbol == "CYP2C19"

    # 3. Add Twin Simulation
    sim = await repo.add_twin_simulation(
        profile_id=profile.id,
        drug_administered="Clopidogrel",
        prescribed_dose_mg=75.0,
        predicted_auc_ratio=0.25,
        toxic_accumulation_risk="HIGH",
        recommended_adjusted_dose_mg=0.0,
        alternate_drug_suggestion="Prasugrel",
        efficacy_score=0.45,
    )
    assert sim.id is not None
    assert sim.alternate_drug_suggestion == "Prasugrel"

    # 4. Fetch Profile
    fetched = await repo.get_profile(profile.id)
    assert fetched is not None
    assert len(fetched.guidelines) == 1
    assert len(fetched.twin_simulations) == 1

    # 5. List Profiles
    profiles = await repo.list_profiles()
    assert len(profiles) >= 1
