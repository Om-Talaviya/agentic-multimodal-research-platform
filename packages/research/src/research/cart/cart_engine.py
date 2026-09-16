import math
from typing import Dict, Any, List, Optional

class CARTEngine:
    """
    Autonomous Cell Therapy CAR-T Engineering & Cytokine Release Syndrome (CRS) Toxicity Predictor.
    Simulates in silico construct assembly, in vitro tumor lysis kinetics, memory Tcm persistence,
    and clinical ASTCT CRS grade / ICANS neurotoxicity risk profiling.
    """

    ANTIGEN_TARGET_MAP = {
        "CD19": {"tumor_types": ["B-ALL", "DLBCL", "MCL"], "default_scfv": "FMC63", "expression_density": 25000},
        "BCMA": {"tumor_types": ["Multiple Myeloma"], "default_scfv": "11D5-3", "expression_density": 18000},
        "HER2": {"tumor_types": ["Breast Cancer", "Gastric Cancer", "Glioblastoma"], "default_scfv": "4D5", "expression_density": 45000},
        "EGFRvIII": {"tumor_types": ["Glioblastoma"], "default_scfv": "139", "expression_density": 12000},
        "PSMA": {"tumor_types": ["Prostate Cancer"], "default_scfv": "J591", "expression_density": 30000},
    }

    COSTIM_MAP = {
        "4-1BB": {"persistence_boost": 0.88, "exhaustion_factor": 0.22, "cytokine_multiplier": 0.75, "phenotype": "Tcm-dominant"},
        "CD28": {"persistence_boost": 0.55, "exhaustion_factor": 0.58, "cytokine_multiplier": 1.45, "phenotype": "Tem-dominant / Rapid Killer"},
        "CD28+4-1BB": {"persistence_boost": 0.92, "exhaustion_factor": 0.35, "cytokine_multiplier": 1.30, "phenotype": "3rd Gen Dual-Costim"},
    }

    def design_car_construct(
        self,
        construct_name: str,
        target_antigen: str,
        costimulatory_domain: str = "4-1BB",
        scfv_clone: Optional[str] = None,
        hinge_transmembrane: str = "CD8a",
        vector_type: str = "Lentiviral"
    ) -> Dict[str, Any]:
        antigen_info = self.ANTIGEN_TARGET_MAP.get(target_antigen.upper(), {
            "tumor_types": ["Solid / Liquid Malignancy"],
            "default_scfv": "CustomClone-01",
            "expression_density": 20000
        })
        selected_scfv = scfv_clone or antigen_info["default_scfv"]
        costim_info = self.COSTIM_MAP.get(costimulatory_domain, self.COSTIM_MAP["4-1BB"])

        leader_seq = "MALPVTALLLPLALLLHAARP"
        scfv_placeholder = f"EVQLQQSG...({selected_scfv})...DIQMTQSP"
        hinge_seq = "TTTPAPRPPTPAPTIASQPLSLRPEACRPAAGGAVHTRGLDFACD" if hinge_transmembrane == "CD8a" else "ESKYGPPCPPCPAPEFEGG"
        tm_seq = "IYIWAPLAGTCGVLLLSLVITLYC"
        costim_seq = "KRGRKKLLYIFKQPFMRPVQTTQEEDGCSCRFPEEEEGGCEL" if "4-1BB" in costimulatory_domain else "RSKRSRLLHSDYMNMTPRRPGPTRKHYQPYAPPRDFAAYRS"
        cd3z_seq = "RVKFSRSADAPAYQQGQNQLYNELNLGRREEYDVLDKRRGRDPEMGGKPRRKNPQEGLYNELQKDKMAEAYSEIGMKGERRRGKGHDGLYQGLSTATKDTYDALHMQALPPR"

        full_aa = f"{leader_seq}_{scfv_placeholder}_{hinge_seq}_{tm_seq}_{costim_seq}_{cd3z_seq}"

        return {
            "construct_name": construct_name,
            "target_antigen": target_antigen.upper(),
            "scfv_binder_clone": selected_scfv,
            "costimulatory_domain": costimulatory_domain,
            "hinge_transmembrane": hinge_transmembrane,
            "signaling_domain": "CD3zeta",
            "vector_type": vector_type,
            "full_aa_sequence": full_aa,
            "target_malignancies": antigen_info["tumor_types"],
            "phenotype_prediction": costim_info["phenotype"],
        }

    def simulate_cytotoxicity(
        self,
        target_antigen: str,
        costimulatory_domain: str,
        target_cell_line: str = "Target-Tumor-Line",
        et_ratio: float = 5.0,
    ) -> Dict[str, Any]:
        costim_info = self.COSTIM_MAP.get(costimulatory_domain, self.COSTIM_MAP["4-1BB"])

        base_lysis = 45.0 + 35.0 * (1.0 - math.exp(-0.35 * et_ratio))
        if costimulatory_domain == "CD28":
            base_lysis = min(98.5, base_lysis * 1.15)
        elif costimulatory_domain == "CD28+4-1BB":
            base_lysis = min(99.2, base_lysis * 1.20)
        else:
            base_lysis = min(95.0, base_lysis)

        persistence = round(costim_info["persistence_boost"] * (0.95 - (et_ratio * 0.01)), 3)
        persistence = max(0.20, min(0.99, persistence))

        pd1_exp = round(costim_info["exhaustion_factor"] * 48.0 + (et_ratio * 1.5), 2)
        tim3_exp = round(costim_info["exhaustion_factor"] * 36.0 + (et_ratio * 1.2), 2)
        lag3_exp = round(costim_info["exhaustion_factor"] * 30.0 + (et_ratio * 1.0), 2)

        grade = "POTENT" if base_lysis >= 80.0 else ("HIGH" if base_lysis >= 60.0 else "MODERATE")

        return {
            "target_cell_line": target_cell_line,
            "effector_to_target_ratio": et_ratio,
            "specific_lysis_pct": round(base_lysis, 2),
            "t_cell_persistence_score": persistence,
            "exhaustion_pd1_expression_pct": pd1_exp,
            "exhaustion_tim3_expression_pct": tim3_exp,
            "exhaustion_lag3_expression_pct": lag3_exp,
            "cytotoxicity_grade": grade,
        }

    def predict_crs_toxicity(
        self,
        target_antigen: str,
        costimulatory_domain: str,
        tumor_burden_index: float = 1.0, # 0.5 (low) to 3.0 (high)
    ) -> Dict[str, Any]:
        costim_info = self.COSTIM_MAP.get(costimulatory_domain, self.COSTIM_MAP["4-1BB"])
        cytokine_mult = costim_info["cytokine_multiplier"] * tumor_burden_index

        peak_il6 = round(150.0 * cytokine_mult * (1.2 if target_antigen.upper() in ["CD19", "BCMA"] else 0.85), 2)
        peak_ifng = round(220.0 * cytokine_mult, 2)
        peak_tnfa = round(95.0 * cytokine_mult, 2)
        peak_il1b = round(45.0 * cytokine_mult, 2)

        if peak_il6 < 120.0:
            astct_grade = "Grade 1"
            icans_risk = 8.5
            dex = False
        elif peak_il6 < 280.0:
            astct_grade = "Grade 2"
            icans_risk = 22.0
            dex = False
        elif peak_il6 < 600.0:
            astct_grade = "Grade 3"
            icans_risk = 48.5
            dex = True
        else:
            astct_grade = "Grade 4"
            icans_risk = 78.0
            dex = True

        safety_summary = (
            f"Simulated cytokine burst profile shows peak IL-6 of {peak_il6} pg/mL resulting in predicted {astct_grade} CRS. "
            f"ICANS neurotoxicity risk is {icans_risk}%. Tocilizumab (anti-IL-6R) administration indicated upon fever onset."
        )

        return {
            "peak_il6_pg_ml": peak_il6,
            "peak_ifng_pg_ml": peak_ifng,
            "peak_tnfa_pg_ml": peak_tnfa,
            "peak_il1b_pg_ml": peak_il1b,
            "astct_crs_grade_predicted": astct_grade,
            "icans_neurotoxicity_risk_pct": icans_risk,
            "tocilizumab_responsive": True,
            "dexamethasone_recommended": dex,
            "safety_summary": safety_summary,
        }
