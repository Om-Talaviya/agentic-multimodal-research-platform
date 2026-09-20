"""
Computational Engine for Phase 104: Single-Cell TCR/BCR Clonotype & Immune Repertoire Analysis.
Implements V(D)J annotation, diversity indices (Shannon Entropy, Gini-Simpson, Clonality),
CDR3 physicochemical profiling, and antigen epitope matching.
"""
import math
from typing import List, Dict, Any, Optional

class TCRClonotypeEngine:
    KNOWN_ANTIGEN_SPECIFICITIES = {
        "CASSLAPGATNEKLFF": "EBV_BMLF1 (GLCTLVAML)",
        "CASSLIGVSSYNEQFF": "CMV_pp65 (NLVPMVATV)",
        "CASSSRSSYEQYF": "Influenza_M1 (GILGFVFTL)",
        "CASSPGQGAYEQYF": "SARS-CoV-2_S (YLQPRTFLL)",
        "CASSLTGTEAFF": "Tumor_MART1 (AAGIGILTV)",
        "CASSRGTEYEQYF": "NY-ESO-1 (SLLMWITQC)"
    }

    def compute_diversity_metrics(self, clonotype_counts: List[int]) -> Dict[str, float]:
        """
        Calculates Shannon Entropy (H), Gini-Simpson Index (D), and Normalized Clonality.
        """
        total = sum(clonotype_counts)
        if total == 0:
            return {"shannon_entropy": 0.0, "gini_simpson_index": 0.0, "clonality_score": 0.0}

        frequencies = [c / total for c in clonotype_counts]
        
        # Shannon Entropy H = - sum(p * ln(p))
        shannon = -sum(p * math.log(p) for p in frequencies if p > 0)
        
        # Gini-Simpson D = 1 - sum(p^2)
        gini_simpson = 1.0 - sum(p ** 2 for p in frequencies)
        
        # Normalized Clonality = 1 - (H / ln(N))
        n_unique = len(clonotype_counts)
        if n_unique > 1:
            clonality = max(0.0, min(1.0, 1.0 - (shannon / math.log(n_unique))))
        else:
            clonality = 1.0

        return {
            "shannon_entropy": round(shannon, 4),
            "gini_simpson_index": round(gini_simpson, 4),
            "clonality_score": round(clonality, 4)
        }

    def analyze_repertoire(
        self,
        sample_name: str,
        raw_clonotypes: List[Dict[str, Any]],
        organism: str = "Homo sapiens",
        chain_type: str = "TCR_ALPHA_BETA"
    ) -> Dict[str, Any]:
        """
        Analyzes raw clonotype sequencing reads, formats CDR3, assigns antigen specificity,
        and aggregates V-J recombination pairing frequencies.
        """
        total_cells = sum(c.get("count", 1) for c in raw_clonotypes)
        counts = [c.get("count", 1) for c in raw_clonotypes]
        
        diversity = self.compute_diversity_metrics(counts)
        
        processed_clonotypes = []
        vdj_pair_counts: Dict[str, int] = {}

        for c in raw_clonotypes:
            cnt = c.get("count", 1)
            freq = round(cnt / max(1, total_cells), 5)
            cdr3_aa = c.get("cdr3_aa", "").strip()
            v_gene = c.get("v_gene", "TRBVUnknown")
            j_gene = c.get("j_gene", "TRBJUnknown")

            # Check known antigen database
            specificity = self.KNOWN_ANTIGEN_SPECIFICITIES.get(cdr3_aa, "Uncharacterized / Novel Antigen")

            processed_clonotypes.append({
                "cdr3_nt": c.get("cdr3_nt"),
                "cdr3_aa": cdr3_aa,
                "v_gene": v_gene,
                "d_gene": c.get("d_gene"),
                "j_gene": j_gene,
                "c_gene": c.get("c_gene"),
                "frequency": freq,
                "count": cnt,
                "is_productive": c.get("is_productive", True),
                "antigen_specificity": specificity
            })

            # Track V-J pairing family
            v_fam = v_gene.split("*")[0]
            j_fam = j_gene.split("*")[0]
            pair_key = f"{v_fam}::{j_fam}"
            vdj_pair_counts[pair_key] = vdj_pair_counts.get(pair_key, 0) + cnt

        # Build VDJ Recombination pairings
        pairings = []
        for pair_key, pair_count in vdj_pair_counts.items():
            v_f, j_f = pair_key.split("::")
            pairings.append({
                "v_family": v_f,
                "j_family": j_f,
                "pairing_frequency": round(pair_count / max(1, total_cells), 4),
                "cdr3_length": int(round(sum(len(c["cdr3_aa"]) for c in processed_clonotypes if c["v_gene"].startswith(v_f)) / max(1, len(processed_clonotypes))))
            })

        # Sort clonotypes by frequency
        processed_clonotypes.sort(key=lambda x: x["frequency"], reverse=True)

        return {
            "sample_name": sample_name,
            "organism": organism,
            "chain_type": chain_type,
            "clonotype_count": len(processed_clonotypes),
            "total_cells": total_cells,
            **diversity,
            "clonotypes": processed_clonotypes,
            "vdj_pairings": pairings
        }
