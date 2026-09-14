"""Deterministic Meta-Analysis and Systematic Literature Review (SLR) Engine."""

import math
from typing import Any, Dict, List, Optional, Tuple
import uuid

from shared.logging import get_logger

logger = get_logger(__name__)


def _norm_cdf(x: float) -> float:
    """Standard normal cumulative distribution function."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _chi2_p_value(q: float, df: int) -> float:
    """Approximate Chi-square p-value using Wilson-Hilferty normal approximation."""
    if df <= 0 or q <= 0:
        return 1.0
    # Wilson-Hilferty transformation: ((q/df)^(1/3) - (1 - 2/(9*df))) / sqrt(2/(9*df)) ~ N(0, 1)
    factor = 2.0 / (9.0 * df)
    transformed = ((q / df) ** (1.0 / 3.0) - (1.0 - factor)) / math.sqrt(factor)
    return max(0.0, min(1.0, 1.0 - _norm_cdf(transformed)))


class EffectSizeCalculator:
    """Deterministic calculation of standard scientific effect sizes and variances."""

    @staticmethod
    def compute_cohens_d(
        mean1: float,
        mean2: float,
        sd1: float,
        sd2: float,
        n1: int,
        n2: int,
    ) -> Dict[str, float]:
        """Compute Cohen's d, pooled variance, standard error, and 95% CI."""
        if n1 <= 1 or n2 <= 1 or sd1 <= 0 or sd2 <= 0:
            raise ValueError("Sample sizes must be > 1 and SDs must be positive.")

        # Pooled standard deviation
        numerator = ((n1 - 1) * (sd1 ** 2)) + ((n2 - 1) * (sd2 ** 2))
        denominator = n1 + n2 - 2
        s_pooled = math.sqrt(numerator / denominator)

        if s_pooled == 0:
            d = 0.0
        else:
            d = (mean1 - mean2) / s_pooled

        # Variance of Cohen's d
        variance = ((n1 + n2) / (n1 * n2)) + ((d ** 2) / (2.0 * (n1 + n2)))
        se = math.sqrt(variance)
        ci_lower = d - (1.96 * se)
        ci_upper = d + (1.96 * se)

        return {
            "effect_size": round(d, 4),
            "variance": round(variance, 6),
            "standard_error": round(se, 4),
            "ci_lower": round(ci_lower, 4),
            "ci_upper": round(ci_upper, 4),
            "metric": "cohens_d",
        }

    @staticmethod
    def compute_hedges_g(
        d: float,
        n1: int,
        n2: int,
        variance_d: Optional[float] = None,
    ) -> Dict[str, float]:
        """Compute small-sample bias corrected Hedges' g."""
        df = n1 + n2 - 2
        if df <= 0:
            return {"effect_size": d, "variance": 0.0, "standard_error": 0.0, "ci_lower": d, "ci_upper": d, "metric": "hedges_g"}

        # Hedges' small-sample correction factor J
        j_correction = 1.0 - (3.0 / (4.0 * df - 1.0))
        g = d * j_correction

        if variance_d is None:
            variance_d = ((n1 + n2) / (n1 * n2)) + ((d ** 2) / (2.0 * (n1 + n2)))

        variance_g = (j_correction ** 2) * variance_d
        se_g = math.sqrt(variance_g)
        ci_lower = g - (1.96 * se_g)
        ci_upper = g + (1.96 * se_g)

        return {
            "effect_size": round(g, 4),
            "variance": round(variance_g, 6),
            "standard_error": round(se_g, 4),
            "ci_lower": round(ci_lower, 4),
            "ci_upper": round(ci_upper, 4),
            "correction_factor": round(j_correction, 4),
            "metric": "hedges_g",
        }

    @staticmethod
    def compute_odds_ratio(
        treated_events: int,
        treated_nonevents: int,
        control_events: int,
        control_nonevents: int,
    ) -> Dict[str, float]:
        """Compute natural log Odds Ratio (lnOR), variance, and exponentiated OR."""
        # Add 0.5 continuity correction if zero cell count
        a = treated_events + 0.5 if (treated_events == 0 or treated_nonevents == 0 or control_events == 0 or control_nonevents == 0) else float(treated_events)
        b = treated_nonevents + 0.5 if (treated_events == 0 or treated_nonevents == 0 or control_events == 0 or control_nonevents == 0) else float(treated_nonevents)
        c = control_events + 0.5 if (treated_events == 0 or treated_nonevents == 0 or control_events == 0 or control_nonevents == 0) else float(control_events)
        d = control_nonevents + 0.5 if (treated_events == 0 or treated_nonevents == 0 or control_events == 0 or control_nonevents == 0) else float(control_nonevents)

        odds_ratio = (a * d) / (b * c)
        ln_or = math.log(odds_ratio)
        variance = (1.0 / a) + (1.0 / b) + (1.0 / c) + (1.0 / d)
        se = math.sqrt(variance)

        ci_lower_ln = ln_or - (1.96 * se)
        ci_upper_ln = ln_or + (1.96 * se)

        return {
            "effect_size": round(ln_or, 4),
            "odds_ratio": round(odds_ratio, 4),
            "variance": round(variance, 6),
            "standard_error": round(se, 4),
            "ci_lower": round(ci_lower_ln, 4),
            "ci_upper": round(ci_upper_ln, 4),
            "or_ci_lower": round(math.exp(ci_lower_ln), 4),
            "or_ci_upper": round(math.exp(ci_upper_ln), 4),
            "metric": "log_odds_ratio",
        }


