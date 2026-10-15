"""Tests for Phase 541: Autonomous Synthetic Protocellular Compartment FtsZ-Min System Dynamic Cleavage Constriction Modeler."""

import pytest
from research.orchestration.synthetic_cell_division_ftsz_constriction_engine import SyntheticCellDivisionFtszConstrictionEngine


def test_synthetic_cell_division_ftsz_constriction_engine():
    engine = SyntheticCellDivisionFtszConstrictionEngine()
    result = engine.analyze(
        target_specimen="Cell-Free Microfluidic Giant Unilamellar Vesicle with Reconstituted FtsZ-FtsA and MinCDE Oscillatory Machinery",
        analytical_modality="protocell-ftsz-cleavage-constriction",
        input_scale=1.0,
    )

    assert result.target_specimen == "Cell-Free Microfluidic Giant Unilamellar Vesicle with Reconstituted FtsZ-FtsA and MinCDE Oscillatory Machinery"
    assert result.confidence_score >= 0.95
    assert result.equatorial_constriction_pinching_force_pN != 0.0
    assert result.min_protein_pole_to_pole_oscillation_period_s != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Synthetic Protocell" in result.summary_report
