"""Synthetic Cell Membrane Dynamics & LNP Formulation Simulator Engine."""
import math
from typing import List, Dict, Any, Optional


class LNPFormulationSimulatorEngine:
    """Simulates Lipid Nanoparticle (LNP) formulation biophysics, microfluidic mixing parameters, and synthetic membrane dynamics."""

    def simulate_formulation(
        self,
        formulation_input: Dict[str, Any],
        raw_components: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Calculates particle size, PDI, encapsulation efficiency, apparent pKa, and membrane fluidity parameters."""
        name = formulation_input.get("formulation_name", "mRNA-LNP Benchmark Construct")
        cargo = formulation_input.get("cargo_type", "mRNA")
        ionizable_name = formulation_input.get("ionizable_lipid_name", "ALC-0315")
        np_ratio = float(formulation_input.get("np_ratio", 6.0))
        frr = float(formulation_input.get("flow_rate_ratio_aqueous_organic", 3.0))
        tfr_ml_min = float(formulation_input.get("total_flow_rate_ml_min", 12.0))

        # Default 4-lipid composition if not provided
        default_components = [
            {
                "component_name": ionizable_name,
                "lipid_category": "IONIZABLE_LIPID",
                "molar_percentage": 50.0,
                "molecular_weight_g_mol": 766.3,
                "charge_at_ph7": 0.05,
            },
            {
                "component_name": "DSPC",
                "lipid_category": "HELPER_LIPID",
                "molar_percentage": 10.0,
                "molecular_weight_g_mol": 790.2,
                "charge_at_ph7": 0.0,
            },
            {
                "component_name": "Cholesterol",
                "lipid_category": "CHOLESTEROL",
                "molar_percentage": 38.5,
                "molecular_weight_g_mol": 386.7,
                "charge_at_ph7": 0.0,
            },
            {
                "component_name": "DMG-PEG2000",
                "lipid_category": "PEG_LIPID",
                "molar_percentage": 1.5,
                "molecular_weight_g_mol": 2509.2,
                "charge_at_ph7": 0.0,
            },
        ]

        components = raw_components or default_components

        # Extract PEG percentage for size modeling
        peg_pct = next((c.get("molar_percentage", 1.5) for c in components if c.get("lipid_category") == "PEG_LIPID"), 1.5)

        # Microfluidic formulation physics calculations
        # Size decreases with higher PEG % and higher TFR
        size_nm = round(max(45.0, min(160.0, 120.0 - (peg_pct * 22.0) - (math.log10(max(1.0, tfr_ml_min)) * 8.0))), 1)
        pdi = round(max(0.04, min(0.28, 0.08 + (0.02 * abs(frr - 3.0)) + (0.01 / max(0.5, peg_pct)))), 2)
        ee_pct = round(max(60.0, min(98.5, 82.0 + (math.log(max(1.0, np_ratio)) * 7.5))), 1)

        # Apparent pKa estimation (TNS assay simulation)
        pka = round(6.45 + (0.02 * (np_ratio - 6.0)), 2)
        zeta_mv = round(2.4 + (0.3 * (np_ratio - 6.0)), 1)

        # Membrane dynamics biophysical profile
        membrane_profile = {
            "membrane_thickness_angstrom": round(39.5 + (0.2 * peg_pct), 1),
            "area_per_lipid_angstrom2": round(62.4 - (0.15 * peg_pct), 1),
            "order_parameter_s2": 0.22,
            "bending_modulus_kc_kbt": 24.5,
            "endosomal_escape_efficiency_pct": round(max(5.0, min(35.0, 12.0 + (ee_pct * 0.1) - (abs(pka - 6.4) * 15.0))), 1),
            "cytotoxicity_score": round(max(0.02, min(0.60, 0.08 + (0.015 * np_ratio))), 2),
        }

        molar_ratios = {c["component_name"]: c.get("molar_percentage", 0.0) for c in components}

        return {
            "formulation_name": name,
            "cargo_type": cargo,
            "ionizable_lipid_name": ionizable_name,
            "lipid_ratio_molar_json": molar_ratios,
            "np_ratio": np_ratio,
            "encapsulation_efficiency_pct": ee_pct,
            "mean_diameter_nm": size_nm,
            "pdi_polydispersity_index": pdi,
            "zeta_potential_mv": zeta_mv,
            "apparent_pka": pka,
            "components": components,
            "membrane_profile": membrane_profile,
            "simulation_metadata_json": {
                "microfluidic_frr": frr,
                "total_flow_rate_ml_min": tfr_ml_min,
                "solvent_aqueous_buffer": "Citrate Buffer pH 4.0",
                "organic_solvent": "100% Ethanol",
                "dialysis_buffer": "PBS pH 7.4",
                "cryoprotectant": "10% Sucrose",
            }
        }
