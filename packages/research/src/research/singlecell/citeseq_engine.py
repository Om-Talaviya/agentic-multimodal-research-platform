"""
Phase 128: Autonomous Single-Cell Spatial CITE-seq Multi-Modal Surface Protein & mRNA Co-Mapping Engine.
Performs DSB (Denoised and Scaled by Background) ADT normalization,
weighted Nearest Neighbor (wNN) multi-modal graph fusion between RNA and ADT,
and computes mRNA-to-protein discordance / post-transcriptional regulation metrics.
"""

import math
from typing import Dict, Any, List, Optional, Tuple


class CITEseqMultiModalEngine:
    """
    Autonomous CITE-seq (Cellular Indexing of Transcriptomes and Epitopes by Sequencing) Engine.
    Integrates single-cell surface antibody-derived tags (ADTs) and single-cell RNA-seq.
    """

    DEFAULT_IMMUNE_PANEL = {
        "CD3e": {"cell_type": "T Cells", "rna_gene": "CD3E"},
        "CD4": {"cell_type": "Helper T Cells", "rna_gene": "CD4"},
        "CD8a": {"cell_type": "Cytotoxic T Cells", "rna_gene": "CD8A"},
        "CD19": {"cell_type": "B Cells", "rna_gene": "CD19"},
        "CD14": {"cell_type": "Classical Monocytes", "rna_gene": "CD14"},
        "CD56": {"cell_type": "NK Cells", "rna_gene": "NCAM1"},
        "PD-1": {"cell_type": "Exhausted T Cells", "rna_gene": "PDCD1"},
        "CTLA-4": {"cell_type": "Regulatory T Cells", "rna_gene": "CTLA4"},
    }

    def compute_dsb_normalization(
        self,
        raw_adt_counts: List[float],
        empty_droplet_background_counts: List[float],
    ) -> List[float]:
        """
        DSB normalization:
        z = (ln(x + 1) - mean(ln(bg + 1))) / std(ln(bg + 1))
        """
        if not empty_droplet_background_counts:
            bg_log = [math.log(1.0 + 1.0)]
        else:
            bg_log = [math.log(max(0.0, bg) + 1.0) for bg in empty_droplet_background_counts]

        mean_bg = sum(bg_log) / float(len(bg_log))
        var_bg = sum((b - mean_bg) ** 2 for b in bg_log) / float(max(1, len(bg_log)))
        std_bg = math.sqrt(var_bg) if var_bg > 0 else 1.0

        dsb_scores = []
        for x in raw_adt_counts:
            log_x = math.log(max(0.0, x) + 1.0)
            z_score = (log_x - mean_bg) / max(0.01, std_bg)
            dsb_scores.append(round(z_score, 3))

        return dsb_scores

    def compute_wnn_fusion_weights(
        self,
        rna_variance: float = 0.45,
        protein_variance: float = 0.62,
    ) -> Dict[str, float]:
        """
        Weighted Nearest Neighbor (wNN) modality weight computation based on signal-to-noise.
        """
        tot = rna_variance + protein_variance
        w_protein = round(protein_variance / max(0.001, tot), 3)
        w_rna = round(1.0 - w_protein, 3)
        return {"weight_protein_adt": w_protein, "weight_rna": w_rna}

    def analyze_protein_rna_concordance(
        self,
        marker_name: str,
        adt_expression_dsb: float,
        rna_expression_tpm: float,
    ) -> Dict[str, Any]:
        """
        Evaluates post-transcriptional discordance between surface protein and transcript abundance.
        """
        marker_meta = self.DEFAULT_IMMUNE_PANEL.get(marker_name, {"cell_type": "Immune", "rna_gene": marker_name})
        
        # Spearman-like concordance approximation
        expected_protein = math.log(max(0.1, rna_expression_tpm) + 1.0)
        delta = abs(adt_expression_dsb - expected_protein)
        rho = max(-1.0, min(1.0, 1.0 - (delta / 4.0)))

        is_discordant = bool(adt_expression_dsb > 3.0 and rna_expression_tpm < 5.0)

        return {
            "marker_name": marker_name,
            "target_gene": marker_meta["rna_gene"],
            "cell_type_annotation": marker_meta["cell_type"],
            "adt_dsb_normalized": adt_expression_dsb,
            "rna_tpm": rna_expression_tpm,
            "concordance_rho": round(rho, 3),
            "is_post_transcriptionally_buffered": is_discordant,
        }

    def simulate_citeseq_pipeline(
        self,
        sample_name: str = "Melanoma_TIL_CITEseq",
        tissue_origin: str = "Melanoma Tumor Infiltrating Lymphocytes",
    ) -> Dict[str, Any]:
        """
        Simulates end-to-end CITE-seq multi-modal analysis pipeline.
        """
        bg_counts = [0.5, 1.2, 0.8, 2.1, 1.0, 0.9, 1.4, 0.6]
        raw_counts = [150.0, 420.0, 850.0, 120.0, 95.0, 12.0]
        dsb_norm = self.compute_dsb_normalization(raw_counts, bg_counts)

        wnn = self.compute_wnn_fusion_weights(0.40, 0.60)

        panel_markers = [
            ("CD8a", dsb_norm[2], 340.0),
            ("CD4", dsb_norm[1], 180.0),
            ("CD3e", dsb_norm[0], 210.0),
            ("PD-1", dsb_norm[3], 45.0),
            ("CTLA-4", dsb_norm[4], 32.0),
            ("CD19", dsb_norm[5], 2.0),
        ]

        concordance_results = []
        for m, adt, rna in panel_markers:
            res = self.analyze_protein_rna_concordance(m, adt, rna)
            concordance_results.append(res)

        tags = [
            {"tag_barcode": "TotalSeq-C-CD8a", "marker": "CD8a", "clone": "RPA-T8", "snr": 18.2},
            {"tag_barcode": "TotalSeq-C-CD4", "marker": "CD4", "clone": "SK3", "snr": 16.5},
            {"tag_barcode": "TotalSeq-C-CD3e", "marker": "CD3e", "clone": "UCHT1", "snr": 15.8},
            {"tag_barcode": "TotalSeq-C-PD1", "marker": "PD-1", "clone": "EH12.2H7", "snr": 14.1},
        ]

        return {
            "sample_name": sample_name,
            "tissue_origin": tissue_origin,
            "total_cells": 14500,
            "adt_panel_size": 54,
            "wnn_weights": wnn,
            "tags": tags,
            "concordance_profiles": concordance_results,
            "summary": {
                "mean_protein_snr": 16.15,
                "concordant_markers_count": sum(1 for c in concordance_results if c["concordance_rho"] > 0.5),
                "wnn_fusion_status": "Converged",
            },
        }