class HeterogeneityEngine:
    """Calculates study heterogeneity statistics (Cochrane Q, I^2, Tau^2)."""

    @staticmethod
    def compute(
        effects: List[float],
        variances: List[float],
    ) -> Dict[str, float]:
        """Compute Cochrane's Q, degrees of freedom, I^2 (%), Tau^2, and heterogeneity p-value."""
        k = len(effects)
        if k < 2 or len(variances) != k:
            return {
                "q_statistic": 0.0,
                "degrees_of_freedom": 0,
                "i_squared": 0.0,
                "tau_squared": 0.0,
                "p_value": 1.0,
            }

        # Inverse variance weights under fixed effect
        weights = [1.0 / max(1e-9, v) for v in variances]
        sum_w = sum(weights)
        if sum_w == 0:
            return {"q_statistic": 0.0, "degrees_of_freedom": k - 1, "i_squared": 0.0, "tau_squared": 0.0, "p_value": 1.0}

        fixed_pooled = sum(w * e for w, e in zip(weights, effects)) / sum_w

        # Cochrane's Q
        q = sum(w * ((e - fixed_pooled) ** 2) for w, e in zip(weights, effects))
        df = k - 1

        # Inconsistency index I^2 (percentage of variance attributable to study heterogeneity)
        if q > df and q > 0:
            i_squared = ((q - df) / q) * 100.0
        else:
            i_squared = 0.0

        # DerSimonian-Laird estimate of between-study variance Tau^2
        sum_w_sq = sum(w ** 2 for w in weights)
        c = sum_w - (sum_w_sq / sum_w)
        if c > 0 and q > df:
            tau_squared = (q - df) / c
        else:
            tau_squared = 0.0

        p_val = _chi2_p_value(q, df)

        return {
            "q_statistic": round(q, 4),
            "degrees_of_freedom": df,
            "i_squared": round(min(100.0, max(0.0, i_squared)), 2),
            "tau_squared": round(tau_squared, 6),
            "p_value": round(p_val, 4),
        }


