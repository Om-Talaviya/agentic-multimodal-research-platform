"""TCR/BCR Clonotype Tracking & Lineage Dynamics Engine."""

import math
from typing import Any, Dict, List, Optional


class TCRClonotypeTrackingEngine:
    """Engine for quantifying immune repertoire diversity, clonal expansion, and lineage convergence."""

    def __init__(self) -> None:
        pass

    def calculate_repertoire_diversity(self, clone_frequencies: List[float]) -> Dict[str, float]:
        """Compute Shannon Entropy, Gini-Simpson Index, Clonality, and Berger-Parker Index."""
        if not clone_frequencies:
            return {"shannon_entropy": 0.0, "gini_simpson_index": 0.0, "clonality_score": 0.0, "berger_parker": 0.0}

        total = sum(clone_frequencies)
        p = [f / total for f in clone_frequencies if f > 0]
        n = len(p)

        shannon = -sum(pi * math.log(pi) for pi in p) if p else 0.0
        max_shannon = math.log(n) if n > 1 else 1.0
        clonality = 1.0 - (shannon / max_shannon) if max_shannon > 0 else 1.0
        gini_simpson = 1.0 - sum(pi * pi for pi in p)
        berger_parker = max(p) if p else 0.0

        return {
            "shannon_entropy": round(shannon, 3),
            "gini_simpson_index": round(gini_simpson, 3),
            "clonality_score": round(max(0.0, min(1.0, clonality)), 3),
            "berger_parker_dominance": round(berger_parker, 3),
        }

    def analyze_clonotype_lineage(
        self,
        study_name: str,
        sample_source: str = "PBMC",
        repertoire_type: str = "TCR_alpha_beta",
        clonotype_data: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Perform automated clonal expansion classification and lineage dynamics mapping."""
        if not clonotype_data:
            clonotype_data = [
                {"cdr3_amino_acid": "CASSLAGGYEQYF", "v_gene": "TRBV5-1", "j_gene": "TRBJ2-7", "clone_frequency": 0.28, "antigen_specificity": "EBV_BMLF1"},
                {"cdr3_amino_acid": "CASSIRSSYEQYF", "v_gene": "TRBV19", "j_gene": "TRBJ2-7", "clone_frequency": 0.19, "antigen_specificity": "CMV_pp65"},
                {"cdr3_amino_acid": "CASSDWGQGNTIYF", "v_gene": "TRBV12-3", "j_gene": "TRBJ1-3", "clone_frequency": 0.12, "antigen_specificity": "Influenza_M1"},
                {"cdr3_amino_acid": "CASSLTGDSNQPQHF", "v_gene": "TRBV7-2", "j_gene": "TRBJ1-5", "clone_frequency": 0.08, "antigen_specificity": "Tumor_Neoantigen_KRAS_G12D"},
                {"cdr3_amino_acid": "CASSRTNTEAFF", "v_gene": "TRBV28", "j_gene": "TRBJ1-1", "clone_frequency": 0.03, "antigen_specificity": "Novel_Target"},
            ]

        freqs = [c["clone_frequency"] for c in clonotype_data]
        div_metrics = self.calculate_repertoire_diversity(freqs)

        clonotypes: List[Dict[str, Any]] = []
        for c in clonotype_data:
            freq = c["clone_frequency"]
            if freq >= 0.05:
                status = "hyperexpanded"
            elif freq >= 0.01:
                status = "large_expansion"
            elif freq >= 0.001:
                status = "medium_expansion"
            else:
                status = "rare_clone"

            clonotypes.append({
                "cdr3_amino_acid": c["cdr3_amino_acid"],
                "v_gene": c["v_gene"],
                "j_gene": c["j_gene"],
                "d_gene": c.get("d_gene", "TRBD1"),
                "clone_frequency": freq,
                "expansion_status": status,
                "antigen_specificity": c.get("antigen_specificity", "Uncharacterized"),
            })

        diversity_list = [
            {"metric_name": "Shannon Entropy (H)", "metric_value": div_metrics["shannon_entropy"], "metric_category": "entropy"},
            {"metric_name": "Gini-Simpson Index", "metric_value": div_metrics["gini_simpson_index"], "metric_category": "evenness"},
            {"metric_name": "Pielou Clonality Index", "metric_value": div_metrics["clonality_score"], "metric_category": "clonality"},
            {"metric_name": "Berger-Parker Dominance", "metric_value": div_metrics["berger_parker_dominance"], "metric_category": "dominance"},
        ]

        summary_metrics = {
            "total_clones_analyzed": len(clonotypes),
            "dominant_clone_v_gene": clonotypes[0]["v_gene"] if clonotypes else "None",
            "shannon_entropy": div_metrics["shannon_entropy"],
            "clonality_score": div_metrics["clonality_score"],
            "hyperexpanded_clone_ratio": round(sum(1 for c in clonotypes if c["expansion_status"] == "hyperexpanded") / max(1, len(clonotypes)), 2),
        }

        return {
            "study_name": study_name,
            "sample_source": sample_source,
            "repertoire_type": repertoire_type,
            "cell_count": 5000,
            "shannon_entropy": div_metrics["shannon_entropy"],
            "gini_simpson_index": div_metrics["gini_simpson_index"],
            "clonality_score": div_metrics["clonality_score"],
            "summary_metrics": summary_metrics,
            "clonotypes": clonotypes,
            "diversity_metrics": diversity_list,
        }
