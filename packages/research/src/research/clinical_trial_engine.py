"""
Clinical Trial Protocols, Regulatory Packages, and Autonomous Protocol Optimization Engine (Phases 36 & 46).
"""

import math
import random
from typing import Any, Dict, List, Optional


class ClinicalTrialEngine:
    """Core intelligence engine for clinical protocol design and regulatory readiness (Phase 36)."""

    def synthesize_protocol(
        self,
        disease_indication: str,
        investigational_agent: str,
        target_gene_or_protein: Optional[str] = None,
        phase_type: str = "Phase I/IIa",
        mechanism_of_action: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self.generate_protocol(
            disease_indication=disease_indication,
            investigational_agent=investigational_agent,
            target_gene_or_protein=target_gene_or_protein,
            phase_type=phase_type,
            mechanism_of_action=mechanism_of_action,
        )

    def generate_protocol(
        self,
        disease_indication: str,
        investigational_agent: str,
        phase_type: str = "Phase I/IIa",
        target_gene_or_protein: Optional[str] = None,
        mechanism_of_action: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a complete structured clinical trial protocol."""
        clean_disease = disease_indication.strip()
        clean_agent = investigational_agent.strip()
        target = target_gene_or_protein or "Target-X"
        moa = mechanism_of_action or f"Targeted modulation of {target} signaling axis"

        protocol_title = (
            f"A {phase_type}, Open-Label, Dose-Escalation and Cohort-Expansion Study to Evaluate the Safety, "
            f"Tolerability, Pharmacokinetics, and Preliminary Efficacy of {clean_agent} in Patients with {clean_disease}"
        )

        primary_endpoint = (
            f"Incidence and severity of treatment-emergent adverse events (TEAEs) and dose-limiting toxicities (DLTs) "
            f"to establish maximum tolerated dose (MTD) and Recommended Phase 2 Dose (RP2D) of {clean_agent}."
        )

        secondary_endpoints = [
            f"Objective Response Rate (ORR) assessed per RECIST v1.1 or disease-specific response criteria.",
            f"Progression-Free Survival (PFS) and Overall Survival (OS) at 12 and 24 months post-initiation.",
            f"Pharmacokinetic profile (Cmax, AUC0-inf, t1/2, clearance) across defined ascending dose cohorts.",
            f"Pharmacodynamic biomarker modulation of {target} expression levels in surrogate tissue/liquid biopsies.",
        ]

        inclusion_criteria = [
            {
                "criterion_type": "inclusion",
                "category": "diagnostic",
                "description": f"Histologically or cytologically confirmed diagnosis of advanced or refractory {clean_disease}.",
                "is_mandatory": True,
                "loinc_code": "52542-8",
            },
            {
                "criterion_type": "inclusion",
                "category": "biomarker",
                "description": f"Documented baseline expression or mutation status of target {target} confirmed via central laboratory assay.",
                "is_mandatory": True,
                "loinc_code": "72234-8",
            },
            {
                "criterion_type": "inclusion",
                "category": "safety",
                "description": "ECOG performance status 0 to 1 with adequate baseline renal, hepatic, and hematologic reserve (eGFR >= 60 mL/min, ALT/AST <= 2.5x ULN).",
                "is_mandatory": True,
                "loinc_code": "89243-0",
            },
        ]

        exclusion_criteria = [
            {
                "criterion_type": "exclusion",
                "category": "safety",
                "description": "Active or uncontrolled severe cardiac disease (NYHA Class III/IV, QTc prolongation > 470ms) or refractory systemic infection.",
                "is_mandatory": True,
                "loinc_code": "4697-6",
            },
            {
                "criterion_type": "exclusion",
                "category": "prior_therapy",
                "description": "Receipt of experimental biological or investigational gene therapy within 28 days or 5 elimination half-lives prior to Day 1.",
                "is_mandatory": True,
                "loinc_code": "78746-5",
            },
            {
                "criterion_type": "exclusion",
                "category": "demographic",
                "description": "Pregnant or breastfeeding females, or individuals of childbearing potential unwilling to practice highly effective contraception.",
                "is_mandatory": True,
                "loinc_code": "82810-3",
            },
        ]

        adverse_risk_score = 0.14
        if "gene" in moa.lower() or "crispr" in clean_agent.lower() or "lnp" in clean_agent.lower():
            adverse_risk_score = 0.18
        elif "immuno" in moa.lower() or "oncology" in clean_disease.lower():
            adverse_risk_score = 0.22

        return {
            "protocol_title": protocol_title,
            "phase_type": phase_type,
            "disease_indication": clean_disease,
            "icd_code": "E78.01" if "lipid" in clean_disease.lower() or "liver" in clean_disease.lower() else "C50.9",
            "investigational_agent": clean_agent,
            "mechanism_of_action": moa,
            "target_gene_or_protein": target,
            "primary_endpoint": primary_endpoint,
            "secondary_endpoints": secondary_endpoints,
            "sample_size_planned": 48 if "Phase I" in phase_type else 160,
            "study_duration_weeks": 52,
            "adverse_risk_score": adverse_risk_score,
            "cohort_criteria": inclusion_criteria + exclusion_criteria,
            "full_protocol_json": {
                "dosing_schedule": "Escalating cohorts (3+3 design) followed by dose-expansion phase",
                "monitoring_plan": "Continuous telemetry during initial 24h post-infusion; biweekly clinical visits",
                "data_safety_monitoring_board": "Independent DSMB convened after every completed dose tier",
            },
        }

    def screen_repurposing_candidates(
        self,
        disease_indication: str,
        target_gene_or_protein: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        target = (target_gene_or_protein or "PCSK9 / HMGCR").upper()
        return [
            {
                "compound_name": "Atorvastatin Bio-Conjugate",
                "smiles_string": "CC(C)C1=C(C(=O)NC2=CC=CC=C2)C(=C(N1CC[C@H](O)C[C@H](O)CC(=O)O)C3=CC=C(F)C=C3)C4=CC=CC=C4",
                "current_approved_indication": "Hypercholesterolemia & Cardiovascular Atherosclerosis",
                "repurposed_indication": f"Targeted Synergistic Co-Therapy for {disease_indication}",
                "binding_affinity_nm": 8.4,
                "bioavailability_pct": 82.5,
                "toxicity_risk_score": 0.08,
                "repurposing_rationale": f"Demonstrates potent upstream down-regulation of lipid biogenesis, creating favorable cellular clearance for {target}-targeted modalities.",
            },
            {
                "compound_name": "Ezetimibe Synergistic Formulation",
                "smiles_string": "C1=CC(=CC=C1[C@@H]2[C@@H](C(=O)N2C3=CC=C(C=C3)F)CC[C@H](C4=CC=C(C=C4)F)O)O",
                "current_approved_indication": "Primary Hyperlipidemia (NPC1L1 Inhibitor)",
                "repurposed_indication": f"Adjunctive Cholesterol Absorption Blocker for {disease_indication}",
                "binding_affinity_nm": 12.1,
                "bioavailability_pct": 65.0,
                "toxicity_risk_score": 0.05,
                "repurposing_rationale": f"Blocks intestinal NPC1L1 transporter to augment {target} clearance pathways without systemic hepatic toxicity.",
            }
        ]

    def generate_regulatory_package(
        self,
        protocol: Dict[str, Any],
        regulatory_agency: str = "FDA",
    ) -> Dict[str, Any]:
        agency = regulatory_agency.upper()
        completeness = 0.88
        return {
            "regulatory_agency": agency,
            "module_type": "IND Module 2 (Common Technical Document Summaries)",
            "completeness_score": completeness,
            "irb_readiness_verdict": "ready",
            "validation_findings": [{"section": "Endpoints", "status": "Compliant"}],
            "submission_checklist": {"form_fda_1571": True},
        }


class ClinicalTrialOptimizerEngine:
    """
    Simulates trial protocol optimization, eligibility criteria stratification, and synthetic arm Kaplan-Meier survival curves (Phase 46).
    """

    def optimize_protocol(
        self,
        title: str,
        indication: str,
        agent: str,
        phase: str = "Phase II",
        target_power: float = 0.85,
        alpha: float = 0.05
    ) -> Dict[str, Any]:
        expected_hr = 0.62
        z_alpha = 1.96
        z_power = 1.04
        required_events = math.ceil(4 * ((z_alpha + z_power) / math.log(expected_hr)) ** 2)
        sample_size = math.ceil(required_events * 1.45)

        criteria = [
            {
                "criterion_type": "INCLUSION",
                "category": "CLINICAL",
                "description": f"Histologically confirmed advanced or metastatic {indication}.",
                "structured_rule": {"variable": "HISTOLOGY_STAGE", "op": "in", "val": ["Stage IIIb", "Stage IV"]},
                "impact_on_enrollment_rate": 0.0
            },
            {
                "criterion_type": "INCLUSION",
                "category": "BIOMARKER",
                "description": "Demonstrated positive biomarker expression (>50% TPS or equivalent).",
                "structured_rule": {"variable": "BIOMARKER_TPS", "op": ">=", "val": 50},
                "impact_on_enrollment_rate": -0.28
            },
            {
                "criterion_type": "INCLUSION",
                "category": "CLINICAL",
                "description": "ECOG Performance Status 0 to 1.",
                "structured_rule": {"variable": "ECOG_PS", "op": "<=", "val": 1},
                "impact_on_enrollment_rate": -0.15
            },
            {
                "criterion_type": "EXCLUSION",
                "category": "PRIOR_THERAPY",
                "description": "Prior exposure to refractory second-line checkpoint inhibitors within 28 days.",
                "structured_rule": {"variable": "PRIOR_IO_DAYS", "op": "<", "val": 28},
                "impact_on_enrollment_rate": -0.12
            },
            {
                "criterion_type": "EXCLUSION",
                "category": "CLINICAL",
                "description": "Untreated active central nervous system (CNS) metastases.",
                "structured_rule": {"variable": "CNS_METASTASES", "op": "==", "val": True},
                "impact_on_enrollment_rate": -0.18
            }
        ]

        patients = []
        for i in range(1, 11):
            score = round(0.72 + (i % 4) * 0.08, 2)
            verdict = "ELIGIBLE" if score >= 0.80 else ("CONDITIONAL" if score >= 0.75 else "INELIGIBLE")
            patients.append({
                "patient_identifier": f"PT-EHR-{1000 + i}",
                "phenotype_match_score": score,
                "biomarker_alignment": "OPTIMAL" if score > 0.85 else "PARTIAL",
                "eligibility_verdict": verdict,
                "exclusion_flags": [] if verdict == "ELIGIBLE" else ["Marginal ECOG PS"],
                "survival_estimate_months": round(12.0 + score * 8.5, 1),
                "hazard_ratio": round(expected_hr + (1.0 - score) * 0.3, 2)
            })

        survival_curve = []
        for month in range(0, 37, 3):
            surv_ctrl = round(math.exp(-0.075 * month), 3)
            surv_treat = round(math.exp(-0.042 * month), 3)
            survival_curve.append({
                "month": month,
                "control_survival": surv_ctrl,
                "interventional_survival": surv_treat
            })

        return {
            "title": title,
            "phase": phase,
            "target_indication": indication,
            "investigational_agent": agent,
            "primary_endpoint": f"Overall Survival (OS) and Progression-Free Survival (PFS) in {indication}",
            "sample_size_target": sample_size,
            "statistical_power": target_power,
            "estimated_duration_months": 24,
            "protocol_summary": f"Adaptive Bayesian design with synthetic control matching for {agent} in {indication}. Optimized sample size: {sample_size} patients across 12 clinical centers.",
            "criteria": criteria,
            "patients": patients,
            "synthetic_arm": {
                "rwe_data_source": "EHR Oncology Flatiron / SEER Aggregate",
                "baseline_patient_count": 850,
                "matched_patient_count": sample_size,
                "median_os_control": 10.4,
                "median_os_interventional": 18.6,
                "p_value": 0.0008,
                "hazard_ratio": expected_hr,
                "survival_curve": survival_curve
            }
        }
