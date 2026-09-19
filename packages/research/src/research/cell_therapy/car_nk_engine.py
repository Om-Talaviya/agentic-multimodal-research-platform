"""Autonomous CAR-NK & Immuno-Oncology SynNotch Circuit Designer (Phase 96)."""

from typing import Dict, Any, List, Optional


class CarNkDesignEngine:
    """Simulates CAR-NK cell killing kinetics, SynNotch multi-antigen gating, and cytokine armor secretion."""

    CO_STIMULATORY_PROFILES = {
        "2B4_plus_41BB": {"cytotoxicity": 92.0, "persistence": 88.0, "exhaustion_resistance": 90.0},
        "DNAM1_plus_CD28": {"cytotoxicity": 95.0, "persistence": 74.0, "exhaustion_resistance": 79.0},
        "DAP12_plus_NKG2D": {"cytotoxicity": 89.0, "persistence": 83.0, "exhaustion_resistance": 86.0},
        "41BB_only": {"cytotoxicity": 81.0, "persistence": 85.0, "exhaustion_resistance": 88.0},
    }

    def design_car_nk(
        self,
        construct_name: str,
        primary_target: str,
        costimulatory_domain: str = "2B4_plus_41BB",
        synnotch_sensor_antigen: Optional[str] = "EpCAM",
        gate_type: str = "AND_GATE",
        armored_cytokine: str = "IL-15",
    ) -> Dict[str, Any]:
        """Designs and simulates an armored, SynNotch-gated CAR-NK construct."""
        costim = self.CO_STIMULATORY_PROFILES.get(costimulatory_domain, self.CO_STIMULATORY_PROFILES["2B4_plus_41BB"])

        cytotoxicity = costim["cytotoxicity"]
        persistence = costim["persistence"]
        exhaustion_res = costim["exhaustion_resistance"]

        # SynNotch logic effect
        if synnotch_sensor_antigen:
            safety_margin = 96.5 if gate_type == "AND_GATE" else 98.2
            enrichment_fold = 18.2 if gate_type == "AND_GATE" else 24.0
            leaky_pct = 1.4
        else:
            safety_margin = 72.0
            enrichment_fold = 1.0
            leaky_pct = 0.0

        synnotch_gates = []
        if synnotch_sensor_antigen:
            synnotch_gates.append({
                "gate_type": gate_type,
                "sensor_antigen": synnotch_sensor_antigen,
                "actuator_payload": f"CAR-{primary_target} Transcription",
                "specificity_enrichment": enrichment_fold,
                "leaky_expression_pct": leaky_pct,
            })

        cytokine_profiles = [
            {
                "cytokine_name": armored_cytokine,
                "secretion_level_pg_ml": 850.0 if armored_cytokine == "IL-15" else 620.0,
                "is_armored_payload": "MEMBRANE_BOUND_CLEAVABLE",
            },
            {
                "cytokine_name": "Granzyme-B",
                "secretion_level_pg_ml": 1450.0,
                "is_armored_payload": "NATURAL_DEGRANULATION",
            },
            {
                "cytokine_name": "IFN-gamma",
                "secretion_level_pg_ml": 420.0,
                "is_armored_payload": "ACTIVATION_INDUCED",
            },
        ]

        return {
            "construct_name": construct_name,
            "primary_target": primary_target,
            "costimulatory_domain": costimulatory_domain,
            "signaling_domain": "CD3zeta",
            "cytotoxicity_score": cytotoxicity,
            "persistence_index": persistence,
            "exhaustion_resistance_score": exhaustion_res,
            "off_tumor_safety_margin": safety_margin,
            "synnotch_gates": synnotch_gates,
            "cytokines": cytokine_profiles,
            "rationale": f"CAR-NK engineered with {costimulatory_domain} and {gate_type} SynNotch against {primary_target}/{synnotch_sensor_antigen or 'None'} with {armored_cytokine} armoring.",
        }
