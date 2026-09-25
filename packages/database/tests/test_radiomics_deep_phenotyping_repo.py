import pytest
from database.repositories.radiomics_deep_phenotyping_repo import RadiomicsDeepPhenotypingRepository

@pytest.mark.asyncio
async def test_radiomics_deep_phenotyping_repository(db_session):
    repo = RadiomicsDeepPhenotypingRepository(db_session)
    
    study = await repo.create_study(
        name="GBM_Cohort_Patient_992",
        scan_modality="Multiparametric MRI",
        tumor_type="Glioblastoma Multiforme",
        gross_tumor_volume_cm3=52.4,
        necrotic_core_fraction=0.25,
        active_rim_fraction=0.45,
        edema_infiltrative_fraction=0.30,
        intratumoral_heterogeneity_index=0.91,
        predicted_overall_survival_months=19.2,
        status="completed",
        summary_report="Extensive hypervascular enhancing rim.",
    )
    assert study.id is not None
    assert study.name == "GBM_Cohort_Patient_992"
    assert study.gross_tumor_volume_cm3 == 52.4

    subregion = await repo.add_habitat_subregion(
        study_id=study.id,
        subregion_name="Hypervascular Rim",
        volume_cm3=23.58,
        mean_perfusion_ktrans=0.42,
        apparent_diffusion_coefficient_adc=0.88,
        hypoxia_pet_avidity_suv=4.8,
    )
    assert subregion.id is not None
    assert subregion.subregion_name == "Hypervascular Rim"

    texture = await repo.add_texture_feature(
        study_id=study.id,
        feature_class="GLCM",
        feature_name="GLCM_Contrast",
        feature_value=14.82,
        ibsi_compliance_flag=True,
        radiogenomic_weight=1.2,
    )
    assert texture.id is not None
    assert texture.feature_name == "GLCM_Contrast"

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "GBM_Cohort_Patient_992"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
