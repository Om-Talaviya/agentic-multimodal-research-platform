"""Chemogenomics Polypharmacology & Off-Target Interactome Engine."""
import math
from typing import List, Dict, Any, Optional


class ChemogenomicsPolypharmacologyEngine:
    """Profiles compound polypharmacology across kinase/GPCR panels and flags antitarget liabilities."""

    def screen_compound(
        self,
        compound_input: Dict[str, Any],
        affinities_input: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Calculates Gini selectivity index, classifies selectivity tier, and identifies off-target safety risks."""
        name = compound_input.get("compound_name", "Imatinib")
        smiles = compound_input.get("smiles", "CC1=C(C=C(C=C1)NC(=O)C2=CC=C(C=C2)CN3CCN(CC3)C)NC4=NC=CC(=N4)C5=CN=CC=C5")
        primary_target = compound_input.get("primary_target", "ABL1")

        # Default multi-target binding panel if none provided
        affinities = affinities_input or [
            {"target_gene": "ABL1", "uniprot_id": "P00519", "protein_family": "KINASE", "affinity_type": "IC50", "affinity_value_nm": 38.0, "is_primary_target": True},
            {"target_gene": "KIT", "uniprot_id": "P10721", "protein_family": "KINASE", "affinity_type": "IC50", "affinity_value_nm": 110.0, "is_primary_target": False},
            {"target_gene": "PDGFRA", "uniprot_id": "P16234", "protein_family": "KINASE", "affinity_type": "IC50", "affinity_value_nm": 140.0, "is_primary_target": False},
            {"target_gene": "DDR1", "uniprot_id": "Q08345", "protein_family": "KINASE", "affinity_type": "IC50", "affinity_value_nm": 95.0, "is_primary_target": False},
            {"target_gene": "EGFR", "uniprot_id": "P00533", "protein_family": "KINASE", "affinity_type": "IC50", "affinity_value_nm": 8500.0, "is_primary_target": False},
            {"target_gene": "SRC", "uniprot_id": "P12931", "protein_family": "KINASE", "affinity_type": "IC50", "affinity_value_nm": 12000.0, "is_primary_target": False},
            {"target_gene": "KCNH2", "uniprot_id": "Q12809", "protein_family": "ION_CHANNEL", "affinity_type": "IC50", "affinity_value_nm": 4200.0, "is_primary_target": False},
            {"target_gene": "HTR2B", "uniprot_id": "P41595", "protein_family": "GPCR", "affinity_type": "KI", "affinity_value_nm": 9800.0, "is_primary_target": False},
        ]

        # Calculate Gini Selectivity Index
        # Convert affinities to potency scores (pIC50 = -log10(IC50_M))
        potencies = []
        for a in affinities:
            nm = float(a.get("affinity_value_nm", 10000.0))
            p_val = max(4.0, min(10.0, -math.log10(max(1e-12, nm * 1e-9))))
            potencies.append(p_val)

        potencies.sort()
        n = len(potencies)
        sum_pot = sum(potencies)
        if n > 1 and sum_pot > 0:
            numerator = sum((i + 1) * potencies[i] for i in range(n))
            gini = round(((2.0 * numerator) / (n * sum_pot)) - ((n + 1.0) / n), 3)
            gini = max(0.05, min(0.95, gini * 2.5))  # Normalize scale
        else:
            gini = 0.50

        if gini >= 0.75:
            selectivity_tier = "HIGHLY_SELECTIVE"
        elif gini >= 0.45:
            selectivity_tier = "FAMILY_SELECTIVE"
        else:
            selectivity_tier = "PAN_INHIBITOR"

        # Antitarget safety checks
        alerts = []
        for a in affinities:
            gene = a.get("target_gene", "")
            pot = float(a.get("affinity_value_nm", 10000.0))
            if gene == "KCNH2" and pot < 1000.0:
                alerts.append({
                    "target_gene": "KCNH2 (hERG)",
                    "risk_type": "CARDIOTOXICITY_HERG",
                    "binding_potency_nm": pot,
                    "severity": "HIGH",
                    "recommendation": "Perform Patch-Clamp electrophysiology assay; modify basic amine or reduce lipophilicity (cLogP)."
                })
                a["is_off_target_liability"] = True
            elif gene == "HTR2B" and pot < 500.0:
                alerts.append({
                    "target_gene": "HTR2B (5-HT2B)",
                    "risk_type": "VALVULOPATHY_5HT2B",
                    "binding_potency_nm": pot,
                    "severity": "HIGH",
                    "recommendation": "High risk of drug-induced valvular heart disease. Redesign core scaffold to ablate 5-HT2B agonism."
                })
                a["is_off_target_liability"] = True
            elif gene == "ABCB11" and pot < 2000.0:
                alerts.append({
                    "target_gene": "ABCB11 (BSEP)",
                    "risk_type": "HEPATOTOXICITY_BSEP",
                    "binding_potency_nm": pot,
                    "severity": "MODERATE",
                    "recommendation": "Inhibition of bile salt export pump may induce cholestatic DILI. Monitor liver transaminases."
                })
                a["is_off_target_liability"] = True

        return {
            "compound_name": name,
            "smiles": smiles,
            "primary_target": primary_target,
            "gini_selectivity_index": gini,
            "selectivity_tier": selectivity_tier,
            "total_targets_screened": len(affinities),
            "off_target_liabilities_count": len(alerts),
            "affinities": affinities,
            "alerts": alerts,
            "profile_summary_json": {
                "polypharmacology_verdict": f"Compound demonstrates {selectivity_tier} profile (Gini Index = {gini}).",
                "potent_kinases": [a["target_gene"] for a in affinities if a.get("affinity_value_nm", 10000) < 200],
                "safety_margin": "CLEAN" if len(alerts) == 0 else "CAUTION_REQUIRED"
            }
        }