class PooledEffectEstimator:
    """Synthesizes multiple studies into pooled effect sizes and forest plot datasets."""

    @classmethod
    def synthesize(
        cls,
        studies: List[Dict[str, Any]],
        model_type: str = "random_effects",  # 'fixed_effect' or 'random_effects'
    ) -> Dict[str, Any]:
        """Perform full quantitative meta-analysis synthesis across included studies."""
        valid_studies = [
            s for s in studies
            if s.get("effect_size") is not None and s.get("variance") is not None and s.get("variance") > 0
        ]

        if not valid_studies:
            return {
                "total_studies_analyzed": 0,
                "pooled_effect_size": 0.0,
                "pooled_ci_lower": 0.0,
                "pooled_ci_upper": 0.0,
                "pooled_p_value": 1.0,
                "z_score": 0.0,
                "q_statistic": 0.0,
                "degrees_of_freedom": 0,
                "i_squared": 0.0,
                "tau_squared": 0.0,
                "forest_plot_data": [],
                "model_type": model_type,
            }

        effects = [float(s["effect_size"]) for s in valid_studies]
        variances = [float(s["variance"]) for s in valid_studies]

        # Calculate Heterogeneity
        het = HeterogeneityEngine.compute(effects, variances)
        tau_sq = het["tau_squared"] if model_type == "random_effects" else 0.0

        # Calculate Study Weights
        adjusted_weights = []
        for v in variances:
            w = 1.0 / (v + tau_sq)
            adjusted_weights.append(w)

        sum_w = sum(adjusted_weights)
        if sum_w == 0:
            sum_w = 1e-9

        # Pooled Effect
        pooled_effect = sum(w * e for w, e in zip(adjusted_weights, effects)) / sum_w
        pooled_variance = 1.0 / sum_w
        pooled_se = math.sqrt(pooled_variance)

        pooled_ci_low = pooled_effect - (1.96 * pooled_se)
        pooled_ci_high = pooled_effect + (1.96 * pooled_se)

        z_score = pooled_effect / max(1e-9, pooled_se)
        p_val = 2.0 * (1.0 - _norm_cdf(abs(z_score)))

        # Build Forest Plot Data Points
        forest_plot_data = []
        for s, eff, var, w in zip(valid_studies, effects, variances, adjusted_weights):
            se = math.sqrt(var)
            ci_low = eff - (1.96 * se)
            ci_high = eff + (1.96 * se)
            weight_pct = (w / sum_w) * 100.0

            forest_plot_data.append({
                "study_id": str(s.get("id", "")),
                "title": s.get("title", "Study"),
                "year": s.get("publication_year"),
                "authors": s.get("authors", []),
                "sample_size": s.get("sample_size"),
                "effect_size": round(eff, 4),
                "variance": round(var, 6),
                "standard_error": round(se, 4),
                "ci_lower": round(ci_low, 4),
                "ci_upper": round(ci_high, 4),
                "weight_percentage": round(weight_pct, 2),
            })

        return {
            "total_studies_analyzed": len(valid_studies),
            "pooled_effect_size": round(pooled_effect, 4),
            "pooled_ci_lower": round(pooled_ci_low, 4),
            "pooled_ci_upper": round(pooled_ci_high, 4),
            "pooled_p_value": round(p_val, 4),
            "z_score": round(z_score, 4),
            "q_statistic": het["q_statistic"],
            "degrees_of_freedom": het["degrees_of_freedom"],
            "i_squared": het["i_squared"],
            "tau_squared": het["tau_squared"],
            "forest_plot_data": forest_plot_data,
            "model_type": model_type,
        }


