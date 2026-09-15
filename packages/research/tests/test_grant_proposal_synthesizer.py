"""Unit tests for Grant Proposal Synthesizer & Institutional Budget Calculator (Phase 35)."""

import pytest
from research.grants.synthesizer import GrantProposalSynthesizer, InstitutionalBudgetCalculator


def test_budget_calculator_multiyear_mtdc():
    calc = InstitutionalBudgetCalculator()
    budget = calc.calculate_multiyear_budget(
        duration_years=5,
        pi_base_salary=180000.0,
        pi_effort_months=2.0,
        postdoc_count=1,
        postdoc_base_salary=65000.0,
        grad_student_count=2,
        grad_student_stipend=38000.0,
        equipment_cost_y1=100000.0,
        cloud_compute_annual=40000.0,
        supplies_annual=20000.0,
        travel_annual=10000.0,
        fringe_rate_percent=28.5,
        indirect_rate_percent=52.0,
        annual_escalation_percent=3.0,
    )

    assert budget["duration_years"] == 5
    assert budget["total_requested_budget"] > 1500000.0
    assert budget["total_direct_costs"] > 0.0
    assert budget["total_indirect_costs"] > 0.0
    assert len(budget["yearly_breakdowns"]) == 5

    # Year 1 should have equipment, Year 2 should not
    assert budget["yearly_breakdowns"][0]["equipment"] == 100000.0
    assert budget["yearly_breakdowns"][1]["equipment"] == 0.0


def test_proposal_synthesizer_narratives_and_aims():
    synthesizer = GrantProposalSynthesizer()
    res = synthesizer.synthesize_proposal_narratives(
        title="Autonomous Materials Discovery Platform",
        research_topic="Room-temperature hydride superconductors",
        funding_agency="NIH",
        grant_mechanism="R01",
        key_findings=["Clathrate hydride structure stabilizes above 165 GPa."],
    )

    assert res["funding_agency"] == "NIH"
    assert "Room-temperature hydride superconductors" in res["executive_abstract"]
    assert len(res["specific_aims"]) == 3
    assert res["specific_aims"][0]["aim_number"] == 1
    assert "hypothesis" in res["specific_aims"][0]
    assert len(res["specific_aims"][0]["milestones"]) >= 2


def test_mock_study_section_scoring():
    synthesizer = GrantProposalSynthesizer()
    review = synthesizer.conduct_mock_study_section_review(
        proposal_title="Autonomous Materials Discovery",
        aims_count=3,
        total_budget=1500000.0,
    )

    assert review["overall_impact_score"] >= 1.0
    assert review["overall_impact_score"] <= 9.0
    assert review["percentile_estimate"] >= 1.0
    assert len(review["critique_strengths"]) > 0
    assert "summary_statement" in review


def test_latex_export():
    synthesizer = GrantProposalSynthesizer()
    proposal_data = {
        "title": "Quantum Agent Operating System",
        "funding_agency": "NSF",
        "executive_abstract": "Abstract content.",
        "significance_narrative": "Significance narrative.",
        "innovation_narrative": "Innovation narrative.",
        "approach_narrative": "Approach narrative.",
    }
    latex = synthesizer.export_proposal_latex(proposal_data, {"total_requested_budget": 2000000.0, "duration_years": 5, "indirect_rate_percent": 52.0})

    assert "\\documentclass" in latex
    assert "Quantum Agent Operating System" in latex
    assert "\\section{1. Specific Aims}" in latex
    assert "\\section{2. Significance}" in latex
