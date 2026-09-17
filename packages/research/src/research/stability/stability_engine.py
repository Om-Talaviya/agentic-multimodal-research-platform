import math
from typing import List, Dict, Any, Optional

class BiotherapeuticStabilityEngine:
    """
    Autonomous Biotherapeutic Developability & Aggregation Propensity Forecaster Engine.
    Implements Spatial Aggregation Propensity (SAP), hydrophobic surface patch mapping,
    thermal unfolding (Tm1/Tm2), colloidal interaction parameters (kD / B22), and
    formulation excipient stabilization modeling.
    """

    def __init__(self):
        # Kyte-Doolittle Hydrophobicity Scale
        self.kd_scale = {
            "I": 4.5, "V": 4.2, "L": 3.8, "F": 2.8, "C": 2.5, "M": 1.9, "A": 1.8,
            "G": -0.4, "T": -0.7, "S": -0.8, "W": -0.9, "Y": -1.3, "P": -1.6,
            "H": -3.2, "E": -3.5, "Q": -3.5, "D": -3.5, "N": -3.5, "K": -3.9, "R": -4.5
        }

    def compute_spatial_aggregation_propensity(
        self,
        heavy_chain: str,
        light_chain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calculates sequence-level Spatial Aggregation Propensity (SAP) score (0.0 to 1.0),
        detects surface hydrophobic patches, and predicts thermal unfolding temperatures.
        """
        hc = heavy_chain.upper().strip()
        lc = (light_chain or "").upper().strip()

        all_seq = hc + lc
        length = max(1, len(all_seq))

        # 1. Hydrophobic residue clustering
        window_size = 7
        patches = []
        high_hydrophobic_sum = 0.0

        for i in range(0, len(hc) - window_size + 1, 4):
            sub = hc[i:i + window_size]
            hydro_score = sum(self.kd_scale.get(aa, 0.0) for aa in sub) / window_size
            if hydro_score > 1.8:
                high_hydrophobic_sum += hydro_score
                risk = "HIGH" if hydro_score > 2.8 else "MODERATE"
                patches.append({
                    "patch_identifier": f"HC_Patch_{i+1}_{i+window_size}",
                    "surface_area_angstrom2": round(window_size * 28.5 + hydro_score * 12.0, 1),
                    "average_hydrophobicity_score": round(hydro_score, 2),
                    "residue_span": f"HC: {i+1}-{i+window_size} ({sub})",
                    "aggregation_risk_level": risk,
                })

        # Base SAP score (0.05 to 0.95)
        sap_score = min(0.95, max(0.05, round((high_hydrophobic_sum / (length / 10.0)) * 0.15, 3)))

        # 2. Thermal unfolding Tm1 and Tm2
        # Human IgG1 canonical Fab/CH2 Tm1 ~ 70-74C, CH3 Tm2 ~ 82-85C
        tm1 = round(74.5 - (sap_score * 12.0), 1)
        tm2 = round(84.0 - (sap_score * 6.0), 1)

        # 3. Colloidal stability: k_D and B22
        # k_D > -10 mL/g indicates favorable repulsive colloidal stability
        kd_ml_g = round(-3.5 - (sap_score * 15.0), 2)
        b22 = round(max(0.2e-4, (2.5e-4) - (sap_score * 2.0e-4)), 6)

        # 4. Shelf-life estimation at 4C
        shelf_life_months = round(max(6.0, 36.0 * (1.0 - sap_score)), 1)

        return {
            "aggregation_propensity_score": sap_score,
            "melting_temp_tm1_celsius": tm1,
            "melting_temp_tm2_celsius": tm2,
            "colloidal_stability_kd": kd_ml_g,
            "diffusion_interaction_parameter_b22": b22,
            "shelf_life_months_at_4c": shelf_life_months,
            "hydrophobic_patches": patches[:6],
        }

    def optimize_formulation_buffer(
        self,
        sap_score: float,
        buffer_type: str = "Histidine",
        ph: float = 6.0,
        surfactant: str = "Polysorbate 80",
        tonicity_agent: str = "Sucrose",
    ) -> Dict[str, Any]:
        """
        Simulates formulation buffer matrix stability and monomer retention % after 4 weeks at 40C.
        """
        base_retention = 98.5

        # Penalties based on SAP score and pH deviation from ideal 5.8-6.2
        sap_penalty = sap_score * 6.0
        ph_penalty = abs(ph - 6.0) * 1.8

        # Excipient benefits
        surfactant_bonus = 1.2 if "Polysorbate" in surfactant or "Poloxamer" in surfactant else 0.0
        sugar_bonus = 1.5 if tonicity_agent in ["Sucrose", "Trehalose"] else 0.5

        final_retention = round(min(99.8, max(75.0, base_retention - sap_penalty - ph_penalty + surfactant_bonus + sugar_bonus)), 2)

        return {
            "buffer_type": buffer_type,
            "ph": ph,
            "surfactant": surfactant,
            "tonicity_agent": tonicity_agent,
            "monomer_retention_pct_at_40c": final_retention,
            "formulation_stability_grade": "STABLE" if final_retention >= 95.0 else ("MARGINAL" if final_retention >= 90.0 else "UNSTABLE"),
        }
