"""Tests for Phase 128 CITEseqRepository."""

import pytest
import uuid
from database.repositories.citeseq_repo import CITEseqRepository


@pytest.mark.asyncio
async def test_citeseq_repo_lifecycle(db_session):
    repo = CITEseqRepository(db_session)

    # 1. Create dataset
    dataset = await repo.create_dataset(
        sample_name="Melanoma_TIL_CITEseq_54P",
        tissue_origin="Melanoma Tumor Infiltrating Lymphocytes",
        total_cells_profiled=15400,
        adt_panel_size=54,
        rna_features_count=26000,
        dsb_background_ambient_mean=1.92,
        wNN_modality_weight_protein=0.62,
        wNN_modality_weight_rna=0.38,
        metadata_json={"sequencer": "NovaSeq 6000"},
    )
    assert dataset.id is not None
    assert dataset.sample_name == "Melanoma_TIL_CITEseq_54P"

    # 2. Add antibody derived tag
    tag = await repo.add_antibody_tag(
        dataset_id=dataset.id,
        tag_barcode="TotalSeq-C-CD8a-001",
        marker_name="CD8a",
        clone_id="RPA-T8",
        isotype_control="IgG1-k",
        signal_to_noise_ratio=18.4,
    )
    assert tag.id is not None
    assert tag.marker_name == "CD8a"

    # 3. Add cell surface protein expression
    exp = await repo.add_protein_expression(
        dataset_id=dataset.id,
        cell_cluster_id="Cytotoxic_CD8_T_Cells",
        marker_name="CD8a",
        dsb_normalized_expression=5.42,
        corresponding_rna_tpm=245.0,
        concordance_spearman_rho=0.84,
        discordance_pvalue=1e-8,
    )
    assert exp.id is not None
    assert exp.cell_cluster_id == "Cytotoxic_CD8_T_Cells"

    # 4. Get dataset
    fetched = await repo.get_dataset(dataset.id)
    assert fetched is not None
    assert len(fetched.antibodies) == 1
    assert len(fetched.expressions) == 1
    assert fetched.antibodies[0].marker_name == "CD8a"

    # 5. List datasets
    datasets = await repo.list_datasets(limit=10)
    assert len(datasets) >= 1
