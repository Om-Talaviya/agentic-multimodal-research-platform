"""Tests for RadiogenomicsRepository."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories.radiogenomics_repo import RadiogenomicsRepository


@pytest.mark.asyncio
async def test_radiogenomics_repo_lifecycle(db_session: AsyncSession):
    repo = RadiogenomicsRepository(db_session)

    # 1. Create Scan
    scan = await repo.create_scan(
        patient_id="TCGA-GBM-0142",
        modality="MRI_T1_CONTRAST",
        anatomical_region="BRAIN_GLIOMA",
        lesion_volume_cm3=32.4,
    )
    assert scan.id is not None
    assert scan.patient_id == "TCGA-GBM-0142"

    # 2. Add Feature
    feat = await repo.add_radiomic_feature(
        scan_id=scan.id,
        feature_family="IBSI_SHAPE_3D",
        feature_name="Sphericity",
        feature_value=0.812,
        normalized_z_score=1.15,
    )
    assert feat.id is not None
    assert feat.feature_name == "Sphericity"

    # 3. Add Genomic Correlation
    corr = await repo.add_genomic_correlation(
        scan_id=scan.id,
        predicted_genomic_alteration="IDH1_R132H",
        prediction_probability=0.92,
        clinical_significance="Favorable prognosis",
    )
    assert corr.id is not None
    assert corr.predicted_genomic_alteration == "IDH1_R132H"

    # 4. Fetch Scan
    fetched = await repo.get_scan(scan.id)
    assert fetched is not None
    assert len(fetched.radiomic_features) == 1
    assert len(fetched.genomic_correlations) == 1

    # 5. List Scans
    scans = await repo.list_scans()
    assert len(scans) >= 1
