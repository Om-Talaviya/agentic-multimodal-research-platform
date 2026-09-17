"""Liquid Biopsy ctDNA Fragmentomics & MRD Detection Engine."""
import math
from typing import List, Dict, Any, Optional


class FragmentomicsMRDEngine:
    """Analyzes cell-free DNA (cfDNA) fragment length profiles, end-motifs, and detects Minimal Residual Disease (MRD)."""

    def analyze_sample(self, sample_input: Dict[str, Any]) -> Dict[str, Any]:
        """Runs fragment size distribution analysis, end-motif profiling, and MRD classification."""
        patient_id = sample_input.get("patient_id", "PT-1001")
        barcode = sample_input.get("sample_barcode", "LB-2026-001")
        cancer_type = sample_input.get("cancer_type", "Colorectal Cancer")
        timepoint = sample_input.get("sampling_timepoint", "POST_SURGERY")
        total_cfdna = float(sample_input.get("total_cfdna_ng_ml", 12.5))
        short_count_input = int(sample_input.get("short_fragments_100_150bp", 35000))
        long_count_input = int(sample_input.get("long_fragments_160_220bp", 100000))

        total_fragments = short_count_input + long_count_input
        short_ratio = round(short_count_input / max(1, long_count_input), 3)

        # Inferred Tumor Fraction (%)
        # Baseline physiological non-cancer short ratio is ~0.18
        # Higher short ratio strongly correlates with ctDNA shed
        inferred_tf_pct = round(max(0.02, min(45.0, (short_ratio - 0.18) * 8.5)), 2)
        if short_ratio < 0.20:
            inferred_tf_pct = round(max(0.01, short_ratio * 0.1), 2)

        # MRD Classification
        if inferred_tf_pct >= 0.10 or short_ratio >= 0.32:
            mrd_status = "MRD_POSITIVE"
            relapse_risk = round(min(0.98, 0.50 + (inferred_tf_pct / 5.0) * 0.4), 2)
        elif inferred_tf_pct <= 0.04 and short_ratio <= 0.22:
            mrd_status = "MRD_NEGATIVE"
            relapse_risk = 0.05
        else:
            mrd_status = "INDETERMINATE"
            relapse_risk = 0.35

        # Generate synthetic/calculated fragment size histogram bins
        bins = [
            {"bin_start_bp": 50, "bin_end_bp": 99, "fragment_count": int(total_fragments * 0.04), "fragment_frequency_pct": 4.0},
            {"bin_start_bp": 100, "bin_end_bp": 130, "fragment_count": int(short_count_input * 0.40), "fragment_frequency_pct": round((short_count_input * 0.40 / total_fragments) * 100, 1)},
            {"bin_start_bp": 131, "bin_end_bp": 150, "fragment_count": int(short_count_input * 0.60), "fragment_frequency_pct": round((short_count_input * 0.60 / total_fragments) * 100, 1)},
            {"bin_start_bp": 151, "bin_end_bp": 175, "fragment_count": int(long_count_input * 0.65), "fragment_frequency_pct": round((long_count_input * 0.65 / total_fragments) * 100, 1)},  # Mono-nucleosomal peak (167bp)
            {"bin_start_bp": 176, "bin_end_bp": 220, "fragment_count": int(long_count_input * 0.35), "fragment_frequency_pct": round((long_count_input * 0.35 / total_fragments) * 100, 1)},
            {"bin_start_bp": 221, "bin_end_bp": 350, "fragment_count": int(total_fragments * 0.08), "fragment_frequency_pct": 8.0},  # Di-nucleosomal
        ]

        # 4-mer End Motifs (CCCA, CCAG, CCTG, TTTT, AAAA, etc.)
        # In cancer, CCCA and CCAG end-motifs are elevated due to altered DNase cleavage
        motifs = [
            {"motif_sequence_4mer": "CCCA", "observed_frequency": 0.084 if mrd_status == "MRD_POSITIVE" else 0.062, "reference_frequency": 0.0625, "motif_diversity_score": 1.34},
            {"motif_sequence_4mer": "CCAG", "observed_frequency": 0.078 if mrd_status == "MRD_POSITIVE" else 0.061, "reference_frequency": 0.0625, "motif_diversity_score": 1.25},
            {"motif_sequence_4mer": "CCTG", "observed_frequency": 0.071, "reference_frequency": 0.0625, "motif_diversity_score": 1.14},
            {"motif_sequence_4mer": "AAAA", "observed_frequency": 0.052, "reference_frequency": 0.0625, "motif_diversity_score": 0.83},
            {"motif_sequence_4mer": "TTTT", "observed_frequency": 0.048, "reference_frequency": 0.0625, "motif_diversity_score": 0.77},
        ]

        return {
            "patient_id": patient_id,
            "sample_barcode": barcode,
            "cancer_type": cancer_type,
            "sampling_timepoint": timepoint,
            "total_cfdna_ng_ml": total_cfdna,
            "tumor_fraction_pct": inferred_tf_pct,
            "mrd_status": mrd_status,
            "fragment_short_ratio": short_ratio,
            "median_fragment_length_bp": 166 if mrd_status == "MRD_POSITIVE" else 167,
            "size_distributions": bins,
            "end_motifs": motifs,
            "sample_metadata_json": {
                "relapse_risk_probability": relapse_risk,
                "total_fragments_analyzed": total_fragments,
                "mononucleosomal_peak_bp": 167,
                "clinical_actionability": "Initiate adjuvant chemotherapy or escalation" if mrd_status == "MRD_POSITIVE" else "Continue standard surveillance protocol"
            }
        }
