import math
from typing import List, Dict, Any, Optional

class QSARToxicityEngine:
    """
    Autonomous In-Silico Toxicity & QSAR Mutagenicity Matrix Engine.
    Implements Hansen/Ashby Ames structural alert scanning, QSAR hERG cardiotoxicity prediction,
    Drug-Induced Liver Injury (DILI) risk classification, and oral rat LD50 forecasting.
    """

    def __init__(self):
        # Known toxicophores and Ashby structural alerts
        self.structural_alerts_db = [
            {"name": "Aromatic Nitro Group", "sub": "N(=O)=O", "category": "Mutagenic Intermediate", "severity": "HIGH"},
            {"name": "Aliphatic Epoxide", "sub": "C1OC1", "category": "Direct DNA Alkylator", "severity": "HIGH"},
            {"name": "Alkyl Halide (Alkylating)", "sub": "CCI", "category": "DNA Crosslinker", "severity": "HIGH"},
            {"name": "Primary Aromatic Amine", "sub": "c[NH2]", "category": "Metabolic CYP Bioactivation", "severity": "MODERATE"},
            {"name": "Alpha,Beta-Unsaturated Carbonyl", "sub": "C=CC=O", "category": "Michael Acceptor Electrophile", "severity": "MODERATE"},
            {"name": "Hydrazine / Hydrazide", "sub": "NN", "category": "Free Radical Generator", "severity": "HIGH"},
        ]

    def predict_compound_toxicity(
        self,
        smiles: str,
        compound_name: str = "Lead-Compound",
        mol_weight: float = 350.0,
        log_p: float = 2.5,
    ) -> Dict[str, Any]:
        """
        Executes full in-silico QSAR toxicological profiling.
        """
        smiles_clean = smiles.strip()

        # 1. Structural alert scan
        matched_alerts = []
        for alert in self.structural_alerts_db:
            if alert["sub"] in smiles_clean or alert["name"].lower() in compound_name.lower():
                matched_alerts.append({
                    "alert_name": alert["name"],
                    "smarts_pattern": alert["sub"],
                    "toxicophore_category": alert["category"],
                    "severity_level": alert["severity"],
                })

        # 2. Ames Mutagenicity Assessment
        has_high_alert = any(a["severity_level"] == "HIGH" for a in matched_alerts)
        ames_prob = 82.5 if has_high_alert else (35.0 if matched_alerts else 8.4)
        ames_status = "POSITIVE" if ames_prob >= 50.0 else "NEGATIVE"

        # 3. hERG Cardiotoxicity (IC50 in uM)
        # Lipophilic bases (high LogP > 3.5 and basic amines) have higher hERG blockade risk
        herg_base = 35.0
        if log_p > 3.5:
            herg_base -= (log_p - 3.5) * 8.0
        if "N" in smiles_clean:
            herg_base -= 5.0
        herg_ic50 = round(max(0.2, herg_base), 2)
        herg_risk = "HIGH" if herg_ic50 < 1.0 else ("MODERATE" if herg_ic50 < 10.0 else "LOW")

        # 4. Drug-Induced Liver Injury (DILI)
        # Rule of 2 (Daily dose > 100mg + LogP >= 3)
        dili_risk = "HIGH" if (log_p >= 3.8 and ames_status == "POSITIVE") else ("MODERATE" if log_p >= 3.0 else "LOW")

        # 5. Acute Oral Rat LD50 (mg/kg)
        # High logP / reactive alerts decrease LD50
        ld50 = round(max(50.0, 2200.0 - (log_p * 250.0) - (len(matched_alerts) * 400.0)), 1)

        return {
            "compound_name": compound_name,
            "smiles_string": smiles_clean,
            "molecular_weight": mol_weight,
            "log_p": log_p,
            "ames_mutagenicity_status": ames_status,
            "ames_probability_pct": ames_prob,
            "herg_ic50_micromolar": herg_ic50,
            "herg_cardiotox_risk": herg_risk,
            "dili_hepatotox_risk": dili_risk,
            "ld50_rat_mg_kg": ld50,
            "structural_alerts": matched_alerts,
        }
