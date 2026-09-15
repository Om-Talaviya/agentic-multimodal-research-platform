"""Unit tests for statistical Meta-Analysis, PRISMA flow tracking, and effect size calculation."""

import pytest
from research.literature.meta_analysis import (
    EffectSizeCalculator,
    HeterogeneityEngine,
    PooledEffectEstimator,
    PRISMAFlowTracker,
    RiskOfBiasEvaluator,
    SLROrchestrator,
)


def test_cohens_d_and_hedges_g_calculation():
    """Verify Cohen's d and Hedges' g small-sample correction."""
    # Mean1 = 85.0, Mean2 = 75.0, SD1 = 10.0, SD2 = 10.0, N1 = 30, N2 = 30
    d_res = EffectSizeCalculator.compute_cohens_d(
        mean1=85.0,
        mean2=75.0,
        sd1=10.0,
        sd2=10.0,
        n1=30,
        n2=30,
    )
    assert d_res["effect_size"] == 1.0  # (85 - 75) / 10 = 1.0
    assert d_res["variance"] > 0
    assert d_res["ci_lower"] < d_res["effect_size"] < d_res["ci_upper"]

    # Test Hedges' g
    g_res = EffectSizeCalculator.compute_hedges_g(
        d=d_res["effect_size"],
        n1=30,
        n2=30,
        variance_d=d_res["variance"],
    )
    # J factor < 1.0 for finite samples, so g < d
    assert g_res["effect_size"] < d_res["effect_size"]
    assert g_res["correction_factor"] < 1.0


def test_odds_ratio_calculation():
    """Verify Odds Ratio and natural log OR computation."""
    # 2x2 table: Treated Events = 40, Treated Non = 60, Control Events = 20, Control Non = 80
    # OR = (40 * 80) / (60 * 20) = 3200 / 1200 = 2.6667
    or_res = EffectSizeCalculator.compute_odds_ratio(
        treated_events=40,
        treated_nonevents=60,
        control_events=20,
        control_nonevents=80,
    )
    assert pytest.approx(or_res["odds_ratio"], 0.01) == 2.67
    assert or_res["effect_size"] > 0  # ln(2.67) > 0
    assert or_res["variance"] > 0


def test_heterogeneity_engine():
    """Verify Cochrane Q, I^2, and Tau^2 calculations."""
    # Homogeneous studies
    effects_homo = [0.5, 0.52, 0.48]
    variances_homo = [0.04, 0.04, 0.04]
    het_homo = HeterogeneityEngine.compute(effects_homo, variances_homo)
    assert het_homo["degrees_of_freedom"] == 2
    assert het_homo["i_squared"] == 0.0

    # Heterogeneous studies
    effects_hetero = [0.1, 0.8, 1.5]
    variances_hetero = [0.01, 0.01, 0.01]
    het_hetero = HeterogeneityEngine.compute(effects_hetero, variances_hetero)
    assert het_hetero["q_statistic"] > 2.0
    assert het_hetero["i_squared"] > 50.0  # Substantial heterogeneity


def test_pooled_effect_synthesis_and_forest_plot():
    """Verify DerSimonian-Laird random effects pooling and forest plot generation."""
    studies = [
        {"id": "1", "title": "Study A", "publication_year": 2024, "effect_size": 0.45, "variance": 0.02, "sample_size": 100},
        {"id": "2", "title": "Study B", "publication_year": 2025, "effect_size": 0.60, "variance": 0.03, "sample_size": 150},
        {"id": "3", "title": "Study C", "publication_year": 2026, "effect_size": 0.50, "variance": 0.015, "sample_size": 200},
    ]

    result = PooledEffectEstimator.synthesize(studies, model_type="random_effects")
    assert result["total_studies_analyzed"] == 3
    assert 0.45 <= result["pooled_effect_size"] <= 0.60
    assert result["pooled_ci_lower"] < result["pooled_effect_size"] < result["pooled_ci_upper"]
    assert len(result["forest_plot_data"]) == 3
    assert result["forest_plot_data"][0]["weight_percentage"] > 0


def test_prisma_flow_tracker():
    """Verify PRISMA 2020 flow metrics."""
    flow = PRISMAFlowTracker.generate_flow_summary(
        identified=500,
        screened=450,
        eligible=120,
        included=30,
        excluded=470,
        exclusion_reasons={"non_comparative": 200, "no_quantitative_outcomes": 270},
    )
    assert flow["identification"]["records_identified_databases"] == 500
    assert flow["included"]["studies_included_in_review"] == 30
    assert flow["attrition_rate"] == 94.0


def test_risk_of_bias_evaluator():
    """Verify RoB 2 deterministic scoring."""
    rob_rct = RiskOfBiasEvaluator.evaluate_study(
        methodology_type="RCT",
        has_control_group=True,
        is_randomized=True,
        sample_size=150,
        attrition_pct=5.0,
    )
    assert rob_rct["overall_risk"] == "low_risk"

    rob_flawed = RiskOfBiasEvaluator.evaluate_study(
        methodology_type="Observational",
        has_control_group=False,
        is_randomized=False,
        sample_size=15,
        attrition_pct=30.0,
    )
    assert rob_flawed["overall_risk"] == "high_risk"
    assert rob_flawed["confounding_bias"] == "high_risk"


def test_slr_orchestrator():
    """Verify end-to-end SLR meta-analysis orchestration."""
    studies = [
        {"title": "Study Alpha", "effect_size": 0.55, "variance": 0.025},
        {"title": "Study Beta", "effect_size": 0.65, "variance": 0.030},
    ]
    orchestration = SLROrchestrator.run_meta_analysis(
        studies=studies,
        synthesis_name="AI CoT Diagnostic Accuracy",
        effect_metric="hedges_g",
    )
    assert orchestration["total_studies_analyzed"] == 2
    assert "summary_markdown" in orchestration
    assert "AI CoT Diagnostic Accuracy" in orchestration["summary_markdown"]