class PRISMAFlowTracker:
    """Tracks and formats PRISMA 2020 systematic review flow metrics."""

    @staticmethod
    def generate_flow_summary(
        identified: int,
        screened: int,
        eligible: int,
        included: int,
        excluded: int,
        exclusion_reasons: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        """Construct standard PRISMA 2020 flow nodes and attrition funnel."""
        return {
            "identification": {
                "records_identified_databases": identified,
                "records_removed_before_screening": 0,
            },
            "screening": {
                "records_screened": screened,
                "records_excluded_title_abstract": excluded if screened > eligible else 0,
            },
            "eligibility": {
                "reports_sought_for_retrieval": eligible,
                "reports_not_retrieved": 0,
                "reports_assessed_for_eligibility": eligible,
                "reports_excluded_with_reasons": exclusion_reasons or {},
            },
            "included": {
                "studies_included_in_review": included,
                "reports_included_in_meta_analysis": included,
            },
            "attrition_rate": round(((identified - included) / max(1, identified)) * 100, 2),
        }


class RiskOfBiasEvaluator:
    """Evaluates study methodological quality across Cochrane RoB 2 / ROBINS-I criteria."""

    @staticmethod
    def evaluate_study(
        methodology_type: Optional[str],
        has_control_group: bool = True,
        is_randomized: bool = True,
        sample_size: Optional[int] = None,
        attrition_pct: float = 0.0,
    ) -> Dict[str, Any]:
        """Deterministic heuristic scoring for risk of bias across core domains."""
        # Selection Bias
        if is_randomized:
            sel_bias = "low_risk"
        elif methodology_type in ["Observational", "Case Study"]:
            sel_bias = "some_concerns"
        else:
            sel_bias = "low_risk"

        # Confounding Bias
        if not has_control_group:
            conf_bias = "high_risk"
        elif methodology_type == "RCT":
            conf_bias = "low_risk"
        else:
            conf_bias = "some_concerns"

        # Measurement Bias
        if sample_size and sample_size < 30:
            meas_bias = "some_concerns"
        else:
            meas_bias = "low_risk"

        # Reporting Bias
        if attrition_pct > 20.0:
            rep_bias = "high_risk"
        elif attrition_pct > 10.0:
            rep_bias = "some_concerns"
        else:
            rep_bias = "low_risk"

        # Overall synthesis
        if "high_risk" in [sel_bias, conf_bias, meas_bias, rep_bias]:
            overall = "high_risk"
        elif [sel_bias, conf_bias, meas_bias, rep_bias].count("some_concerns") >= 2:
            overall = "some_concerns"
        else:
            overall = "low_risk"

        return {
            "selection_bias": sel_bias,
            "confounding_bias": conf_bias,
            "measurement_bias": meas_bias,
            "reporting_bias": rep_bias,
            "overall_risk": overall,
            "domain_scores": {
                "selection": 1.0 if sel_bias == "low_risk" else (0.5 if sel_bias == "some_concerns" else 0.0),
                "confounding": 1.0 if conf_bias == "low_risk" else (0.5 if conf_bias == "some_concerns" else 0.0),
                "measurement": 1.0 if meas_bias == "low_risk" else (0.5 if meas_bias == "some_concerns" else 0.0),
                "reporting": 1.0 if rep_bias == "low_risk" else (0.5 if rep_bias == "some_concerns" else 0.0),
            },
        }


class SLROrchestrator:
    """Coordinates the end-to-end SLR and Meta-Analysis pipeline."""

    @classmethod
    def run_meta_analysis(
        cls,
        studies: List[Dict[str, Any]],
        synthesis_name: str,
        effect_metric: str = "hedges_g",
        model_type: str = "random_effects",
    ) -> Dict[str, Any]:
        """Execute complete quantitative meta-analysis calculation."""
        meta_results = PooledEffectEstimator.synthesize(studies, model_type=model_type)

        summary_md = (
            f"### Meta-Analysis Synthesis: {synthesis_name}\n\n"
            f"- **Analyzed Studies**: {meta_results['total_studies_analyzed']}\n"
            f"- **Model**: {model_type.replace('_', ' ').title()}\n"
            f"- **Pooled Effect Size ({effect_metric})**: {meta_results['pooled_effect_size']} "
            f"[95% CI: {meta_results['pooled_ci_lower']} to {meta_results['pooled_ci_upper']}]\n"
            f"- **Test of Overall Effect**: $Z = {meta_results['z_score']}$ ($p = {meta_results['pooled_p_value']}$)\n"
            f"- **Heterogeneity**: $Q = {meta_results['q_statistic']}$ ($df = {meta_results['degrees_of_freedom']}$), "
            f"$I^2 = {meta_results['i_squared']}\\%$, $\\tau^2 = {meta_results['tau_squared']}$\n"
        )

        return {
            **meta_results,
            "synthesis_name": synthesis_name,
            "effect_metric": effect_metric,
            "summary_markdown": summary_md,
        }
