"""Clinical Trial Site Selection & Protocol Feasibility Engine."""
import math
import random
from typing import List, Dict, Any, Optional


class ClinicalSiteSelectionEngine:
    """Evaluates candidate clinical trial sites and forecasts protocol recruitment feasibility."""

    def evaluate_site(self, site_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates feasibility score and risk tier for a single candidate site."""
        rate = float(site_data.get("historical_recruitment_rate", 1.0))
        timeline_days = int(site_data.get("ethics_approval_timeline_days", 45))
        density = int(site_data.get("patient_pool_density", 1000))
        pi_exp_years = float(site_data.get("pi_experience_years", 5.0))
        competing_trials = int(site_data.get("competing_trials_count", 1))

        # Velocity score (0.0 to 1.0): based on patients/month (3.0+ is top tier)
        velocity_score = min(1.0, rate / 3.0)

        # Regulatory speed score: 30 days is excellent, 90+ is slow
        reg_score = max(0.1, min(1.0, (90.0 - timeline_days) / 60.0))

        # Density score: 5000+ is max
        density_score = min(1.0, density / 5000.0)

        # Competition penalty
        comp_factor = max(0.4, 1.0 - (competing_trials * 0.1))

        # PI factor
        pi_factor = min(1.0, pi_exp_years / 10.0)

        feasibility_score = round(
            0.35 * velocity_score +
            0.20 * reg_score +
            0.20 * density_score +
            0.15 * pi_factor +
            0.10 * comp_factor,
            3
        )

        if feasibility_score >= 0.75:
            risk_tier = "LOW_RISK"
        elif feasibility_score >= 0.50:
            risk_tier = "MODERATE_RISK"
        else:
            risk_tier = "HIGH_RISK"

        return {
            "site_name": site_data.get("site_name", "Unknown Site"),
            "country": site_data.get("country", "Unknown"),
            "city": site_data.get("city", "Unknown"),
            "principal_investigator": site_data.get("principal_investigator", "Dr. Investigator"),
            "historical_recruitment_rate": rate,
            "ethics_approval_timeline_days": timeline_days,
            "patient_pool_density": density,
            "feasibility_score": feasibility_score,
            "risk_tier": risk_tier,
            "selected_for_trial": feasibility_score >= 0.50,
            "metrics_json": {
                "velocity_score": round(velocity_score, 3),
                "reg_score": round(reg_score, 3),
                "density_score": round(density_score, 3),
                "pi_factor": round(pi_factor, 3),
                "competing_trials": competing_trials,
            }
        }

    def simulate_recruitment(
        self,
        target_enrollment: int,
        recruitment_duration_months: float,
        sites: List[Dict[str, Any]],
        dropout_rate: float = 0.10,
        n_simulations: int = 100,
    ) -> Dict[str, Any]:
        """Runs stochastic Poisson-gamma Monte Carlo simulation of enrollment trajectory."""
        selected_sites = [s for s in sites if s.get("selected_for_trial", True)]
        if not selected_sites:
            selected_sites = sites

        base_aggregate_rate = sum(s.get("historical_recruitment_rate", 1.0) for s in selected_sites)
        if base_aggregate_rate <= 0:
            base_aggregate_rate = 1.0

        effective_target = int(math.ceil(target_enrollment / (1.0 - dropout_rate)))
        simulated_durations = []

        # Deterministic pseudo-random seed for reproducibility in testing
        rng = random.Random(42)

        for _ in range(n_simulations):
            cum_patients = 0
            month = 0.0
            step = 0.5
            while cum_patients < effective_target and month < recruitment_duration_months * 3.0:
                # Add slight noise to aggregate monthly rate
                noise = rng.gauss(1.0, 0.15)
                monthly_rate = max(0.2, base_aggregate_rate * noise)
                cum_patients += monthly_rate * step
                month += step
            simulated_durations.append(month)

        simulated_durations.sort()
        p10 = round(simulated_durations[int(0.10 * len(simulated_durations))], 1)
        p50 = round(simulated_durations[int(0.50 * len(simulated_durations))], 1)
        p90 = round(simulated_durations[int(0.90 * len(simulated_durations))], 1)

        # Generate trajectory curve points for P50
        curve_points = []
        cum = 0.0
        max_months = int(math.ceil(p90 * 1.2))
        for m in range(1, max_months + 1):
            cum += base_aggregate_rate * (1.0 - math.exp(-m / 4.0))  # Site ramp-up curve
            enrolled = min(float(target_enrollment), round(cum * (1.0 - dropout_rate), 1))
            curve_points.append({
                "month": m,
                "projected_enrolled": enrolled,
                "target_enrolled": min(float(target_enrollment), round(target_enrollment * (m / recruitment_duration_months), 1)),
            })

        # Identify bottleneck risks
        bottlenecks = []
        if p90 > recruitment_duration_months:
            bottlenecks.append({
                "risk_type": "TIMELINE_OVERRUN",
                "severity": "HIGH",
                "description": f"P90 completion timeline ({p90} mo) exceeds target ({recruitment_duration_months} mo).",
                "recommendation": "Activate 2-3 additional high-density investigative sites."
            })
        avg_approval = sum(s.get("ethics_approval_timeline_days", 45) for s in selected_sites) / len(selected_sites)
        if avg_approval > 60:
            bottlenecks.append({
                "risk_type": "REGULATORY_DELAY",
                "severity": "MODERATE",
                "description": f"Average ethics/IRB turnaround ({round(avg_approval, 1)} days) delays study start.",
                "recommendation": "Initiate parallel central IRB submission and pre-screen patients."
            })

        return {
            "simulation_name": "Monte Carlo Stochastic Enrollment v1",
            "target_timeline_months": recruitment_duration_months,
            "p10_completion_months": p10,
            "p50_completion_months": p50,
            "p90_completion_months": p90,
            "dropout_rate": dropout_rate,
            "enrollment_curve_json": curve_points,
            "bottleneck_risks_json": bottlenecks,
        }

    def evaluate_study_feasibility(
        self,
        study_data: Dict[str, Any],
        sites_input: List[Dict[str, Any]],
        dropout_rate: float = 0.10,
    ) -> Dict[str, Any]:
        """End-to-end evaluation of study protocol feasibility and candidate sites."""
        evaluated_sites = [self.evaluate_site(s) for s in sites_input]
        target = int(study_data.get("target_enrollment", 100))
        duration = float(study_data.get("recruitment_duration_months", 12.0))

        sim_result = self.simulate_recruitment(
            target_enrollment=target,
            recruitment_duration_months=duration,
            sites=evaluated_sites,
            dropout_rate=dropout_rate,
        )

        return {
            "study_title": study_data.get("study_title", "Clinical Study"),
            "protocol_code": study_data.get("protocol_code", "CT-001"),
            "indication": study_data.get("indication", "Oncology"),
            "phase": study_data.get("phase", "Phase 2"),
            "target_enrollment": target,
            "recruitment_duration_months": duration,
            "total_sites": len(evaluated_sites),
            "evaluated_sites": evaluated_sites,
            "simulation": sim_result,
        }
